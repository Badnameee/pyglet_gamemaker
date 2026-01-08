from __future__ import annotations

import pyglet
from pyglet_gamemaker.sprite.sprite_sheet import SpriteSheet
from pyglet.window import Window
from pyglet.image import Animation, AnimationFrame
from pyglet.sprite import Sprite

sheet = SpriteSheet('Test Button SpriteSheet.png', 3, 1, top_down=False)
print(f'Lookup before naming: {sheet.lookup}')
sheet.name('Unpressed', 'Hover', 'Pressed')
print(f'Lookup after naming: {sheet.lookup}')
print(f'Single item: {sheet.item_dim}')
print(f'Cols: {sheet.cols}, Rows: {sheet.rows}')
print(f'Total Dim: {sheet.img.width}, {sheet.img.height}')

window = Window()

anim_sheet = SpriteSheet('Test Animation SpriteSheet.png', 3, 2)
frames = [AnimationFrame(frame, 1/12) for frame in anim_sheet.texture_grid]
anim = Animation(frames)
sprite = Sprite(anim)
sprite.scale = 15

@window.event
def on_draw():
	window.clear()
	sprite.draw()

pyglet.app.run()