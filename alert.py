import discord

#embed creator fix
def embed(alert:str):
	embed = discord.Embed()
	embed.description = alert
	embed.colour = discord.Colour.purple()
	embed.set_author(name = "Noticefication")
	return embed

#short sender
class Sender:

	def __init__(self, ctx):
		self.ctx = ctx

	async def send(self, alert:str):
		await self.ctx.send(embed = embed(alert))

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
	
	#create class for alert something
	@classmethod
	def create(cls, ctx):
		alert = cls(ctx)
		alert.user = UserAlert(ctx.author, ctx)
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
		await self.send(f"You are not in voice channel now")
	
	async def join(self, channel, call_self:bool):
		await self.send(f"{self.user.name} has joined {channel.mention} channel")
	
	async def leave(self):
		await self.send(f"{self.user.name} has left from voice channel")

	async def now_together(self, user, channel):
		await self.send(f"{user.name} is already in voice channel {channel.mention} with you")
	
	async def not_together(self, user):
		await self.send(f"You are not in voice channel with {user.name} now")
	
	async def mustbe_together(self, user):
		await self.send(f"You have to join voice channel with {user.name} first")

	async def must_join(self):
		await self.send("You have to join voice channel first")

	async def require_permission(self, name:str):
		await self.send(f"You have to have {name} permissions first")

#bot alert setting
class BotAlert:
	
	def __init__(self, user, ctx):
		self.user = user
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	async def leave(self):
		await self.send(f"{self.user.name} has left from voice channel")
	
	async def join(self, channel):
		await self.send(f"{self.user.name} has joined {channel.mention} channel")
	
	async def empy(self):
		await self.send(f"{self.user.name} is not in voice channel now")
	
	async def stop(self):
		await self.send(f"{self.user.name} has stopped playing the sound")

	async def busy(self):
		await self.send(f"{self.user.name} is busy now")
		
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
		await self.send("There is some problem while processing the song")

	async def skip(self):
		await self.channel(f"{self.user.name} has skipped the song")
	
	async def disconnect(self):
		await self.channel(f"{self.user.name} has disconnected {self.bot.name} from voice channel")
	
	async def play(self):
		await self.channel(f"{self.user.name} has continued the song")
	
	async def pause(self):
		await self.channel(f"{self.user.name} has paused the song")
	
	async def loop_on(self):
		await self.channel("Loop current song is turned on")
	
	async def loop_off(self):
		await self.channel("Loop current song is turned off")

	async def loop_all_on(self):
		await self.channel("Loop all songs is turned on")
	
	async def loop_all_off(self):
		await self.channel("Loop all songs is turned off")
	
	async def setup(self, channel):
		await self.send(f"Channel is created as {channel.mention}")
	
	async def unsetup(self):
		await self.send("Deleted setup channel")
	
	async def clear(self):
		await self.channel(f"{self.bot.name} has disconnected from voice channel")

	async def exist(self, channel):
		await self.send(f"{self.bot.name}'s channel is already exsit {channel.mention}")
	
	async def not_exist(self):
		await self.send(f"{self.bot.name} is not have setup channel now")

	async def not_found(self):
		await self.send(f"{self.bot.name} cannot found that sound")

