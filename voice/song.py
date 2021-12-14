import discord
import typing
import youtube_dl
import asyncio
from async_timeout import timeout
from functools import partial
from discord.ext import commands
from database import Database as database
from voice.player import Player
from alert import Alert

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'yesplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5" ## song will end if no this line
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):

	def __init__(self, source, *, data, requester):
		super().__init__(source)
		self.requester = requester
		self.info = YoutubeInfo(data, requester)

	def __getitem__(self, item: str):
		return self.__getattribute__(item)

	@classmethod
	async def create_source(cls, message:discord.Message, *, loop):
		loop = loop or asyncio.get_event_loop()

		to_run = partial(ytdl.extract_info, url = message.content, download = False)
		data = await loop.run_in_executor(None, to_run)

		if 'entries' in data:
			source = [YoutubeInfo(_, message.author) for _ in data['entries']]
		else:
			source = [(YoutubeInfo(data, message.author))]

		return source

	@classmethod
	async def regather_stream(cls, source, *, loop):
		loop = loop or asyncio.get_event_loop()
		requester = source.author

		to_run = partial(ytdl.extract_info, url=source.url, download=False)
		
		data = await loop.run_in_executor(None, to_run)

		return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data, requester=requester)

class YoutubeInfo:
	def __init__(self, data, author:discord.abc.User):
		self.url = data['webpage_url']
		self.title  = data['title']
		self.channel = data['channel']
		self.author = author
		self.thumbnail = data['thumbnail']
		t = data['duration']
		self.duration = f"{int(t/3600)}h:{int(t%3600/60)}m:{int(t%3600%60)}s"


class Source(discord.PCMVolumeTransformer):

	def __init__(self, source, message):
		super().__init__(source)
		self.message = message

	def __getitem__(self, item: str):
		return self.__getattribute__(item)

	@classmethod
	async def pull(cls, name:str, message, *, loop):
		loop = loop or asyncio.get_event_loop()
		to_run = partial(Data.set, name = name, message = message)
		data = await loop.run_in_executor(None, to_run)
		return data

	@classmethod
	async def regather_stream(cls, data, *, loop):
		loop = loop or asyncio.get_event_loop()
		to_run = partial(Data.get, name = data.name, message = data.message)
		data = await loop.run_in_executor(None, to_run)

		return cls(discord.FFmpegPCMAudio(data.path), data.message)
	
class Data:

	def __init__(self, name, message):
		self.name = name
		self.message = message
	
	@classmethod
	def set(cls, name, message):
		return cls(name, message)

	@classmethod
	def get(cls, name, message):
		cls = cls(name, message)
		cls.path = f"voice/source/{name}.mp3"
		return cls

class MusicPlayer:

	def __init__(self, ctx):
		self.alert = Alert.music(ctx)
		self.client = ctx.bot
		self._guild = ctx.guild
		self.channel = ctx.channel

		self.queue = asyncio.Queue()
		self.next_event = asyncio.Event()
		self.player = None
		self.queue_list = None
		self.loop = False
		self.loop_all = False
		self.current = None
		
		ctx.bot.loop.create_task(self.player_loop())

	async def player_loop(self):

		await self.client.wait_until_ready()

		while not self.client.is_closed():
			self.next_event.clear()

			try:
				# Wait for the next song. If we timeout cancel the player and disconnect...
				async with timeout(300):
					if self.loop:
						if self.current is None:
							qsource = await self.queue.get()
						else:
							qsource = self.current
					else:
						self.current = None
						qsource = await self.queue.get()

			except asyncio.TimeoutError:
				return await self.destroy()
			
			except :
				return await self.destroy()

			#if can play source
			if not isinstance(qsource, YTDLSource) and not self.player is None:
				try:
					source = await YTDLSource.regather_stream(qsource, loop=self.client.loop)
				except:
					await self.alert.player.error()
					continue
			
			if not isinstance(qsource, Source) and self.player is None:
				try:
					source = await Source.regather_stream(qsource, loop=self.client.loop)
				except:
					await self.alert.player.error()
					continue
					
			source.volume = 1

			if self._guild.voice_client is None:
				await self.player.clear()
				await self.queue_list.clear()
				return

			if self.loop and not self.player is None: loop = 'one'
			elif self.loop_all and not self.player is None: loop = 'all'
			else: loop = None

			try:
				self._guild.voice_client.play(source, after=lambda _: self.client.loop.call_soon_threadsafe(self.next_event.set))
			except:
				await self.alert.player.error()

			if not self.loop and not self.player is None:
				await self.player.update(source.info, loop = loop)
				await self.queue_list.pop()

			await self.next_event.wait()

			if self.loop and not self.player is None:
				self.current = qsource

			if self.loop_all and not self.player is None:
				await self.queue.put(qsource)
				await self.queue_list.update(qsource)
			
			if self.player is None:
				await qsource.message.edit(delete_after = 3)
			# Make sure the FFmpeg process is cleaned up.
			source.cleanup()
			if not self.loop and not self.player is None:
				await self.player.clear()


	async def destroy(self):
		try:
			await self._guild.voice_client.disconnect()
		except:pass

		if self.player is not None:
			await self.player.clear()
			await self.queue_list.clear()
		return await self.alert.player.clear()

