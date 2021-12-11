from replit import db
import discord

#class for get data from data base easier
class Database:
	
	#pull data
	@staticmethod
	def pull(option:str, guild:discord.Guild):
		try:
			value = db[str(guild.id)][option]
		except:
			return None

		return value
	
	#add data if not exist
	@staticmethod
	def add(option:str, guild:discord.Guild, value):
		try:
			db[str(guild.id)][option]
		except:
			db[str(guild.id)][option] = value
			return True

		return False

	#clear data only
	@staticmethod
	def clear(guild:discord.Guild):
		db[str(guild.id)] = {}