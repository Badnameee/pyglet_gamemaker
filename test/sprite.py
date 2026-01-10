from __future__ import annotations

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pyglet
from pyglet.gl import *
from pyglet.graphics import Batch
from pyglet.image.animation import Animation as PygletAnimation
from pyglet.image.animation import AnimationFrame as PygletAnimationFrame
from pyglet.sprite import Sprite
from pyglet.window import Window

from pyglet_gamemaker.sprite.animation import Animation, AnimationList
from pyglet_gamemaker.sprite.sprite_sheet import SpriteSheet

pyglet.resource.path.append('..')
pyglet.resource.reindex()

#######################
# Testing SpriteSheet #
#######################

sheet = SpriteSheet(
	'test/media/Button SpriteSheet.png', 3, 1, top_down=False, atlas=False
)
print(f'Lookup before naming: {sheet.lookup}')
sheet.name('Unpressed', 'Hover', 'Pressed')
print(f'Lookup after naming: {sheet.lookup}')
print(f'Single item: {sheet.item_dim}')
print(f'Cols: {sheet.cols}, Rows: {sheet.rows}')
print(f'Total Dim: {sheet.img.width}, {sheet.img.height}')
print()

######################
# Testing Animations #
######################

window = Window()
batch = Batch()
glClearColor(0, 1, 0, 1)

anim_sheet = SpriteSheet('test/media/SpriteSheet.png', 3, 2, atlas=False)
frames = [PygletAnimationFrame(frame, 1 / 12) for frame in anim_sheet.image_grid]
anim = PygletAnimation(frames)
sprite = Sprite(anim, batch=batch)
sprite.scale = 10

anim2 = Animation.from_file(
	'test/media/Button SpriteSheet.png', 3, 1, 1 / 3, loop=True, atlas=False
)
sprite2 = Sprite(anim2, 0, sprite.height, batch=batch)
sprite2.scale = 10

anim3 = AnimationList(
	'test/media/AnimationList.png',
	atlas=False,
)
sprite_3s = []
x = sprite.width
for anim in anim3.animations.values():
	sprite_3s.append(Sprite(anim, x, 100, batch=batch))
	sprite_3s[-1].scale = 10
	x += sprite_3s[-1].width

# Alias images
glBindTexture(GL_TEXTURE_2D, 1)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glBindTexture(GL_TEXTURE_2D, 2)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glBindTexture(GL_TEXTURE_2D, 3)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glBindTexture(GL_TEXTURE_2D, 0)


@window.event
def on_draw():
	window.clear()
	batch.draw()


pyglet.app.run()
