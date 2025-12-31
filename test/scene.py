import pyglet
from pyglet.window import Window
from pyglet_gamemaker.scene import Scene
from src.sprite import SpriteSheet
from src.types import *


class TestScene(Scene):
	WIDGET_POS = {'Test1': (0.2, 0.1), 'Test2': (0.5, 0.5), 'Test3': (0.7, 0.7)}

	default_font_info = None, 40

	def __init__(self, name, bg_color):
		super().__init__(name)
		self.bg_color = bg_color

	def initialize(self):
		self.sheet = SpriteSheet('Default Button.png', 3, 1)

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
		if button.ID == 'Test2':
			print(f'{self.__class__.__name__}: Test2 was clicked!')
		elif button.ID == 'Test3':
			print(f'{self.__class__.__name__}: Test3 was clicked!')

	def on_full_click(self, button):
		if button.ID == 'Test2':
			print(f'{self.__class__.__name__}: Test2 was fully pressed!')
		elif button.ID == 'Test3':
			print(f'{self.__class__.__name__}: Test3 was fully pressed!')

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
