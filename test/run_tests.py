from __future__ import annotations

import os


def clear_terminal() -> None:
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')


# Holds all imports for tests
tests = [
	'sprite',
	'gui_button',
	'gui_text',
	'gui_text_button',
	'shapes_hitbox',
	'shapes_rect',
	'shapes_circle',
	'scene',
	'window',
]

clear_terminal()
for test_num, test in enumerate(tests, 1):
	print(f'\n-----------------------------\nStarting test #{test_num}: "{test}"\n\n')
	exec(f'import test.{test}')  # Run actual test
