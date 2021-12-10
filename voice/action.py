import discord 
from discord.ext import commands
import typing

class Voice:
	def __init__(self, client:typing.Union[discord.Client, commands.Bot]):
		self.client = client

	async def join(self, author:discord.abc.User, channel:discord.TextChannel):
		voice_client = channel.guild.voice_client
		if author.voice is None:
			await channel.send("คุณต้องเข้าช่องเสียงก่อนจะให้สายไหมเข้าไปอยู่ด้วยนะ")
			return False

		if voice_client is not None:
			if author.voice.channel == voice_client.channel:
				return True
			
			await channel.send(f"ตอนนี้สายไหมอยู่ในช่องเสียง  {voice_client.channel.mention} กับคนอื่นแล้ว")
			return False

		vc = author.voice.channel
		await vc.connect()
		voice_client = channel.guild.voice_client
		
		await channel.send(f"สายไหมเข้าร่วมช่องเสียงกับคุณในห้อง {voice_client.channel.mention} แล้ว");
		return True
	
	def is_none(self, guild:discord.Guild):
		if guild.voice_client is None:return True
		return False
	
	def pull_source(self, name:str):
		path = f"sound/{name}.mp3"
		source = discord.FFmpegPCMAudio(source = path)
		return source
	
	@classmethod
	def check(cls, author:discord.abc.User, voice_client:discord.VoiceClient):
		if voice_client is None : 
			return False

		if author.voice is None:
			return False
		
		if voice_client.channel == author.voice.channel:
			return True
		
		return False