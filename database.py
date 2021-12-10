from replit import db
import discord

class Database:
	
	@classmethod
	def pull(cls, option:str, guild:discord.Guild):
		try:
			value = db[str(guild.id)][option]
		except:
			return None

		return value
	
	@classmethod
	def add(cls, option:str, guild:discord.Guild, value):
		try:
			db[str(guild.id)][option]
		except:
			db[str(guild.id)][option] = value
			return True

		return False

	@classmethod
	def clear(cls, guild:discord.Guild):
		db[str(guild.id)] = {}