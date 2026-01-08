from __future__ import annotations

import pyglet
from pyglet.window import Window

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.sprite.sprite_sheet import SpriteSheet
from pyglet_gamemaker.types import Color


class TestScene(Scene):
	WIDGET_POS = {'Test1': (0.2, 0.1), 'Test2': (0.5, 0.5), 'Test3': (0.7, 0.7)}

	default_font_info = None, 40

	def __init__(self, name, bg_color):
		super().__init__(name)
		self.bg_color = bg_color

	def initialize(self):
		self.sheet = SpriteSheet('Test Button SpriteSheet.png', 3, 1)

		self.bg = self.create_bg(self.bg_color)
		self.create_text(
			'Test1',
			'Hi',
			('center', 'center'),
		)
		self.create_button(
			'Test2',
			self.sheet,
			0,
			('center', 'center'),
			on_half_click=self.on_half_click,
			on_full_click=self.on_full_click,
		)
		self.create_text_button(
			'Test3',
			'Hi2',
			self.sheet,
			0,
			('center', 'center'),
			('center', 'center'),
			hover_enlarge=5,
			on_half_click=self.on_half_click,
			on_full_click=self.on_full_click,
		)

	def on_half_click(self, button):
		print(f'{self.__class__.__name__}: {button.ID} was clicked!')

	def on_full_click(self, button):
		print(f'{self.__class__.__name__}: {button.ID} was fully pressed!')

	def enable(self):
		for widget in self.widgets.values():
			widget.enable()

	def disable(self):
		for widget in self.widgets.values():
			widget.disable()


menu = TestScene('Test', Color.ORANGE)
window = Window(640, 480, caption=__name__)
menu.set_window(window)
menu.enable()


@window.event
def on_draw():
	window.clear()
	menu.batch.draw()


pyglet.app.run()
