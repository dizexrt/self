import discord
import typing
import youtube_dl
import asyncio
from async_timeout import timeout
from functools import partial
from discord.ext import commands
from database import Database as database
from component.music import ComponentQueue, ComponentPlayer
from voice.action import Voice

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

class Player:
	def __init__(self, message:discord.Message):
		self.message = message
		self.guild = message.channel.guild
		self.source = None
	
	@classmethod
	async def pull(cls, guild:discord.Guild):
		channel = guild.get_channel(database.pull('channel', guild))
		_id = database.pull('player', guild)
		message =  await channel.fetch_message(_id)
		return cls(message)
	
	@classmethod
	def default(cls, guild:discord.Guild):
		embed = discord.Embed(
			title = "Music player",
			description = "```\nไม่มีเพลงที่กำลังเล่นอยู่ในขณะนี้\n```"
		)
		embed.set_thumbnail(url = guild.icon_url)
		embed.set_footer(text = f"server : {guild.name}")
		return embed

	async def update(self, source:YoutubeInfo, loop:str):
		self.source = source
		embed = discord.Embed(title = "Now Playing")
		embed.add_field(name = "Title", value = f"```\n{source.title}\n```", inline = False)
		embed.add_field(name = "Channel", value = f"```\n{source.channel}\n```", inline = False)
		embed.add_field(name = "Duration", value = f"```\n{source.duration}\n```", inline = False)
		embed.set_footer(text = f"requested by | {source.author}")
		embed.set_image(url = source.thumbnail)
		await self.message.edit(embed = embed, components = ComponentPlayer.update(loop, source.url))
	
	async def update_loop(self, loop:str):
		await self.message.edit(components = ComponentPlayer.update(loop, self.source.url))
	
	async def clear(self):
		await self.message.edit(embed = self.default(self.guild), components = ComponentPlayer.turn_off())

class Queue:
	def __init__(self, message:discord.Message):
		self.message = message
		self.guild = message.channel.guild
		self._q = []
		self._page = []
		self._current = 0
	
	@classmethod
	def default(cls, guild:discord.Guild):
		embed = discord.Embed()
		embed.title = "Page : 1"
		embed.description = "```\nไม่มีเพลงอยู่ในคิวในขณะนี้\n```"
		return embed
	
	@classmethod
	async def pull(cls, guild:discord.Guild):
		channel = guild.get_channel(database.pull('channel', guild))
		_id = database.pull('queue', guild)
		message = await channel.fetch_message(_id)
		return cls(message)

	async def _update(self):
		await self.message.edit(embed = self._page[self._current], components = ComponentQueue.page(self._current+1, len(self._page)))

	async def update(self, source:YoutubeInfo):
		self._q.append(source)
		await self._update_page()

	async def pop(self):
		if len(self._q) > 0:
			self._q.pop(0)
			await self._update_page()

	async def clear(self):
		self._q = []
		self._current = 0
		await self.message.edit(embed = self.default(self.guild), components = ComponentQueue.turn_off())

	async def _update_page(self):
		page = int(len(self._q)/10)
		left = int(len(self._q)%10)
		self._page = []

		if len(self._q) == 0:
			self._page = [self.default(self.guild)]
			return await self._update()

		if page > 0:
			for p in range(page):
				embed = discord.Embed()
				embed.title = f"Page : {p+1}"

				q = "```\n"
				for i in range(10):
					music = self._q[p*10+i]
					q += f"{i+1}. {music.title}\n"
				q += "```"

				embed.description = q

				self._page.append(embed)
		
		embed = discord.Embed()
		embed.title = f"Page : {page+1}"

		q = "```\n"
		for i in range(left):
			music = self._q[page*10+i]
			q += f"{i+1}. {music.title}\n"
		q += "```"

		embed.description = q
		self._page.append(embed)

		await self._update()
	
	async def next_page(self):
		self._current +=1
		if self._current >= len(self._page):
			self._current = 0

		await self._update()

	async def previous_page(self):
		self._current -=1
		if self._current < 0:
			self._current = len(self._page)-1

		await self._update()

