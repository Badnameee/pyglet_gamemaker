# Holds all imports for tests
tests = [
	'gui_button',
	'gui_text',
	'gui_text_button',
	'sprite_spritesheet',
	'shapes_hitbox',
	'shapes_rect',
]

for test_num, test in enumerate(tests, 1):
	print(
		'\n'
		'-----------------------------'
		'\n'
		f'Starting test #{test_num}'
		'\n'
		'\n'
	)
	exec(f'import test.{test}') # Run actual test
