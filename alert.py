import discord
from component import button, ButtonGroup

#embed creator fix
def embed(alert:str):
	embed = discord.Embed()
	embed.description = alert
	embed.colour = discord.Colour.purple()
	embed.set_author(name = "📢 Noticefication")
	return embed

#short sender
class Sender:

	def __init__(self, ctx):
		self.ctx = ctx

	async def send(self, alert:str):
		return await self.ctx.send(embed = embed(alert))

#alert base
class Alert:

	def __init__(self, ctx):
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	#create class for alert voice
	@classmethod
	def voice(cls, ctx):
		voice = cls(ctx)
		voice.user = UserAlert(ctx.author, ctx)
		voice.bot = BotAlert(ctx.bot.user, ctx)
		return voice

	@classmethod
	def component(cls, ctx):
		voice = cls(ctx)
		voice.user = UserAlert(ctx.author, ctx)
		voice.bot = BotAlert(ctx.bot.user, ctx.channel)
		return voice
	
	#create class for alert something
	@classmethod
	def source(cls, ctx):
		alert = cls(ctx)
		alert.source = Source(ctx)
		alert.bot = BotAlert(ctx.bot.user, ctx)
		return alert

	#create class for alert musicplayer
	@classmethod
	def music(cls, ctx):
		music = cls(ctx)
		music.player = Music(ctx.author , ctx.bot.user, ctx)
		music.user = UserAlert(ctx.author, ctx)
		music.bot = BotAlert(ctx.bot.user, ctx)
		return music

#user alert setting
class UserAlert:

	def __init__(self, user, ctx):
		self.user = user
		self.sender = Sender(ctx)
		self.send = self.sender.send

	async def empty(self, call:bool = False):
		return await self.send(f"✅ You are not in voice channel now")
	
	async def join(self, channel, call_self:bool):
		return await self.send(f"✅ {self.user.name} has joined {channel.mention} channel")
	
	async def leave(self):
		return await self.send(f"🔌 {self.user.name} has left from voice channel")
	
	async def disconnect(self, user):
		return await self.send(f"🔌 {self.user.name} disconnected {user.name} from voice channel")

	async def now_together(self, user, channel):
		return await self.send(f"👥 {user.name} is already in voice channel {channel.mention} with you")
	
	async def not_together(self, user):
		return await self.send(f"👤 You are not in voice channel with {user.name} now")
	
	async def mustbe_together(self, user):
		return await self.send(f"👥 You have to join voice channel with {user.name} first")

	async def must_join(self):
		return await self.send("🔊 You have to join voice channel first")

	async def require_permission(self, name:str):
		return await self.send(f"🔒 You have to have {name} permissions first")

#bot alert setting
class BotAlert:
	
	def __init__(self, user, ctx):
		self.user = user
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	async def leave(self):
		return await self.send(f"🔌 {self.user.name} has left from voice channel")
	
	async def join(self, channel):
		return await self.send(f"✅ {self.user.name} has joined {channel.mention} channel")
	
	async def empy(self):
		return await self.send(f"⭕ {self.user.name} is not in voice channel now")
	
	async def stop(self):
		return await self.send(f"⭕ {self.user.name} has stopped playing the sound")
	
	async def empty(self):
		return await self.send(f"⭕ {self.user.name} is not joined voice channel now")

	async def busy(self):
		return await self.send(f"⭕ {self.user.name} is busy now")
	
	async def play(self, channel):
		return await self.send(f"🎙 {self.user.name} played the sound in channel {channel.mention}")
		
#music player alert setting
class Music:

	def __init__(self, user, bot, ctx):
		self.user = user
		self.bot = bot
		self.sender = Sender(ctx)
		self.sender2 = Sender(ctx.channel)
		self.channel = self.sender2.send
		self.send = self.sender.send
	
	async def error(self):
		return await self.send("👀 There is some problem while processing the song")

	async def skip(self):
		return await self.channel(f"⏭ {self.user.name} has skipped the song")
	
	async def disconnect(self):
		return await self.channel(f"🔌 {self.user.name} has disconnected {self.bot.name} from voice channel")
	
	async def play(self):
		return await self.channel(f"⏯ {self.user.name} has continued the song")
	
	async def pause(self):
		return await self.channel(f"⏯ {self.user.name} has paused the song")
	
	async def loop_on(self):
		return await self.channel("🔂 Loop current song is turned on")
	
	async def loop_off(self):
		return await self.channel("🔂 Loop current song is turned off")

	async def loop_all_on(self):
		return await self.channel("🔁 Loop all songs is turned on")
	
	async def loop_all_off(self):
		return await self.channel("🔁 Loop all songs is turned off")
	
	async def setup(self, channel):
		return await self.send(f"🧱 Channel is created as {channel.mention}")
	
	async def unsetup(self):
		return await self.send("❌ Deleted setup channel")
	
	async def clear(self):
		return await self.channel(f"⭕ {self.bot.name} has disconnected from voice channel")

	async def exist(self, channel):
		return await self.send(f"😊 {self.bot.name}'s channel is already exsit {channel.mention}")
	
	async def not_exist(self):
		return await self.send(f"🥪 {self.bot.name} is not have setup channel now")

	async def not_found(self):
		return await self.send(f"🥧 {self.bot.name} cannot found that sound")

class Source:

	def __init__(self, ctx):
		self.send = Sender(ctx).send
		self.channel = Sender(ctx.channel).send
		self.bot = ctx.bot.user
		self.ctx = ctx

	async def play(self, channel):
		return await self.ctx.send(
			content = 'play sound',
			embed = embed(f"✅ {self.bot.name} has played sound in channel {channel.mention} now"),
			components = [
				ButtonGroup(
					button(True, label = 'stop', id = 'stop', style = 'red')
				)
			]
		)