class MusicPlayer:

	def __init__(self, ctx):
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

			#if can play source
			if not isinstance(qsource, YTDLSource):
				try:
					source = await YTDLSource.regather_stream(qsource, loop=self.client.loop)
				except:
					await self._channel.send("ล้มเหลวในการเล่นเพลง", delete_after = 3)
					continue
					
			source.volume = 5

			if self._guild.voice_client is None:
				await self.player.clear()
				await self.queue_list.clear()
				return

			if self.loop: loop = 'one'
			elif self.loop_all: loop = 'all'
			else: loop = None

			try:
				self._guild.voice_client.play(source, after=lambda _: self.client.loop.call_soon_threadsafe(self.next_event.set))
			except:
				await self.channel.send("ล้มเหลวในการดาวโหลดเพลง")

			if not self.loop:
				await self.player.update(source.info, loop = loop)
				await self.queue_list.pop()

			await self.next_event.wait()

			if self.loop:
				self.current = qsource

			if self.loop_all:
				await self.queue.put(qsource)
				await self.queue_list.update(qsource)
				
			# Make sure the FFmpeg process is cleaned up.
			source.cleanup()
			if not self.loop:
				await self.player.clear()

	async def destroy(self):
		await self._guild.voice_client.disconnect()
		await self.player.clear()
		await self.queue_list.clear()
		return

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
			if self.search(guild) is not None:
				queue = await Queue.pull(guild)
				player = await Player.pull(guild)
				await queue.clear()
				await player.clear()
			
	def search(self, guild:discord.Guild):
		channel_id = database.pull('channel', guild)
		if channel_id is None: return None

		channel = guild.get_channel(channel_id)
		return channel

	async def setup(self, guild:discord.Guild):
		channel = await guild.create_text_channel(name = f"ห้องของ {self.client.user.name}")
		queue = await channel.send(embed = Queue.default(guild), components = ComponentQueue.turn_off())
		player = await channel.send(embed = Player.default(guild),
		components = ComponentPlayer.turn_off())

		database.clear(guild)
		database.add('channel', guild, channel.id)
		database.add('player', guild, player.id)
		database.add('queue', guild, queue.id)
		return channel
	
	async def delete_setup(self, guild:discord.Guild):
		channel = guild.get_channel(database.pull('channel', guild))
		await channel.delete()
		database.clear(guild)

	async def put(self, message:discord.Message, first:bool):
		ctx = await self.client.get_context(message)
		guild = message.channel.guild
		if first:
			try:
				del self.players[guild.id]
			except:
				pass
			
			_player = self.get_player(ctx)
			player = await Player.pull(guild)
			queue = await Queue.pull(guild)
			_player.player = player
			_player.queue_list = queue
			self.update(guild, _player)
		
		_player = self.get_player(ctx)
		source = await YTDLSource.create_source(message, loop=self.client.loop)

		for _ in source:
			await _player.queue.put(_)
			await _player.queue_list.update(_)
	
	async def pause(self, ctx):
		vc = ctx.voice_client
		check = Voice.check(ctx.author, vc)
		if check:
			vc.pause()
			return
		
		return await ctx.send("คุณต้องเข้าช่องเสียงเดียวกับสายไหมก่อนนะ😊")
	
	async def play(self, ctx):
		vc = ctx.voice_client
		check = Voice.check(ctx.author, vc)
		if check:
			vc.resume()
			return
		
		return await ctx.send("คุณต้องเข้าช่องเสียงเดียวกับสายไหมก่อนนะ😊")
		
	async def skip(self, ctx):
		vc = ctx.voice_client
		check = Voice.check(ctx.author, vc)
		if check:
			if vc.is_paused():
				pass
			elif not vc.is_playing():
				return
			
			vc.stop()
			return
		
		return await ctx.send("คุณต้องเข้าช่องเสียงเดียวกับสายไหมก่อนนะ😊")
	
	async def leave(self, ctx):
		vc = ctx.voice_client
		check = Voice.check(ctx.author, vc)
		if check:
			del self.players[ctx.channel.guild.id]
			return await vc.disconnect()

		return await ctx.send("คุณต้องเข้าช่องเสียงเดียวกับสายไหมก่อนนะ😊")
	
	async def queue_next(self, ctx):
		_player = self.get_player(ctx)
		await _player.queue_list.next_page()
	
	async def queue_previous(self, ctx):
		_player = self.get_player(ctx)
		await _player.queue_list.previous_page()

	async def loop(self, ctx, option:str):
		_player = self.get_player(ctx)

		if option == 'one':
			if _player.loop == True:
				_player.loop = False
				await _player.player.update_loop('off')
				await ctx.channel.send("ปิดการเล่นซ้ำเพลงล่าสุดแล้ว")
			else:
				_player.loop = True
				_player.loop_all = False
				await _player.player.update_loop('one')
				await ctx.channel.send("เปิดการเล่นซ้ำเพลงล่าสุดแล้ว")
			return
		
		if option == 'all':
			if _player.loop_all == True:
				_player.loop_all = False
				await _player.player.update_loop('off')
				await ctx.channel.send("ปิดการเล่นซ้ำเพลงทั้งหมดแล้ว")
			else:
				_player.loop = False
				_player.loop_all = True
				await _player.player.update_loop('all')
				await ctx.channel.send("เปิดการเล่นซ้ำเพลงทั้งหมดแล้ว")
			return
		
		