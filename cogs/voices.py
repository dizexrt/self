from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from main import guild_ids, voice, source, name
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
		description = f'ให้ {name} พูดข้อความที่คุณส่งมา',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'text',
				description = 'ป้อนข้อความ',
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
		description = f'ให้ {name} สุ่มเล่นเสียง',
		guild_ids = guild_ids,
	)
	async def _random(self, ctx:SlashContext):
		await voice.play_source(ctx, random.choice(source))

	#fix sound to play
	@cog_ext.cog_slash(
		name = 'fix',
		description = f'ให้ {name} เล่นเสียงตามหมายเลขที่กำหนด',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'number',
				description = f'ใส่หมายเลขที่กต้องการ 1 - {len(source)}',
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
		description = f'หยุดการใช้เสียงของ {name}',
		guild_ids = guild_ids,
	)
	async def _stop(self, ctx:SlashContext):
		await voice.stop(ctx)

	#stop sound
	@cog_ext.cog_slash(
		name = 'disconnect',
		description = f'ให้ {name} ออกจากช่องเสียง',
		guild_ids = guild_ids,
	)
	async def _disconnect(self, ctx:SlashContext):
		await voice.disconnect(ctx)

def setup(client):
	client.add_cog(VoiceAction(client))