import pyglet

# Holds all imports for tests
tests = [
	'sprite_spritesheet',
	'gui_button',
	'gui_text',
	'gui_text_button',
	'shapes_hitbox',
	'shapes_rect',
	'shapes_circle',
	'menu',
	'window',
]

pyglet.resource.path = ['test']
pyglet.resource.reindex()

for test_num, test in enumerate(tests, 1):
	print(f'\n-----------------------------\nStarting test #{test_num}: "{test}"\n\n')
	exec(f'import test.{test}')  # Run actual test
