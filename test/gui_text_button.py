import random

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from src.gui import TextButton
from src.sprite import SpriteSheet

window = Window(640, 480, caption=__name__)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = Batch()
txt_group = Group()
button_group = Group()
UI_group = Group()

sheet = SpriteSheet('Default Button.png', 3, 1)
sheet.name('Unpressed', 'Hover', 'Pressed')


def on_half_click(button):
	print(f'{button} pressed down on!')


def on_full_click(button):
	print(f'{button} fully pressed and releaased!')


@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.A:
		button.x -= 10
	elif symbol == key.D:
		button.x += 10
	elif symbol == key.W:
		button.y += 10
	elif symbol == key.S:
		button.y -= 10
	elif symbol == key.LEFT:
		button.anchor_x -= 10
	elif symbol == key.RIGHT:
		button.anchor_x += 10
	elif symbol == key.UP:
		button.anchor_y += 10
	elif symbol == key.DOWN:
		button.anchor_y -= 10
	elif symbol == key.R:
		button.hover_enlarge = random.randint(0, 25)
		print(f'Button enlarge changed to {button.hover_enlarge}')
	else:
		return

	print(f'New button pos: {button.pos}')
	button_anchor.position = button.pos


@window.event
def on_draw():
	window.clear()
	batch.draw()


button = TextButton(
	'Hi',
	'This is text!',
	320,
	240,
	window,
	batch,
	button_group,
	txt_group,
	sheet,
	0,
	('center', 'center'),
	('center', 'center'),
	font_info=('Arial', 30),
	on_half_click=on_half_click,
	on_full_click=on_full_click,
)
button_anchor = Circle(
	*button.pos, 10, color=(0, 255, 255), batch=batch, group=UI_group
)

pyglet.app.run()
