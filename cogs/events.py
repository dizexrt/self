from discord.ext import commands
from main import voice
from discord_slash import ComponentContext

#command create
class Event(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	@commands.Cog.listener()
	async def on_message(self, message):

		channel = voice.player.find(message.channel.guild)

		if message.channel == channel:
			if message.author.bot: 
				if message.content == 'เล่นเสียง':return
				return await message.edit(delete_after = 3)
			source = message
			await message.delete()
			return await voice.play(source)
		
		if message.author.bot : return

		await self.client.process_commands(message)
	
	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.client.user.name} is ready!")
		await voice.player.cleanup()
	
	@commands.Cog.listener()
	async def on_component(self, ctx:ComponentContext):

		log = ctx.custom_id

		if log == 'stop':
			if await voice.stop_component(ctx):
				return await ctx.edit_origin(content = '')

		await ctx.edit_origin(content = '')
		
		if log == 'play':
			await voice.player.play(ctx)
		
		elif log == 'pause':
			await voice.player.pause(ctx)

		elif log == 'loop':
			await voice.player.loop(ctx, 'one')
		
		elif log == 'loop_all':
			await voice.player.loop(ctx, 'all')

		elif log == 'leave':
			await voice.player.leave(ctx)
		
		elif log == 'skip':
			await voice.player.skip(ctx)

		elif log == 'next':
			await voice.player.next_q(ctx)

		elif log == 'previous':
			await voice.player.prev_q(ctx)

#setup command
def setup(client):
	client.add_cog(Event(client))


