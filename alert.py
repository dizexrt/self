import discord
from component import button, ButtonGroup

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
		return await self.ctx.send(embed = embed(alert))

#alert base
class Alert:

	def __init__(self, ctx):
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	#create class for alert component
	@classmethod
	def component(cls, ctx):
		component = cls(ctx)
		component.bot = BotAlert(ctx.bot.user, ctx.channel)
		component.user = UserAlert(ctx.author, ctx)
		return component
	
	#create class for alert voice
	@classmethod
	def voice(cls, ctx):
		voice = cls(ctx)
		voice.user = UserAlert(ctx.author, ctx)
		voice.bot = BotAlert(ctx.bot.user, ctx)
		return voice
	
	#create class for alert something
	@classmethod
	def source(cls, ctx):
		alert = cls(ctx)
		alert.bot = BotAlert(ctx.author, ctx)
		alert.source = Source(ctx)
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
		return await self.send(f"❎ คุณยังไม่ได้เข้าช่องเสียงในขณะนี้")
	
	async def join(self, channel, call_self:bool):
		return await self.send(f"✅ {self.user.name} ได้เข้าร่วมช่องเสียง {channel.mention} แล้ว")
	
	async def leave(self):
		return await self.send(f"❌ {self.user.name} ได้ออกจากช่องเสียงแล้ว")
	
	async def disconnect(self, user):
		return await self.send(f"⭕ {self.user.name} ได้ตัดการเชื่อมต่อ {user.name} จากช่องเสียงแล้ว")

	async def now_together(self, user, channel):
		return await self.send(f"🍖 {user.name} ได้อยู่ร่วมช่องเสียง {channel.mention} กับคูณอยู่แล้ว")
	
	async def not_together(self, user):
		return await self.send(f"🥗 คุณยังไม่ได้เข้าช่องเสียงร่วมกับ {user.name} ในขณะนี้")
	
	async def mustbe_together(self, user):
		return await self.send(f"🥪 คุณต้องเข้าร่วมช่องเสียงกับ {user.name} ก่อนนะ")

	async def must_join(self):
		return await self.send("🔊 คุณต้องเข้าร่วมช่องเสียงก่อนนะ")

	async def require_permission(self, name:str):
		return await self.send(f"🔒 คุณต้องมีอำนาจ {name} ก่อนนะ")

#bot alert setting
class BotAlert:
	
	def __init__(self, bot, ctx):
		self.bot = bot
		self.sender = Sender(ctx)
		self.send = self.sender.send
	
	async def leave(self):
		return await self.send(f"⭕ {self.bot.name} ได้ออกจากช่องเสียงแล้ว")
	
	async def join(self, channel):
		return await self.send(f"⭕ {self.bot.name} ได้เข้าร่วมช่องเสียง {channel.mention} แล้ว")
	
	async def empty(self):
		return await self.send(f"⭕ {self.bot.name} ยังไม่ได้อยู่ในช่องเสียงในขณะนี้")

	async def play(self, channel):
		return await self.send(f"⭕ {self.bot.name} ทำการเล่นเสียงในห้องเสียง {channel.mention} แล้ว")
	
	async def stop(self):
		return await self.send(f"⭕ {self.bot.name} หยุดการเล่นเสียงแล้ว")

	async def busy(self):
		return await self.send(f"⭕ {self.bot.name} ยังไม่ว่างในขณะนี้")

	async def move_and_wait(self, channel):
		return await self.send(f"{self.bot.name} ได้ย้ายไปที่ห้อง {channel.mention} แล้ว แต่ ยังคงเล่นเสียงก่อนหน้าต่อไป")
		
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
		return await self.send("⭕ เกิดปัญหาขึ้นระหว่างการเล่นเสียง")

	async def skip(self):
		return await self.channel(f"⭕ {self.user.name} ได้ทำการข้ามเพลงปัจจุบัน")
	
	async def disconnect(self):
		return await self.channel(f"⭕ {self.user.name} ได้ตัดการเชื่อมต่อ {self.bot.name} จากช่องเสียง")
	
	async def play(self):
		return await self.channel(f"⭕ {self.bot.name} กลับมาเล่นเสียงต่อแล้ว")
	
	async def pause(self):
		return await self.channel(f"⭕ {self.bot.name} พักการใช้เสียงชั่วคราวแล้ว")
	
	async def loop_on(self):
		return await self.channel(f"⭕ {self.user.name} ได้เปิดการเล่นซ้ำเพลงปัจจุบันแล้ว")
	
	async def loop_off(self):
		return await self.channel(f"⭕ {self.user.name} ปิดการเล่นซ้ำเพลงปัจจุบันแล้ว")

	async def loop_all_on(self):
		return await self.channel(f"⭕ {self.user.name} ได้เปิดการเล่นซ้ำเพลงทั้งหมดแล้ว")
	
	async def loop_all_off(self):
		return await self.channel(f"⭕ {self.user.name} ปิดการเล่นซ้ำเพลงทั้งหมดแล้ว")
	
	async def setup(self, channel):
		return await self.send(f"⭕ สร้างช่องเสียงของ {self.bot.name} ที่ห้อง {channel.mention} แล้ว")
	
	async def unsetup(self):
		return await self.send("⭕ ลบช่องเสียงของสายไหมที่มีอยู่แล้ว")
	
	async def clear(self):
		return await self.channel(f"⭕ {self.bot.name} ได้ทำการออกจากช่องเสียงแล้ว")

	async def exist(self, channel):
		return await self.send(f"⭕ ห้องของ {self.bot.name} มีอยู่แล้วนะ {channel.mention}")
	
	async def not_exist(self):
		return await self.send(f"⭕ {self.bot.name} ยังไม่มีห้องของตัวเองนะ")

	async def not_found(self):
		return await self.send(f"⭕ {self.bot.name} ไม่พบเสียงที่ต้องการเล่น")


class Source:

	def __init__(self, ctx):
		self.send = Sender(ctx).send
		self.bot = ctx.bot.user
		self.ctx = ctx

	async def play(self, channel):
		return await self.ctx.send(
			content = 'เล่นเสียง',
			embed = embed(f"{self.bot.name} ได้ทำการเล่นเสียงในห้อง {channel.mention} แล้ว"),
			components = [
				ButtonGroup(
					button(True, label = 'stop', id = 'stop', style = 'red')
				)
			]
		)

