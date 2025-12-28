import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from src.shapes import Rect, HitboxRender
from src.types import Color

window = Window(640, 480, caption=__name__)
batch = Batch()
group = Group()

rect = Rect(100, 100, 100, 50, Color.WHITE, batch, group)
hitbox2 = HitboxRender.from_rect(300, 300, 100, 50, Color.RED, batch, group)


@window.event
def on_mouse_motion(x, y, dx, dy):
	rect.pos = x, y


@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.A:
		rect.anchor_x -= 10
	elif symbol == key.D:
		rect.anchor_x += 10
	elif symbol == key.W:
		rect.anchor_y += 10
	elif symbol == key.S:
		rect.anchor_y -= 10
	elif symbol == key.LEFT:
		rect.angle -= 0.1
	elif symbol == key.RIGHT:
		rect.angle += 0.1

	elif symbol == key.J:
		rect.width -= 10
	elif symbol == key.L:
		rect.width += 10
	elif symbol == key.I:
		rect.height += 10
	elif symbol == key.K:
		rect.height -= 10


def update(dt):
	if rect.collide(hitbox2)[0]:
		rect.render.opacity = 128
	else:
		rect.render.opacity = 255


@window.event
def on_draw():
	window.clear()
	batch.draw()


pyglet.clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
