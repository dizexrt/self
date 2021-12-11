#System import
import os
from online import keep_alive

#discord
import discord
from discord.ext import commands
from discord_slash import SlashCommand

#owner
from voice.action import Voice

#bot setup
class Bot:

	prefix = "l."
	token = os.environ['lavender']
	
	@staticmethod
	def intents():
		intents = discord.Intents.all()
		intents.members = True
		return intents

#client using
client = commands.Bot(Bot.prefix, intents = Bot.intents())
slash = SlashCommand(client, sync_commands = True)
voice = Voice(client)

#upload commands
for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

#run client
keep_alive()
client.run(Bot.token)