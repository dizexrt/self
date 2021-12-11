from replit import db
import discord

class Database:
	
	@staticmethod
	def pull(option:str, guild:discord.Guild):
		try:
			value = db[str(guild.id)][option]
		except:
			return None

		return value
	
	@staticmethod
	def add(option:str, guild:discord.Guild, value):
		try:
			db[str(guild.id)][option]
		except:
			db[str(guild.id)][option] = value
			return True

		return False

	@staticmethod
	def clear(guild:discord.Guild):
		db[str(guild.id)] = {}