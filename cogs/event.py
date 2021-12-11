from discord.ext import commands
from main import voice

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

		self.client.process_commands(message)
	
	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.client.user.name} is ready!")

def setup(client):
	client.add_cog(Event(client))