############
class SongAPI:
	def __init__(self, client:typing.Union[discord.Client, commands.Bot]):
		self.players = {}
		self.client = client

	def get_player(self, ctx):
		try:
			now_player = self.players[ctx.channel.guild.id]
		except:
			now_player = MusicPlayer(ctx)
			self.players[ctx.channel.guild.id] = now_player
		return now_player
	
	def update(self, guild:discord.Guild, player:MusicPlayer):
		try:
			self.players[guild.id]
		except:return
		else:
			self.players[guild.id] = player
	
	async def cleanup(self):
		for guild in self.client.guilds:
			if self.find(guild) is not None:
				await Player.cleanup(guild)
			
	def find(self, guild:discord.Guild):
		channel_id = database.pull('channel', guild)
		if channel_id is None: return None

		channel = guild.get_channel(channel_id)
		return channel

	async def setup(self, guild:discord.Guild):
		channel = await Player.setup(guild, self.client.user.name)
		return channel
	
	async def unsetup(self, guild:discord.Guild):
		await Player.unsetup(guild)

	async def put(self, message:discord.Message):
		ctx = await self.client.get_context(message)
		guild = message.channel.guild
		
			
		_player = self.get_player(ctx)
		p = await Player.pull(guild)

		if _player.player is None:
			_player.queue_list = p.queue
			_player.player = p.player
			self.update(guild, _player)
			_player = self.get_player(ctx)

		source = await YTDLSource.create_source(message, loop=self.client.loop)

		for _ in source:
			await _player.queue.put(_)
			await _player.queue_list.update(_)

	async def put_source(self, ctx, name, message):
		guild = ctx.channel.guild

		_player = self.get_player(ctx)

		if _player.player is not None:
			_player.player = None
			_player.queue_list = None
			self.update(guild, _player)
			_player = self.get_player(ctx)
		
		source = await Source.pull(name, message, loop=self.client.loop)
		await _player.queue.put(source)
	
	def check(self, ctx):
		if ctx.author.voice is not None and ctx.voice_client is not None:
			if ctx.author.voice.channel == ctx.voice_client.channel:return True
		
		return False
	
	async def pause(self, ctx):
		vc = ctx.voice_client
		alert = Alert.music(ctx)

		if self.check(ctx):
			vc.pause()
			return await alert.player.pause()
		
		return await alert.user.mustbe_together(ctx.bot.user)
	
	async def play(self, ctx):
		vc = ctx.voice_client
		alert = Alert.music(ctx)

		if self.check(ctx):
			vc.resume()
			return await alert.player.play()
		
		return await alert.user.mustbe_together(ctx.bot.user)
		
	async def skip(self, ctx):
		vc = ctx.voice_client
		alert = Alert.music(ctx)

		if self.check(ctx):
			if vc.is_paused():
				pass
			elif not vc.is_playing():
				return
			
			vc.stop()
			return await alert.player.skip()
		
		return await alert.user.mustbe_together(ctx.bot.user)
	
	async def leave(self, ctx):
		vc = ctx.voice_client
		alert = Alert.music(ctx)

		if self.check(ctx):
			del self.players[ctx.channel.guild.id]
			await vc.disconnect()
			return await alert.player.disconnect()

		return await alert.user.mustbe_together(ctx.bot.user)
	
	async def next_q(self, ctx):
		_player = self.get_player(ctx)
		await _player.queue_list.next()
	
	async def prev_q(self, ctx):
		_player = self.get_player(ctx)
		await _player.queue_list.previous()

	async def loop(self, ctx, option:str):
		_player = self.get_player(ctx)
		alert = Alert.music(ctx)

		if not self.check(ctx):
			return await alert.user.mustbe_together(ctx.bot.user)

		if option == 'one':
			if _player.loop == True:
				_player.loop = False
				await _player.player.update_loop('off')
				await alert.player.loop_off()
			else:
				_player.loop = True
				_player.loop_all = False
				await _player.player.update_loop('one')
				await alert.player.loop_on()
			return
		
		if option == 'all':
			if _player.loop_all == True:
				_player.loop_all = False
				await _player.player.update_loop('off')
				await alert.player.loop_all_off()
			else:
				_player.loop = False
				_player.loop_all = True
				await _player.player.update_loop('all')
				await alert.player.loop_all_on()
			return
		