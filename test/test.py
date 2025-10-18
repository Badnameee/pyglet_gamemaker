# type: ignore

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from src.gui import Button
from src.sprite import SpriteSheet

window = Window(640, 480)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = Batch()
group = Group()

pyglet.resource.path = ['test']
pyglet.resource.reindex()

sheet = SpriteSheet('Default Button.png', 3, 1)
sheet.name('Unpressed', 'Hover', 'Pressed')

def on_half_click(button):
	print(f'{button} pressed down on!')
def on_full_click(button):
	print(f'{button} fully pressed and releaased!')

@window.event
def on_key_press(symbol: int, modifiers: int):
	if symbol == key.LEFT:
		button.x -= 10
	elif symbol == key.RIGHT:
		button.x += 10
	elif symbol == key.DOWN:
		button.y -= 10
	elif symbol == key.UP:
		button.y += 10
	else:
		return

	print(f'New button pos: {button.pos}')

@window.event
def on_draw():
	window.clear()
	batch.draw()

button = Button(
	'Hi', 320, 240, ('center', 'center'),
	sheet, window, batch, group,
	on_half_click=on_half_click, on_full_click=on_full_click
)

pyglet.app.run()
