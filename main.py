#System import
import os
from online import keep_alive
from gtts import gTTS

#discord additional import
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_choice, create_option

#owner additional imported
from alert import Alert
from voice.action import Voice
from voice.music import SongAPI

#class for bot Setting
class Bot:
	Intents = discord.Intents.all()
	Prefix = "l."
	Token = os.environ['lavender']
		
Bot.Intents.members = True

client = commands.Bot(command_prefix= Bot.Prefix, intents= Bot.Intents)
Bot.Guilds = [g.id for g in client.guilds]

slash = SlashCommand(client, sync_commands = True)
alert = Alert(client)
voice = Voice(client)
music = SongAPI(client)

@client.event
async def on_ready():
	print(f"{client.user.name} is ready!")
	await music.cleanup()

@client.event
async def on_guild_join(guild):
	Bot.Guilds.append(guild.id)

@client.event
async def on_message(message):
	channel = message.channel
	guild = channel.guild

	music_channel = music.search(guild)
	bot = message.author.bot

	if music_channel is not None and channel == music_channel:
		
		if bot: return await message.edit(delete_after = 3)

		check = voice.is_none(guild)
		join = await voice.join(message.author, music_channel)
		
		if join:
			search = message
			await message.delete()
			await music.put(search, check)
			return
	
	if bot:return

	await client.process_commands(message)

@client.event
async def on_component(ctx:ComponentContext):
	log = ctx.custom_id

	if  log == "join_btn":
		await ctx.edit_origin(components = alert.join_btn_off)
		await voice.join(ctx, join_alert = True)
		return
	
	if log == "play":
		await music.play(ctx)
	
	if log == "skip":
		await music.skip(ctx)

	if log == "leave":
		await music.leave(ctx)

	if log == "pause":
		await music.pause(ctx)
	
	if log == "next":
		await music.queue_next(ctx)

	if log == "previous":
		await music.queue_previous(ctx)
	
	if log == "loop":
		await music.loop(ctx, 'one')

	if log == "loop_all":
		await music.loop(ctx, 'all')
	
	await ctx.edit_origin(content="")

@slash.slash(
	name = 'setup',
	description = "จัดการกับห้องของสายไหม",
	guild_ids = Bot.Guilds,
	options = [
			create_option(
			name = "option",
			description	= "เลือกหนึ่งอย่างที่คุณต้องการ",
			option_type	= 3,
			required 	= True,
			choices 	= [
				create_choice(value = 'create', name = '➕สร้างห้อง'),
				create_choice(value = 'delete', name = '➖ลบห้อง')
			]
		)
	]
)
async def _setup(ctx:SlashContext, option:str):
	guild = ctx.channel.guild
	permission = False

	for role in ctx.author.roles:
		if role.permissions.manage_channels is True:
			permission = True
			break
		
		if role.permissions.administrator is True:
			permission = True
			break
	
	if permission is False: 
		await ctx.send("คุณต้องมีอำนาจในการจัดการช่องก่อนนะ😁")
		return

	if option == 'create':
		
		channel = music.search(guild)

		if channel is None:
			channel = await music.setup(guild)
			return await ctx.send(f"ตั้งค่าห้องของ{client.user.name} แล้ว {channel.mention}")
		
		return await ctx.send(f"{client.user.name}มีห้องของตัวเองอยู่แล้ว {channel.mention}")

	if option == 'delete':
		
		channel = music.search(guild)

		if channel is not None:
			channel = await music.delete_setup(guild)
			return await ctx.send(f"ลบห้องของ{client.user.name}แล้ว")
		
		return await ctx.send(f"{client.user.name}ยังไม่มีห้องของตัวเอง")
			
#command
@slash.slash(
	name="join",
	description = "ถ้าห้องเธอยังว่าง เราขอเข้าไปอยู่ข้างๆนะ😳", 
	guild_ids = Bot.Guilds
)
async def _join(ctx: SlashContext):
	await voice.join(ctx, join_alert = True)

#command
@slash.slash(
	name = 'stop',
	description = "ต้องการให้สายไหมหยุดใช้เสียงงั้นหรอ😳",
	guild_ids = Bot.Guilds
)
async def _stop(ctx: SlashContext):
	if ctx.author.voice is None:
		await ctx.send ("คุณต้องอยู่ในช่องเสียงก่อนถึงจะใช้คำสั่งนี้ได้นะ")
		return

	if ctx.voice_client is None: 
		await alert.vc_empty(ctx)
		return

	if ctx.author.voice.channel == ctx.voice_client.channel:
		if ctx.voice_client.is_playing:
			ctx.voice_client.stop()
			await ctx.send("สายไหมหยุดการเล่นเสียงปัจจุบันแล้ว")
		else:
			await ctx.send ("สายไหมยังไม่ได้ใช้เสียงอยู่ในขณะนี้")
		return
	
	await ctx.send("สายไหมไม่ได้อยู่ร่วมห้องกับคุณ")

