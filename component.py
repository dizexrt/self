import discord
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import typing


#button options
class Button:

	style  = {
		'red':ButtonStyle.red,
		'green':ButtonStyle.green,
		'blue':ButtonStyle.blue,
		'gray':ButtonStyle.gray,
		'link':5
	}

#creaete mini button
def button(
	active:bool,
	label:str, 
	id:str,
	style:str, 
	emoji:typing.Union[discord.Emoji, discord.PartialEmoji, str] = None,
	url:str = None
):
	style = Button.style[style]
	return create_button(style, label, emoji, id, url, not active)

#group mini button
def ButtonGroup(*button:button):
	return create_actionrow(*button)