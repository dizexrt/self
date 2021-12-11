import discord

#embed creator fix
def embed(alert:str):
	embed = discord.Embed()
	embed.description = alert
	embed.colour = discord.Colour.purple()
	embed.set_author(name = "📢การแจ้งเตือน")
	return embed

#short sender
class Sender:

	def __init__(self, ctx):
		self.ctx = ctx

	async def send(self, alert:str):
		await self.ctx.send(embed = embed(alert))

#alert base
class Alert:

	def __init__(self, ctx):
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	#create class for alert voice
	@classmethod
	def voice(cls, ctx):
		voice = cls(ctx)
		voice.user = UserAlert(ctx.author, ctx)
		voice.bot = BotAlert(ctx.bot.user, ctx)
		return voice
	
	#create class for alert something
	@classmethod
	def create(cls, ctx):
		alert = cls(ctx)
		alert.user = UserAlert(ctx.author, ctx)
		alert.bot = BotAlert(ctx.bot.user, ctx)
		return alert

	#create class for alert musicplayer
	@classmethod
	def music(cls, ctx):
		music = cls(ctx)
		music.player = Music(ctx.author , ctx.bot.user, ctx)
		music.user = UserAlert(ctx.author, ctx)
		music.bot = BotAlert(ctx.bot.user, ctx)
		return music

#user alert setting
class UserAlert:

	def __init__(self, user, ctx):
		self.user = user
		self.sender = Sender(ctx)
		self.send = self.sender.send

	async def empty(self, call:bool = False):
		await self.send(f"❎ คุณยังไม่ได้เข้าช่องเสียงในขณะนี้")
	
	async def join(self, channel, call_self:bool):
		await self.send(f"✅ {self.user.name} ได้เข้าร่วมช่องเสียง {channel.mention} แล้ว")
	
	async def leave(self):
		await self.send(f"❌ {self.user.name} ได้ออกจากช่องเสียงแล้ว")
	
	async def disconnect(self, user):
		await self.channel(f"⭕ {self.user.name} ได้ตัดการเชื่อมต่อ {user.name} จากช่องเสียงแล้ว")

	async def now_together(self, user, channel):
		await self.send(f"🍖 {user.name} ได้อยู่ร่วมช่องเสียง {channel.mention} กับคูณอยู่แล้ว")
	
	async def not_together(self, user):
		await self.send(f"🥗 คุณยังไม่ได้เข้าช่องเสียงร่วมกับ {user.name} ในขณะนี้")
	
	async def mustbe_together(self, user):
		await self.send(f"🥪 คุณต้องเข้าร่วมช่องเสียงกับ {user.name} ก่อนนะ")

	async def must_join(self):
		await self.send("🔊 คุณต้องเข้าร่วมช่องเสียงก่อนนะ")

	async def require_permission(self, name:str):
		await self.send(f"🔒 คุณต้องมีอำนาจ {name} ก่อนนะ")

#bot alert setting
class BotAlert:
	
	def __init__(self, user, ctx):
		self.user = user
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	async def leave(self):
		await self.send(f"⭕ {self.user.name} ได้ออกจากช่องเสียงแล้ว")
	
	async def join(self, channel):
		await self.send(f"⭕ {self.user.name} ได้เข้าร่วมช่องเสียง {channel.mention} แล้ว")
	
	async def empty(self):
		await self.send(f"⭕ {self.user.name} ยังไม่ได้อยู่ในช่องเสียงในขณะนี้")

	async def play(self, channel):
		await self.send(f"⭕ {self.user.name} ทำการเล่นเสียงในห้องเสียง {channel.mention} แล้ว")
	
	async def stop(self):
		await self.send(f"⭕ {self.user.name} หยุดการเล่นเสียงแล้ว")

	async def busy(self):
		await self.send(f"⭕ {self.user.name} ยังไม่ว่างในขณะนี้")
		
#music player alert setting
class Music:

	def __init__(self, user, bot, ctx):
		self.user = user
		self.bot = bot
		self.sender = Sender(ctx)
		self.sender2 = Sender(ctx.channel)
		self.channel = self.sender2.send
		self.send = self.sender.send
	
	async def error(self):
		await self.send("⭕ เกิดปัญหาขึ้นระหว่างการเล่นเสียง")

	async def skip(self):
		await self.channel(f"⭕ {self.user.name} ได้ทำการข้ามเพลงปัจจุบัน")
	
	async def disconnect(self):
		await self.channel(f"⭕ {self.user.name} ได้ตัดการเชื่อมต่อ {self.bot.name} จากช่องเสียง")
	
	async def play(self):
		await self.channel(f"⭕ {self.bot.name} กลับมาเล่นเสียงต่อแล้ว")
	
	async def pause(self):
		await self.channel(f"⭕ {self.bot.name} พักการใช้เสียงชั่วคราวแล้ว")
	
	async def loop_on(self):
		await self.channel(f"⭕ {self.user.name} ได้เปิดการเล่นซ้ำเพลงปัจจุบันแล้ว")
	
	async def loop_off(self):
		await self.channel(f"⭕ {self.user.name} ปิดการเล่นซ้ำเพลงปัจจุบันแล้ว")

	async def loop_all_on(self):
		await self.channel(f"⭕ {self.user.name} ได้เปิดการเล่นซ้ำเพลงทั้งหมดแล้ว")
	
	async def loop_all_off(self):
		await self.channel(f"⭕ {self.user.name} ปิดการเล่นซ้ำเพลงทั้งหมดแล้ว")
	
	async def setup(self, channel):
		await self.send(f"⭕ สร้างช่องเสียงของ {self.bot.name} ที่ห้อง {channel.mention} แล้ว")
	
	async def unsetup(self):
		await self.send("⭕ ลบช่องเสียงของสายไหมที่มีอยู่แล้ว")
	
	async def clear(self):
		await self.channel(f"⭕ {self.bot.name} ได้ทำการออกจากช่องเสียงแล้ว")

	async def exist(self, channel):
		await self.send(f"⭕ ห้องของ {self.bot.name} มีอยู่แล้วนะ {channel.mention}")
	
	async def not_exist(self):
		await self.send(f"⭕ {self.bot.name} ยังไม่มีห้องของตัวเองนะ")

	async def not_found(self):
		await self.send(f"⭕ {self.bot.name} ไม่พบเสียงที่ต้องการเล่น")

