from alert import Alert
from voice.music import SongAPI

class Voice:

	def __init__(self, client):
		self.client = client
		self.player = SongAPI(client)

	async def join(self, ctx):
		log = VoiceState(ctx)
		alert = Alert.voice(ctx)
		user = alert.user
		bot = alert.bot

		if not log.user:
			return await user.empty(ctx)
		
		if log.user and not log.bot:
			await ctx.author.voice.channel.connect()
			await bot.join(ctx, ctx.voice_client.channel)
		
		if log.bot:
		
			if not log.together:
				return await user.not_together(ctx, ctx.bot.user)
			
			if log.together:
				return await user.now_together(ctx, ctx.bot.user, ctx.voice_client.channel)
	
	async def play(self, message):
		ctx = await self.client.get_context(message)
		log = VoiceState(ctx)
		alert = Alert.voice(ctx)
		user = alert.user
		bot = alert.bot

		if not log.user:
			return await user.must_join(ctx)
		
		if log.user and not log.bot:
			await ctx.author.voice.channel.connect()
			await bot.join(ctx, ctx.voice_client.channel)
			return await self.playr.put(message.content, True)
		
		if log.bot:
		
			if not log.together:
				return await user.mustbe_together(ctx, ctx.bot.user)
			
			if log.together:
				return await self.player.put(message.content, False)
				
class VoiceState:

	def __init__(self, ctx):
		self.ctx = ctx
		self.user = self._user_log()
		self.bot = self._bot_log()
		self.together = self._together()

	def _user_log(self):
		if self.ctx.author.voice is None: return False
		return True
	
	def _bot_log(self):
		if self.ctx.voice_client is None: return False
		return True
	
	def _together(self):
		if self.user and self.bot:
			if self.ctx.author.voice.channel == self.ctx.voice_client.channel:
				return True
		
		return False
