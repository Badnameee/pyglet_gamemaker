# mypy: disable-error-code="index"

"""Module holding Animation class.

Use `~pgm.sprite.Animation` instead of `~pgm.sprite.animation.Animation`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.image.animation import Animation as _Animation
from pyglet.image.animation import AnimationFrame as _AnimationFrame

from .sprite_sheet import SpriteSheet

if TYPE_CHECKING:
	from typing import Self

	from pyglet.image import AbstractImage


class Animation(_Animation):
	"""Stores an single Animation from frames.

	Can be initialized from:
	- Raw frames `.__init__()`
	- A file path and extra arguments `.from_file()`

	Each frame is an instance of `~pgm.sprite.animation.AnimationFrame` with:
	- an image
	- a duration
	- an optional frame number for sorting

	Setting a duration to `None` will prevent the animation from passing that frame.
	"""

	sprite_sheet: SpriteSheet | None = None
	"""The spritesheet"""

	def __init__(self, frames: list[AnimationFrame], loop: bool = False) -> None:
		"""Create an animation from animation frames.

		Args:
			frames (list[AnimationFrame]):
				The list of frames for the animation
			loop (bool, optional):
				If True, loop the animation.
				Defaults to False.
		"""
		if not loop:
			frames[-1].duration = None
		super().__init__(frames)  # type: ignore[arg-type]

	@classmethod
	def from_file(
		cls,
		file_path: str,
		rows: int,
		cols: int,
		frame_duration: float,
		row_padding: int = 0,
		col_padding: int = 0,
		top_down: bool = True,
		loop: bool = False,
		atlas: bool = True,
	) -> Self:
		"""Create an Animation from a file path.

		Args:
			file_path (str):
				The path to the sprite sheet
			rows (int):
				The number of rows for sprites
			cols (int):
				The number of columns for sprites
			frame_duration (float):
				The duration of each frame in the animation.
			row_padding (int, optional):
				The amount to pad between rows of sprites. Does not include edge of sheet.
				Defaults to 0.
			col_padding (int, optional):
				The amount to pad between columns of sprites. Does not include edge of sheet.
				Defaults to 0.
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
			loop (bool, optional):
				If True, have animation loop when using `~pyglet.sprite.Sprite`.
				Defaults to False.
			atlas (bool, optional):
				If True, spritesheet is stored in a global atlas. False if not.
				See `~pgm.sprite.SpriteSheet` for more info.
				Defaults to True.
		"""
		sprite_sheet = SpriteSheet(
			file_path, rows, cols, row_padding, col_padding, top_down, atlas=atlas
		)

		# Copied from pyglet.image.animation.Animation.from_image_sequence as cls() call errors
		frames = [
			AnimationFrame(image, frame_duration) for image in sprite_sheet.image_grid
		]

		self = cls(frames, loop)
		self.sprite_sheet = sprite_sheet
		return self


class AnimationFrame(_AnimationFrame):
	"""A single frame of an animation.

	A frame contains:
	- an image
	- a duration
	- an optional frame number for sorting the frames

	< and > methods can be used to sort the frames is necessary.
	"""

	frame_num: int | None

	def __init__(
		self, image: AbstractImage, duration: float | None, frame_num: int | None = None
	) -> None:
		"""Create an animation frame.

		Args:
			image (AbstractImage):
				The image to display
			duration (float | None):
				The duration of the frame
			frame_num (int | None, optional):
				The frame number in the animation.
				Defaults to None.
		"""
		super().__init__(image, duration)
		self.frame_num = frame_num

	def __lt__(self, other: AnimationFrame) -> bool:
		"""Shorthand for comparing frame num. Always returns False if frame num is not set."""
		return (
			self.frame_num is not None
			and other.frame_num is not None
			and self.frame_num < other.frame_num
		)

	def __gt__(self, other: AnimationFrame) -> bool:
		"""Shorthand for comparing frame num. Always returns False if frame num is not set."""
		return (
			self.frame_num is not None
			and other.frame_num is not None
			and self.frame_num > other.frame_num
		)

	def __repr__(self) -> str:
		"""Show variables in frame."""
		if self.frame_num:
			return f'AnimationFrame({self.image}, duration={self.duration}, frame={self.frame_num})'
		return f'AnimationFrame({self.image}, duration={self.duration})'


class AnimationList:
	"""Stores a sequence of animations created by a single spritesheet.

	This is achieved using a `.yaml` file with the same name as the spritesheet.

	The created animations will be available through the `.animations` dictionary using unaliased name.

	All config settings:
	- `rows:` - Number of sprite rows in spritesheet
	- `cols:` - Number of sprite columns in spritesheet
	- `row-padding:` - Pixels of padding between sprite rows (not including origin side, ex. top-down means not including top-most side)
	- `col-padding:` - Pixels of padding between sprite columns (not including left-most side)
	- `top-down:` - If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.

	- `Delimiter`: - The character that goes between animation name-alias and frame number
	- `void:` - The character denoting no sprite. Can = delimiter.

	- `anim-data:` - A dictionary containing the data for each animation
		- `{name}:` - Each nested key will be the alias name
			- `name:` - The unaliased name in order to search in dictionary after creating animation
			- `fps:` - Frames per second of the animation
			- `loop:` - If True, loop the animation

	- `data:` - A 2d list containing the data for each row
		- `- [C_1, C_2, ...]` - Each row contains a list in the format {alias}{delimiter}{frame-num} or {void}

	An example .yaml file (can be found in `test/media/` folder in github repository)
	```
	rows: 4
	cols: 4
	row-padding: 0
	col-padding: 0
	top-down: True

	delimiter: _
	void: _

	anim-data:
	  C:
	    name: Circle
	    fps: 10
	    loop: True
	  R:
	    name: Rectangle
	    fps: 8
	    loop: True

	data:
	  - [C_1, C_2, C_3, C_4]
	  - [C_5, C_6, C_7, C_8]
	  - [C_9, C_10, R_1, R_2]
	  - [R_3, R_4, _, _]
	```
	"""

	animations: dict[str, Animation]
	"""All the animations from the spritesheet"""
	all_frames: dict[str, list[AnimationFrame]]
	"""All the frames. Get frames using alias."""

	def __init__(
		self,
		file_path: str,
		top_down: bool = True,
		atlas: bool = True,
	) -> None:
		"""Create an animation list.

		Args:
			file_path (str):
				The path to the spritesheet. Must be relative to cwd or be absolute.
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
			atlas (bool, optional):
				If True, add spritesheet to atlas for more efficient rendering but less fine control.
				Ex. Cannot set texture parameters without setting for entire atlas.
				If False, create separate texture. Slower but allows for more customization.
				Defaults to True.
		"""
		self.sprite_sheet = SpriteSheet.from_yaml(
			file_path,
			top_down,
			atlas,
		)

		# Parse .yaml frames
		self.all_frames = {}
		for row in self.sprite_sheet.yaml['data']:
			for name in row:
				# Void, no frame
				if name == self.sprite_sheet.yaml['void']:
					continue

				alias, _, frame_num = name.partition(
					self.sprite_sheet.yaml['delimiter']
				)
				self.all_frames.setdefault(alias, [])
				self.all_frames[alias].append(
					AnimationFrame(
						self.sprite_sheet[name],
						1 / self.sprite_sheet.yaml['anim-data'][alias]['fps'],
						int(frame_num),
					)
				)

		# Sort possible unsorted .yaml frames
		for frames in self.all_frames.values():
			frames.sort()

		# Create animations
		self.animations = {}
		for alias, frames in self.all_frames.items():
			self.animations[self.sprite_sheet.yaml['anim-data'][alias]['name']] = (
				Animation(
					frames,
					self.sprite_sheet.yaml['anim-data'][alias]['loop'],
				)
			)
