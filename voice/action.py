from alert import Alert
from voice.song import SongAPI
import discord

#Main class for create voice action
class Voice:

	def __init__(self, client):
		self.client = client
		self.player = SongAPI(client)
	
	#play music from song.py
	async def play(self, message):

		ctx = await self.client.get_context(message)
		log = VoiceState(ctx)
		alert = Alert.voice(ctx)

		if not log.user:
			return await alert.user.must_join()

		if log.user and not log.bot:

			await ctx.author.voice.channel.connect()
			await alert.bot.join(ctx.voice_client.channel)
			return await self.player.put(message)
		
		#bot not free
		if log.bot:

			if not log.together:

				if not log.bot_alone:
					return await alert.user.mustbe_together(ctx.bot.user)
				
				if log.bot_alone:
					await ctx.voice_client.move_to(ctx.author.voice.channel)
					return await self.player.put(message)

			if log.together:
				return await self.player.put(message)
	
	async def play_slash(self, ctx, query, channel):

		log = VoiceState(ctx)
		alert = Alert.voice(ctx)

		if not log.user:
			return await alert.user.must_join()

		if log.user and not log.bot:

			await ctx.author.voice.channel.connect()
			await alert.bot.add(channel)
			return await self.player.put_query(ctx, query)
		
		#bot not free
		if log.bot:

			if not log.together:

				if not log.bot_alone:
					return await alert.user.mustbe_together(ctx.bot.user)
				
				if log.bot_alone:
					await ctx.voice_client.move_to(ctx.author.voice.channel)
					await alert.bot.add(channel)
					return await self.player.put_query(ctx, query)

			if log.together:
				await alert.bot.add(channel)
				return await self.player.put_query(ctx, query)
	
	#play music from song.py
	async def play_source(self, ctx, name):
		log = VoiceState(ctx)
		alert = Alert.source(ctx)

		if not log.user:
			return await alert.user.must_join()

		if log.user and not log.bot:

			await ctx.author.voice.channel.connect()
			message = await alert.source.play(ctx.voice_client.channel)
			return await self.player.put_source(ctx, name, message)
		
		#bot not free
		if log.bot:

			if not log.together:

				if not log.bot_alone:
					return await alert.user.mustbe_together(ctx.bot.user)
				
				if log.bot_alone:
					await ctx.voice_client.move_to(ctx.author.voice.channel)
					if not ctx.voice_client.is_playing():
						message = await alert.source.play(ctx.voice_client.channel)
						return await self.player.put_source(ctx, name, message)
					else:
						await alert.bot.move_and_wait(ctx.voice_client.channel)

			if log.together:
				if not ctx.voice_client.is_playing():
					message = await alert.source.play(ctx.voice_client.channel)
					return await self.player.put_source(ctx, name, message)
				
				else:
					return await alert.bot.busy()
			

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
	
	async def stop_component(self, ctx):

		log = VoiceState(ctx)
		alert = Alert.component(ctx)
		alertv = Alert.voice(ctx)

		if not log.user:
			await alert.user.must_join()
			return False
		
		if not log.bot:
			await alertv.bot.empty()
			return False

		if log.bot and not log.together:
			await alert.user.mustbe_together(ctx.bot.user)
			return False

		if log.bot and log.together:
			ctx.voice_client.stop()
			await alert.bot.stop()
			return True

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
		self.bot_alone = self._bot_alone()

	def _user_log(self):
		if self.ctx.author.voice is None: return False
		return True
	
	def _bot_log(self):
		if self.ctx.voice_client is None: return False
		return True
	
	def _bot_alone(self):
		if self.ctx.voice_client is not None:
			if len(self.ctx.voice_client.channel.members) == 1:
				return True
		return False
	
	def _together(self):
		if self.user and self.bot:
			if self.ctx.author.voice.channel == self.ctx.voice_client.channel:
				return True
		
		return False
