# type: ignore

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group

from src.shapes import HitboxRender
from src.types import Color

window = Window(640, 480)
batch = Batch()
group = Group(0)

hitbox = HitboxRender(HitboxRender.from_rect(100, 100, 100, 50), Color.WHITE, batch, group)
hitbox2 = HitboxRender(HitboxRender.from_rect(300, 300, 100, 50), Color.RED, batch, group)

@window.event
def on_mouse_motion(x, y, dx, dy):
	hitbox.move_to(x, y)

@window.event
def on_key_press(symbol, modifiers):

	if symbol == key.A:
		hitbox.anchor_x += 10
	elif symbol == key.D:
		hitbox.anchor_x -= 10
	elif symbol == key.W:
		hitbox.anchor_y -= 10
	elif symbol == key.S:
		hitbox.anchor_y += 10
	elif symbol == key.LEFT:
		hitbox.angle -= 0.1
	elif symbol == key.RIGHT:
		hitbox.angle += 0.1

def update(dt):
	if hitbox.collide(hitbox2)[0]:
		hitbox.render.opacity = 128
	else:
		hitbox.render.opacity = 255

@window.event
def on_draw():
	window.clear()
	batch.draw()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()