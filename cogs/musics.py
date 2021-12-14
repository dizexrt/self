from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from main import guild_ids, voice, name
from alert import Alert

class Music(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	@cog_ext.cog_slash(
		name = 'setup',
		description = f'เลือกการตั้งค่าให้กับห้องของ{name}',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'option',
				description = 'เลือกการตั้งค่า',
				option_type = 3,
				required = True,
				choices = [
					create_choice(value = 'create', name = '✅สร้างห้อง'),
					create_choice(value = 'delete', name = '❎ลบห้อง')
				]
			)
		]
	)
	async def _setup(self, ctx:SlashContext, option:str):
		
		log = ctx.author.guild_permissions
		alert = Alert.music(ctx)

		
		if log.administrator or log.manage_channels:
			channel = voice.player.find(ctx.guild)

			if channel is None:

				if option == 'create':
					channel = await voice.player.setup(ctx.guild)
					return await alert.player.setup(channel)
				
				if option == 'delete':
					return await alert.player.not_exist()
				
			if channel is not None:
				
				if option == 'create':
					return await alert.player.exist(channel)
				
				if option == 'delete':
					await voice.player.unsetup(ctx.guild)
					try:
						await alert.player.unsetup()
					except:pass
					return 
		
		
		return await alert.user.require_permission('แอดมิน หรือ การจัดการแชนแนล')

	@cog_ext.cog_slash(
		name = 'play',
		description = 'เปิดเพลง',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'query',
				description = 'ใส่ชื่อเพลง หรือ ลิงก์เพลงจาก Youtube',
				option_type = 3,
				required = True
			)
		]
	)
	async def _play(self, ctx:SlashContext, query:str):
		channel = voice.player.find(ctx.channel.guild)
		if channel is not None:
			await voice.play_slash(ctx, query, channel)
		else:
			pass

def setup(client):
	client.add_cog(Music(client))