#command
@slash.slash(
	name="pause", 
	description = "ให้สายไหมพัก จิบน้ำมะนาวสักหน่อยนะ🤤", 
	guild_ids = Bot.Guilds
)
async def _pause(ctx:SlashContext):
	if ctx.author.voice is None:
		await ctx.send ("คุณต้องอยู่ในช่องเสียงก่อนถึงจะใช้คำสั่งนี้ได้นะ")
		return

	if ctx.voice_client is None: 
		await alert.vc_empty(ctx)
		return
	
	if ctx.author.voice.channel == ctx.voice_client.channel:
		if ctx.voice_client.is_playing:
			ctx.voice_client.pause()
			await ctx.send("สายไหมพักการใช้เสียงแล้ว")
		else:
			await ctx.send ("สายไหมยังไม่ได้ใช้เสียงอยู่ในขณะนี้")
		return
	
	await ctx.send("สายไหมไม่ได้อยู่ร่วมห้องกับคุณ")

#command
@slash.slash(
	name="resume", 
	description = "สายไหมพร้อมที่จะใช้เสียงต่อแล้ว😊", 
	guild_ids = Bot.Guilds
)
async def _resume(ctx:SlashContext):
	if ctx.author.voice is None:
		await ctx.send ("คุณต้องอยู่ในช่องเสียงก่อนถึงจะใช้คำสั่งนี้ได้นะ")
		return
		
	if ctx.voice_client is None: 
		await alert.vc_empty(ctx)
		return

	if ctx.author.voice.channel == ctx.voice_client.channel:
		if ctx.voice_client.is_paused:
			ctx.voice_client.resume()
			await ctx.send("สายไหมกลับมาใช้เสียงต่อแล้ว")
		else:
			await ctx.send ("สายไหมยังไม่ได้พักการเล่นเสียงอยู่ในขณะนี้")
		return
	
	await ctx.send("สายไหมไม่ได้อยู่ร่วมห้องกับคุณ")

#command
@slash.slash(
	name = 'disconnect',
	description = 'ให้สายไหมออกจากช่องเสียงของคุณ',
	guild_ids = Bot.Guilds
)
async def _disconnect(ctx:SlashContext):
	if ctx.author.voice is None:
		await ctx.send ("คุณต้องอยู่ในช่องเสียงก่อนถึงจะใช้คำสั่งนี้ได้นะ")
		return
		
	if ctx.voice_client is None: 
		await alert.vc_empty(ctx)
		return

	if ctx.author.voice.channel == ctx.voice_client.channel:
		await ctx.voice_client.disconnect()
		await ctx.send("สายไหมได้ออกจากช่องเสียงแล้ว")
		return
	
	await ctx.send("สายไหมไม่ได้อยู่ร่วมห้องกับคุณ")

#command
@slash.slash(
	name = 'speak',
	description = "ให้สายไหมพูดตามข้อความที่ส่งมา",
	guild_ids = Bot.Guilds,
	options = [
		create_option(
			name = 'text',
			description = "ใส่ข้อความที่ต้องการให้สายไหมอ่าน",
			option_type = 3,
			required = True
		)
	]
)
async def _speak(ctx:SlashContext, text:str):
	join = await voice.join(ctx.author, ctx.channel)

	if join:
		tts = gTTS(text = text, lang = 'th')
		tts.save('voice/source/tts.mp3')
		source = voice.pull_source('tts')

		try:
			ctx.voice_client.play(source)
		except:
			await ctx.send("สายไหมยังไม่สามารถพูดได้ในขณะนี้")
			return
		else:
			await ctx.send(f"สายไหมพูดข้อความในห้อง {ctx.voice_client.channel.mention} แล้ว")
			return

@slash.slash(
	name = 'ครส',
	description = "ให้สายไหมพูดตามข้อความที่ส่งมา",
	guild_ids = Bot.Guilds,
)
async def d(ctx:SlashContext):
	join = await voice.join(ctx.author, ctx.channel)

	if join:
		source = voice.pull_source('ครส')
		try:
			ctx.voice_client.play(source)
		except:
			await ctx.send("สายไหมยังไม่สามารถพูดได้ในขณะนี้")
			return
		else:
			await ctx.send(f"สายไหมเล่นเสียงในห้อง {ctx.voice_client.channel.mention} แล้ว")
			return
		
keep_alive()
client.run(Bot.Token)