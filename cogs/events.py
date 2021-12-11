from discord.ext import commands
from main import voice
from discord_slash import ComponentContext
import asyncio
from async_timeout import timeout

#command create
class Event(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	@commands.Cog.listener()
	async def on_message(self, message):

		channel = voice.player.find(message.channel.guild)

		if message.channel == channel:
			if message.author.bot: return await message.edit(delete_after = 3)
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
	async def on_voice_state_update(self, member, before, after):
    

		voice_client = member.guild.voice_client

		if not member.bot:

			if voice_client is None: return
			
			if before.channel != voice_client.channel:return

			try:
				async with timeout(150):
					len(voice_client.channel.members) > 1
					
			except asyncio.TimeoutError:
				return await voice_client.disconnect()
					
		
		if member.bot:

			if after.channel is not None:
				try:
					async with timeout(150):

						len(voice_client.channel.members) > 1 and voice_client.is_playing()
						
				except asyncio.TimeoutError:
					return await voice_client.disconnect()

	
	@commands.Cog.listener()
	async def on_component(self, ctx:ComponentContext):

		log = ctx.custom_id

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
		
		await ctx.edit_origin(content = '')

#setup command
def setup(client):
	client.add_cog(Event(client))


