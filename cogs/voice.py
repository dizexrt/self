from discord.ext import commands
from voice.action import Voice
from main import client


class Music(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	@commands.command(name = 'join')
	async def join(self, ctx):
		voice = Voice(client)
		await voice.join(ctx)


def setup(client):
	client.add_cog(Music(client))


