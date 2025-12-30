import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from src.shapes import HitboxRender, HitboxRenderCircle
from src.types import Color

window = Window(640, 480, caption=__name__)
batch = Batch()
group = Group()

hitbox = HitboxRender.from_rect(100, 100, 100, 50, Color.WHITE, batch, group)
hitbox2 = HitboxRender.from_rect(300, 300, 100, 50, Color.RED, batch, group)
circle = HitboxRenderCircle(100, 100, 50, color=Color.WHITE, batch=batch, group=group)
circle.render.visible = False

mode = 'rect'


@window.event
def on_mouse_motion(x, y, dx, dy):
	hitbox.pos = x, y
	circle.pos = x, y


@window.event
def on_key_press(symbol, modifiers):
	global mode

	if symbol == key.A:
		hitbox.anchor_x -= 10
		circle.anchor_x -= 10
	elif symbol == key.D:
		hitbox.anchor_x += 10
		circle.anchor_x += 10
	elif symbol == key.W:
		hitbox.anchor_y += 10
		circle.anchor_y += 10
	elif symbol == key.S:
		hitbox.anchor_y -= 10
		circle.anchor_y -= 10
	elif symbol == key.LEFT:
		hitbox.angle -= 0.1
		circle.angle -= 0.1
	elif symbol == key.RIGHT:
		hitbox.angle += 0.1
		circle.angle += 0.1

	if symbol == key.C:
		mode = 'circle' if mode == 'rect' else 'rect'
		if mode == 'rect':
			hitbox.render.visible = True
			circle.render.visible = False
		elif mode == 'circle':
			hitbox.render.visible = False
			circle.render.visible = True


def update(dt):
	if mode == 'rect':
		if hitbox.collide(hitbox2)[0]:
			hitbox.render.opacity = 128
		else:
			hitbox.render.opacity = 255
	elif mode == 'circle':
		if hitbox2.collide(circle)[0]:
			circle.render.opacity = 128
		else:
			circle.render.opacity = 255


@window.event
def on_draw():
	window.clear()
	batch.draw()


pyglet.clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
