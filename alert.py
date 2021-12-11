import discord

def embed(alert:str):
	embed = discord.Embed()
	embed.description = alert
	embed.colour = discord.Colour.purple()
	return embed


class Sender:

	def __init__(self, ctx):
		self.ctx = ctx

	async def send(self, alert:str):
		await self.ctx.send(embed = embed(alert))

class Alert:

	def __init__(self):pass

	@classmethod
	def voice(cls, ctx):
		voice = cls()
		voice.user = UserVoice(ctx.author, ctx)
		voice.bot = BotVoice(ctx.bot.user, ctx)
		return voice
	
	@classmethod
	def music(cls, ctx):
		music = cls()
		music.player = Player(ctx)
		return music


class UserVoice:

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

class BotVoice:
	
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

class Player:

	def __init__(self, ctx):
		self.ctx = ctx
		self.guild = ctx.guild
	
	async def error(self):
		pass

