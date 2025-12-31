from src.window import Window
from src.types import *
from pyglet_gamemaker.scene import Scene
from src.sprite import SpriteSheet


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
			self.dispatch_event('on_scene_change', 'TestScene2')

	def enable(self):
		print(self.__class__.__name__ + ' enabled')
		for widget in self.widgets.values():
			widget.enable()

	def disable(self):
		print(self.__class__.__name__ + ' disabled')
		for widget in self.widgets.values():
			widget.disable()


class TestScene2(Scene):
	WIDGET_POS = {
		'Test1': (0, 0.3),
		'Test2': (0.4, 0.6),
		'Test3': (0.6, 0.8),
	}

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
			self.dispatch_event('on_scene_change', 'TestScene')

	def enable(self):
		print(self.__class__.__name__, 'enabled')
		for widget in self.widgets.values():
			widget.enable()

	def disable(self):
		print(self.__class__.__name__, 'disabled')
		for widget in self.widgets.values():
			widget.disable()

test1 = TestScene('TestScene', Color.ORANGE)
test2 = TestScene2('TestScene2', Color.WHITE)

window = Window((640, 480))
window.add_scene('TestScene', test1)
window.add_scene('TestScene2', test2)
window.run()
