import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from src.shapes import HitboxRenderCircle
from src.types import Color

window = Window(640, 480, caption=__name__)
batch = Batch()
group = Group()

circle = HitboxRenderCircle(100, 100, 50, color=Color.WHITE, batch=batch, group=group)
circle2 = HitboxRenderCircle(300, 300, 50, color=Color.RED, batch=batch, group=group)


@window.event
def on_mouse_motion(x, y, dx, dy):
	circle.pos = x, y


@window.event
def on_key_press(symbol, modifiers):

	if symbol == key.A:
		circle.anchor_x -= 10
	elif symbol == key.D:
		circle.anchor_x += 10
	elif symbol == key.W:
		circle.anchor_y += 10
	elif symbol == key.S:
		circle.anchor_y -= 10
	elif symbol == key.LEFT:
		circle.angle -= 0.1
	elif symbol == key.RIGHT:
		circle.angle += 0.1


def update(dt):
	if circle.collide(circle2)[0]:
		circle.render.opacity = 128
	else:
		circle.render.opacity = 255


@window.event
def on_draw():
	window.clear()
	batch.draw()


pyglet.clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
