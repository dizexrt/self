from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from main import guild_ids, voice
from alert import Alert

class Music(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	@cog_ext.cog_slash(
		name = 'setup',
		description = 'create or delete music channel',
		guild_ids = guild_ids,
		options = [
			create_option(
				name = 'option',
				description = 'select option for setting up',
				option_type = 3,
				required = True,
				choices = [
					create_choice(value = 'create', name = '✅create'),
					create_choice(value = 'delete', name = '❎delete')
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
		
		
		return await alert.user.require_permission('administrator or manage channels')


def setup(client):
	client.add_cog(Music(client))