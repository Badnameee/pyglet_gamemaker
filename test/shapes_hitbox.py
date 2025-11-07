# type: ignore

import math

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from src.shapes import HitboxRender
from src.types import Color

window = Window(640, 480)
batch = Batch()
group = Group()

hitbox = HitboxRender.from_rect(100, 100, 100, 50, Color.WHITE, batch, group)
hitbox2 = HitboxRender.from_rect(300, 300, 100, 50, Color.RED, batch, group)
circle = Circle(100, 100, 50, color=Color.WHITE.value, batch=batch, group=group)
circle.visible = False

mode = 'rect'

@window.event
def on_mouse_motion(x, y, dx, dy):
	if mode == 'rect':
		hitbox.move_to(x, y)
	elif mode == 'circle':
		circle.position = x, y

@window.event
def on_key_press(symbol, modifiers):
	global mode

	if mode == 'rect':
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
	elif mode == 'circle':
		if symbol == key.A:
			circle.anchor_x += 10
		elif symbol == key.D:
			circle.anchor_x -= 10
		elif symbol == key.W:
			circle.anchor_y -= 10
		elif symbol == key.S:
			circle.anchor_y += 10
		elif symbol == key.LEFT:
			circle.rotation -= 0.1 * 180 / math.pi
		elif symbol == key.RIGHT:
			circle.rotation += 0.1 * 180 / math.pi

	if symbol == key.C:
		mode = 'circle' if mode == 'rect' else 'rect'
		if mode == 'rect':
			hitbox.render.visible = True
			circle.visible = False
		elif mode == 'circle':
			hitbox.render.visible = False
			circle.visible = True

def update(dt):
	if mode == 'rect':
		if hitbox.collide(hitbox2)[0]:
			hitbox.render.opacity = 128
		else:
			hitbox.render.opacity = 255
	elif mode == 'circle':
		if HitboxRender.circle_collide(circle, hitbox2)[0]:
			circle.opacity = 128
		else:
			circle.opacity = 255

@window.event
def on_draw():
	window.clear()
	batch.draw()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()