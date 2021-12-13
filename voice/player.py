
import discord
from database import Database as database
from component import button, ButtonGroup


song_image = 'https://cdn.discordapp.com/attachments/918611726566580244/919561353100951632/Queue_1.png'

class ComponentQueue:
	
	@staticmethod
	def page(page:int, max:int):
		active = True
		
		if max == 1: active = False

		components = [
			ButtonGroup(
				button(active, label = '', id = 'previous', style = 'blue', emoji = '⏮'),
				button(False, label = f'page : {page}/{max}', id = 'page', style = 'gray'),
				button(active, label = '', id = 'next', style = 'blue', emoji = '⏭')
			)
		]
		return components
	
	@staticmethod
	def turn_off():
		components = [
			ButtonGroup(
				button(False, label = '', id = 'previous', style = 'blue', emoji = '⏮'),
				button(False, label = f'page : 1/1', id = 'page', style = 'gray'),
				button(False, label = '', id = 'next', style = 'blue', emoji = '⏭')
			)
		]
		return components
	
class ComponentPlayer:

	@staticmethod
	def turn_off():
		components = [
			ButtonGroup(
				button(False, label = '', id = 'play', style = 'green', emoji = '▶'),
				button(False, label = '', id = 'pause', style = 'green', emoji = '⏸'),
				button(False, label = '', id = 'skip', style = 'red', emoji = '⏭'),
				button(False, label = '', id = 'leave', style = 'red', emoji = '⏹'),
				button(True, label = 'link', id = None, style = 'link', url = 'https://www.youtube.com/')
			),
			ButtonGroup(
				button(False, label = '', id = 'loop', style = 'gray', emoji = '🔂'),
				button(False, label = '', id = 'loop_all', style = 'gray', emoji = '🔁')
			)
		]
		return components
	
	@staticmethod
	def update(loop:str, url:str):
		
		active, inactive = 'green', 'gray'

		if loop == 'one':
			one, all = active, inactive
		
		elif loop == 'all':
			one, all = inactive, active
		
		else:
			one, all = inactive, inactive

		components = [
			ButtonGroup(
				button(True, label = '', id = 'play', style = 'green', emoji = '▶'),
				button(True, label = '', id = 'pause', style = 'green', emoji = '⏸'),
				button(True, label = '', id = 'skip', style = 'red', emoji = '⏭'),
				button(True, label = '', id = 'leave', style = 'red', emoji = '⏹'),
				button(True, label = 'link', id = None, style = 'link', url = url)
			),
			ButtonGroup(
				button(True, label = '', id = 'loop', style = one, emoji = '🔂'),
				button(True, label = '', id = 'loop_all', style = all, emoji = '🔁')
			)
		]

		return components


class MusicPlayer:
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
	
	@staticmethod
	def default(guild:discord.Guild):
		embed = discord.Embed(title = "▶ Music player")
		title = 'No current song'
		song = "```\nสามารถค้นหาเพลงจากชื่อ หรือวางลิงก์จาก youtube ได้เลย\n```"
		embed.add_field(name = title, value = song, inline = False)
		embed.set_image(url = song_image)
		embed.set_footer(text = f"server : {guild.name}")
		return embed

	async def update(self, source, loop:str):
		self.source = source
		embed = discord.Embed(title = "▶ Now Playing")
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

class MusicQueue:
	def __init__(self, message:discord.Message):
		self.message = message
		self.guild = message.channel.guild
		self._q = []
		self._page = []
		self._current = 0
	
	@staticmethod
	def default(guild:discord.Guild):
		embed = discord.Embed(title = '📋 Music Queue')
		page = "page : 1"
		queue = "```\nยังไม่มีเพลงอยู่ในคิวในขณะนี้\n```"
		embed.add_field(name = page, value = queue, inline = False)
		embed.set_image(url = song_image)
		return embed
	
	@classmethod
	async def pull(cls, guild:discord.Guild):
		channel = guild.get_channel(database.pull('channel', guild))
		_id = database.pull('queue', guild)
		message = await channel.fetch_message(_id)
		return cls(message)

	async def _update(self):
		await self.message.edit(embed = self._page[self._current], components = ComponentQueue.page(self._current+1, len(self._page)))

	async def update(self, source):
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
		pages = int(len(self._q)/10)
		left = int(len(self._q)%10)
		self._page = []

		if len(self._q) == 0:
			self._page = [self.default(self.guild)]
			return await self._update()

		if pages > 0:
			for p in range(pages):
				embed = discord.Embed(title = "📋 Music Queue")
				page = f"page : {p+1}"

				queue = "```\n"
				for i in range(10):
					music = self._q[p*10+i]
					queue += f"{i+1}. {music.title}\n"
				queue += "```"

				embed.add_field(name = page, value = queue, inline = False)
				embed.set_image(url = song_image)

				self._page.append(embed)
		
		embed = discord.Embed(title = "📋 Music Queue")
		page = f"page : {pages+1}"

		queue = "```\n"
		for i in range(left):
			music = self._q[pages*10+i]
			queue += f"{i+1}. {music.title}\n"
		queue += "```"

		embed.add_field(name = page, value = queue, inline = False)
		embed.set_image(url = song_image)
		self._page.append(embed)

		await self._update()
	
	async def next(self):
		self._current +=1
		if self._current >= len(self._page):
			self._current = 0

		await self._update()

	async def previous(self):
		self._current -=1
		if self._current < 0:
			self._current = len(self._page)-1

		await self._update()

class Player:

	def __init__(self, guild):
		self.guild = guild
		self.queue = None
		self.player = None

	@classmethod
	async def pull(cls, guild):
		p = cls(guild)
		p.queue = await MusicQueue.pull(guild)
		p.player = await MusicPlayer.pull(guild)
		return p
	
	@staticmethod
	async def setup(guild, name):
		channel = await guild.create_text_channel(name = name)
		q = await channel.send(
			embed = MusicQueue.default(channel.guild), 
			components = ComponentQueue.turn_off()
		)
		p = await channel.send(
			embed = MusicPlayer.default(channel.guild),
			components = ComponentPlayer.turn_off()
		)

		database.clear(channel.guild)
		database.add('channel', channel.guild, channel.id)
		database.add('player', channel.guild, p.id)
		database.add('queue', channel.guild, q.id)
		return channel
	
	@staticmethod
	async def unsetup(guild):
		channel = guild.get_channel(database.pull('channel', guild))
		await channel.delete()
		database.clear(guild)
	
	@staticmethod
	async def cleanup(guild):
		q = await MusicQueue.pull(guild)
		p = await MusicPlayer.pull(guild)
		await q.clear()
		await p.clear()


	