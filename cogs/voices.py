from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from main import guild_ids, voice, source
from gtts import gTTS
import random
from alert import Alert

#create commands
class VoiceAction(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	#say message from sender
	@cog_ext.cog_slash(
		name = 'say',
		description = 'say message that you send',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'message',
				description = 'send message that you want to listen',
				option_type = 3,
				required = True
			)
		]
	)
	async def _say(self, ctx:SlashContext, message:str):
		tts = gTTS(message, lang = 'th')
		tts.save("voice/source/tts.mp3")
		await voice.play_source(ctx, 'tts')
	
	#random sound
	@cog_ext.cog_slash(
		name = 'random',
		description = 'random sound to speak',
		guild_ids = guild_ids,
	)
	async def _random(self, ctx:SlashContext):
		await voice.play_source(ctx, random.choice(source))

	#fix sound to play
	@cog_ext.cog_slash(
		name = 'fix',
		description = 'play sound from number',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'number',
				description = 'input number that you want to listen',
				option_type = 4,
				required = True
			)
		]
	)
	async def _fix(self, ctx:SlashContext, number:int):
		if number > 0 and number <= len(source):
			pull = source[number-1]
			return await voice.play_source(ctx, pull)
		
		alert = Alert.music(ctx)
		return await alert.player.not_found()
	
	#stop sound
	@cog_ext.cog_slash(
		name = 'stop',
		description = 'stop bot from playing sound',
		guild_ids = guild_ids,
	)
	async def _stop(self, ctx:SlashContext):
		await voice.stop(ctx)

def setup(client):
	client.add_cog(VoiceAction(client))