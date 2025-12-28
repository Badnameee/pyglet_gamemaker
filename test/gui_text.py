import string
import random

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from src.gui import Text

window = Window(640, 480, caption=__name__)
batch = Batch()
txt_group = Group()
UI_group = Group(1)


@window.event
def on_mouse_motion(x, y, dx, dy):
	# txt.pos = x, y
	txt.offset((dx, dy))
	txt_anchor.position = txt.pos
	print(f'New txt pos: {txt.pos}')


@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.LEFT:
		txt.anchor_x -= 10
	elif symbol == key.RIGHT:
		txt.anchor_x += 10
	elif symbol == key.UP:
		txt.anchor_y += 10
	elif symbol == key.DOWN:
		txt.anchor_y -= 10
	elif symbol == key.A:
		txt.rotation -= 10
	elif symbol == key.D:
		txt.rotation += 10
	elif symbol == key.R:
		txt.reset()
		txt.text = 'Hello World'
	elif symbol == key.P:
		txt.text += random.choice(string.ascii_lowercase)
	elif symbol == key.O:
		txt.text = txt.text[:-1]
	else:
		return

	print(f'New txt pos: {txt.pos}')
	print(f'New txt font: {txt.font_info}')
	txt_anchor.position = txt.pos


@window.event
def on_draw():
	window.clear()
	batch.draw()


txt = Text('Hello World', 0, 0, batch, txt_group, ('center', 'center'), ('Arial', 50))
txt.start_pos = 320, 240
txt_anchor = Circle(*txt.pos, 10, color=(0, 255, 255), batch=batch, group=UI_group)

pyglet.app.run()
