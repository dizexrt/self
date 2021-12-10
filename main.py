#System import
import os
from online import keep_alive

import discord
from discord.ext import commands
from discord_slash import SlashCommand

class Bot:

	prefix = "l."
	token = os.environ['lavender']
	
	@staticmethod
	def intents():
		intents = discord.Intents.all()
		intents.members = True
		return intents


client = commands.Bot(Bot.prefix, intents = Bot.intents())

slash = SlashCommand(client, sync_commands = True)

@client.event
async def on_ready():
	print(f"{client.user.name} is ready!")


for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

keep_alive()
client.run(Bot.token)