import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from src.gui import Button
from src.sprite import SpriteSheet

window = Window(640, 480, caption=__name__)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = Batch()
button_group = Group()
UI_group = Group(1)

sheet = SpriteSheet('Default Button.png', 3, 1)
sheet.name('Unpressed', 'Hover', 'Pressed')


def on_half_click(button):
	print(f'{button} pressed down on!')


def on_full_click(button):
	print(f'{button} fully pressed and releaased!')


@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.A:
		button.offset((-10, 0))
	elif symbol == key.D:
		button.offset((10, 0))
	elif symbol == key.W:
		button.offset((0, 10))
	elif symbol == key.S:
		button.offset((0, -10))
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
	else:
		return

	print(f'New button pos: {button.pos}')
	button_anchor.position = button.pos


@window.event
def on_draw():
	window.clear()
	batch.draw()


button = Button(
	'Hi',
	320,
	240,
	sheet,
	0,
	window,
	batch,
	button_group,
	('center', 'center'),
	on_half_click=on_half_click,
	on_full_click=on_full_click,
)
button_anchor = Circle(
	*button.pos, 10, color=(0, 255, 255), batch=batch, group=UI_group
)

pyglet.app.run()
