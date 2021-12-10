from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import typing
import discord

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
	
class Button:

	style  = {
		'red':ButtonStyle.red,
		'green':ButtonStyle.green,
		'blue':ButtonStyle.blue,
		'gray':ButtonStyle.gray,
		'link':5
	}
	

def ButtonGroup(*button:button):
	return create_actionrow(*button)


class ComponentQueue:
	
	@classmethod
	def page(self, page:int, max:int):
		active = True
		
		if max == 1: active = False

		components = [
			ButtonGroup(
				button(active, label = '', id = 'previous', style = 'blue', emoji = '⏮'),
				button(False, label = f'page : {page}/{max}', id = 'page', style = 'gray'),
				button(active, label = '', id = 'next', style = 'blue', emoji = '⏭')
			)
		]
		return components
	
	@classmethod
	def turn_off(self):
		components = [
			ButtonGroup(
				button(False, label = '', id = 'previous', style = 'blue', emoji = '⏮'),
				button(False, label = f'page : 1/1', id = 'page', style = 'gray'),
				button(False, label = '', id = 'next', style = 'blue', emoji = '⏭')
			)
		]
		return components
	
class ComponentPlayer:

	@classmethod
	def turn_off(cls):
		components = [
			ButtonGroup(
				button(False, label = '', id = 'play', style = 'green', emoji = '▶'),
				button(False, label = '', id = 'pause', style = 'green', emoji = '⏸'),
				button(False, label = '', id = 'skip', style = 'gray', emoji = '⏭'),
				button(False, label = '', id = 'leave', style = 'red', emoji = '⏹'),
				button(False, label = 'link', id = None, style = 'link', url = 'https://www.youtube.com/')
			),
			ButtonGroup(
				button(False, label = '', id = 'loop', style = 'gray', emoji = '🔂'),
				button(False, label = '', id = 'loop_all', style = 'gray', emoji = '🔁')
			)
		]
		return components
	
	@classmethod
	def update(cls, loop:str, url:str):
		
		active, inactive = 'green', 'gray'

		if loop == 'one':
			one, all = active, inactive
		
		elif loop == 'all':
			one, all = inactive, active
		
		else:
			one, all = inactive, inactive

		components = [
			ButtonGroup(
				button(True, label = '', id = 'play', style = 'green', emoji = '▶'),
				button(True, label = '', id = 'pause', style = 'green', emoji = '⏸'),
				button(True, label = '', id = 'skip', style = 'gray', emoji = '⏭'),
				button(True, label = '', id = 'leave', style = 'red', emoji = '⏹'),
				button(True, label = 'link', id = None, style = 'link', url = url)
			),
			ButtonGroup(
				button(True, label = '', id = 'loop', style = one, emoji = '🔂'),
				button(True, label = '', id = 'loop_all', style = all, emoji = '🔁')
			)
		]

		return components
	
