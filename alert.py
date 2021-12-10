import discord

def embed(alert:str):
	embed = discord.Embed()
	embed.description = alert
	embed.colour = discord.Colour.purple()
	return embed

async def send(ctx, alert:str):
	await ctx.send(embed = embed(alert))

class Alert:

	def __init__(self):
		self.user = None
		self.bot = None

	@classmethod
	def voice(cls, ctx):
		voice = cls()
		voice.user = UserVoice(ctx.author)
		voice.bot = BotVoice(ctx.bot.user)
		return voice	


class UserVoice:

	def __init__(self, user):
		self.user = user

	async def empty(self, ctx, call:bool = False):
		await send(ctx, f"You are not in voice channel now")
	
	async def join(self, ctx, channel, call_self:bool):
		await send(ctx, f"{self.user.name} has joined {channel.mention} channel")
	
	async def leave(self, ctx):
		await send(ctx, f"{self.user.name} has left from voice channel")

	async def now_together(self, ctx, user, channel):
		await send(ctx, f"{user.name} is already in voice channel {channel.mention} with you")
	
	async def not_together(self, ctx, user):
		await send(ctx, f"You are not in voice channel with {user.name} now")
	
	async def mustbe_together(self, ctx, user):
		await send(ctx, f"You have to join voice channel with {user.name} first")

	async def must_join(self, ctx):
		await send(ctx, "You have to join voice channel first")

class BotVoice:
	
	def __init__(self, user):
		self.user = user
	
	async def leave(self, ctx):
		await send(ctx, f"{self.user.name} has left from voice channel")
	
	async def join(self, ctx, channel):
		await send(ctx, f"{self.user.name} has joined {channel.mention} channel")
	
	async def empy(self, ctx):
		await send(ctx, f"{self.user.name} is not in voice channel now")

class MusicAlert(Alert):pass

class PlayerAlert(Alert):pass

