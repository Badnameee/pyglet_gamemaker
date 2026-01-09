from __future__ import annotations

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random

import pyglet
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from pyglet.window import Window, key

from pyglet_gamemaker.gui import TextButton
from pyglet_gamemaker.sprite.sprite_sheet import SpriteSheet

pyglet.resource.path.append('..')
pyglet.resource.reindex()

window = Window(640, 480, caption=__name__)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = Batch()
txt_group = Group()
button_group = Group()
UI_group = Group()

sheet = SpriteSheet('test/media/Button SpriteSheet.png', 3, 1)
sheet.name('Unpressed', 'Hover', 'Pressed')


def on_half_click(button):
	print(f'{button.ID} pressed down on!')


def on_full_click(button):
	print(f'{button.ID} fully pressed and releaased!')


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
		button.reset()
	elif symbol == key.T:
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
