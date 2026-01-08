from __future__ import annotations

import pyglet_gamemaker as pgm


class Demo(pgm.Scene):
	# Store scaled positions (x, y) relative to window size
	#   (0.5, 0.5) is center
	WIDGET_POS = {'Text': (0.5, 0.1), 'Button': (0.5, 0.4), 'TextButton': (0.5, 0.6)}

	# Set default font information here
	default_font_info = None, 40

	def create_widgets(self):
		# Create a sprite sheet with image assets
		#   This image, found in /test, has 3 images (bottom to top):
		#   Unpressed, Hover, and Pressed
		self.sheet = pgm.sprite_sheet.SpriteSheet(
			'test/Test Button SpriteSheet.png', 3, 1
		)

		# Create a solid background with the given color
		self.create_bg(pgm.types.Color.RED)

		# Create separate text and button
		self.create_text(
			'Text', 'Test', ('center', 'center'), color=pgm.types.Color.BLACK
		)
		self.create_button(
			'Button',
			self.sheet,
			0,
			('center', 'center'),
			on_half_click=self.on_half_click,
			on_full_click=self.on_full_click,
		)

		# A textbutton combines text and a button
		#   Hover enlarge makes text larger when hovering
		#   Works well with using larger hover sprite for button
		self.create_text_button(
			'TextButton',
			'Text',
			self.sheet,
			0,
			('center', 'center'),
			('center', 'center'),
			hover_enlarge=5,
			on_half_click=self.on_half_click,
			on_full_click=self.on_full_click,
		)

	def on_half_click(self, button):
		print(f'{button.ID} pressed down!')

	def on_full_click(self, button):
		print(f'{button.ID} fully pressed and released!')

	def enable(self):
		# Enable all widgets
		for widget in self.widgets.values():
			widget.enable()

	def disable(self):
		# Disable all widgets
		for widget in self.widgets.values():
			widget.enable()


demo = Demo('Demo')
game = pgm.Window((640, 480))
game.add_scene('Demo', demo)
game.run()
