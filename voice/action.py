from alert import Alert
from voice.song import SongAPI
import discord

#Main class for create voice action
class Voice:

	def __init__(self, client):
		self.client = client
		self.player = SongAPI(client)

	#join with slash
	async def slash_join(self, ctx):

		log = VoiceState(ctx)
		alert = Alert.voice(ctx)
		user = alert.user
		bot = alert.bot

		if not log.user:
			return await user.empty()

		if log.user and not log.bot:
			await ctx.author.voice.channel.connect()
			await bot.join(ctx.voice_client.channel)

		if log.bot:

			if not log.together:
				return await user.not_together(ctx.bot.user)

			if log.together:
				return await user.now_together(ctx.bot.user, ctx.voice_client.channel)
	
	#play music from song.py
	async def play(self, message):

		ctx = await self.client.get_context(message)
		log = VoiceState(ctx)
		alert = Alert.voice(ctx)
		user = alert.user
		bot = alert.bot

		if not log.user:
			return await user.must_join()

		if log.user and not log.bot:
			await ctx.author.voice.channel.connect()
			await bot.join(ctx.voice_client.channel)
			return await self.player.put(message, True)
		
		#bot not free
		if log.bot:

			if not log.together:
				return await user.mustbe_together(ctx.bot.user)

			if log.together:
				return await self.player.put(message, False)
	
	#play source from path
	async def play_source(self, ctx, name):
		log = VoiceState(ctx)
		alert = Alert.voice(ctx)
		user = alert.user
		bot = alert.bot

		if not log.user:
			return await user.must_join()

		if log.user and not log.bot:
			await ctx.author.voice.channel.connect()
			await bot.join(ctx.voice_client.channel)
			source = Source.pull(name)
			ctx.voice_client.play(source)
			return await bot.play()

		if log.bot:
			
			if not log.together:
				return await user.mustbe_together(ctx.bot.user)

			if log.together:
				source = Source.pull(name)
				try:
					ctx.voice_client.play(source)
				except:
					return await bot.busy()

				return await bot.play()

	#stop playing sound slash
	async def stop(self, ctx):

		log = VoiceState(ctx)
		alert = Alert.voice(ctx)

		if not log.user:
			return await alert.user.must_join()
		
		if not log.bot:
			return await alert.bot.empty()

		if log.bot and not log.together:
			return await alert.user.mustbe_together(ctx.bot.user)

		if log.bot and log.together:
			ctx.voice_client.stop()
			return await alert.bot.stop()

	#stop playing sound slash
	async def disconnect(self, ctx):

		log = VoiceState(ctx)
		alert = Alert.voice(ctx)

		if not log.user:
			return await alert.user.must_join()

		if not log.bot:
			return await alert.bot.empy()

		if log.bot and not log.together:
			return await alert.user.mustbe_together(ctx.bot.user)

		if log.bot and log.together:
			await ctx.voice_client.disconnect()
			return await alert.user.disconnect(ctx.bot.user)			
	
#class for source	
class Source:

	@staticmethod
	def pull(name:str):
		path = f"voice/source/{name}.mp3"
		return discord.FFmpegPCMAudio(path)
	


#class fro checking voice state
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
