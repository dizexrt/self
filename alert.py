import discord
from discord_slash import SlashContext
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord.ext import commands
import typing

class Alert:

	join_btn_on = [
		create_actionrow(
			create_button(
				style = ButtonStyle.green,
				label = "Join",
				emoji = "➡",
				custom_id = 'join_btn',
				disabled = False
			)
		)
	]

	join_btn_off = [
		create_actionrow(
			create_button(
				style = ButtonStyle.green,
				label = "Join",
				emoji = "➡",
				custom_id = 'join_btn',
				disabled = True
			)
		)
	]

	def __init__(self, client:typing.Union[discord.Client, commands.Bot]):
		self.client = client
		self.Embed = discord.Embed()
	
	async def vc_empty(self, ctx:SlashContext):
		self.Embed.title = "สายไหมยังไม่ได้อยู่ในห้องเสียงขณะนี้"
		self.Embed.description = "ชวนสายไหมเข้าช่องเสียงได้ผ่านปุ่มข้างล่างนี้เลยนะ😊"
		self.Embed.color = self.client.user.color
		self.Embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar_url)
		await ctx.send(
			embed = self.Embed, 
			components = self.join_btn_on
		)


