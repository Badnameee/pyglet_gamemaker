# type: ignore

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from src.gui import TextButton
from src.sprite import SpriteSheet

window = Window(640, 480, caption=__name__)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = Batch()
group = Group()

sheet = SpriteSheet('Default Button.png', 3, 1)
sheet.name('Unpressed', 'Hover', 'Pressed')

def on_half_click(button):
	print(f'{button} pressed down on!')
def on_full_click(button):
	print(f'{button} fully pressed and releaased!')

hover_enlarge = 3

@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.LEFT:
		button.x -= 10
	elif symbol == key.RIGHT:
		button.x += 10
	elif symbol == key.UP:
		button.y += 10
	elif symbol == key.DOWN:
		button.y -= 10
	elif symbol == key.R:
		if button.hover_enlarge == 0:
			button.hover_enlarge = hover_enlarge
			print('Button enlarging added!')
		else:
			button.hover_enlarge = 0
			print('Button enlarging removed!')
	else:
		return

	print(f'New button pos: {button.pos}')

@window.event
def on_draw():
	window.clear()
	batch.draw()

button = TextButton(
	'Hi',
	'This is text!', 320, 240,
	window, batch, group,
	sheet, 0,
	('center', 'center'),
	('center', 'center'),
	font_info=('Arial', 30),
	hover_enlarge=hover_enlarge,
	on_half_click=on_half_click, on_full_click=on_full_click
)

pyglet.app.run()
