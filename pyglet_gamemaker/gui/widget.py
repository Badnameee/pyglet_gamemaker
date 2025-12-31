from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import Anchor, AnchorX, AnchorY, Point2D


class Widget(ABC):
	CONVERT_DYNAMIC: dict[AnchorX | AnchorY, float] = {
		'left': 0,
		'bottom': 0,
		'center': 0.5,
		'right': 1,
		'top': 1,
	}
	"""Converts dynamic anchor to multiplier"""

	_anchor: Point2D = 0, 0
	"""Internally holds anchor offset of widget"""

	raw_anchor: Anchor = 0, 0
	"""Holds the raw anchor position (static + dynamic) of widget"""
	start_pos: Point2D = 0, 0
	"""Original (*unanchored* AND *unrotated*) position of widget"""
	start_anchor: Anchor = 0, 0
	"""Original anchor offset of widget"""
	dispatch: bool = True
	"""If False, don't dispatch events to handlers"""
	attach_events: bool = True
	"""If False, don't attach events to window"""

	def offset(self, val: Point2D) -> None:  # noqa: D102
		"""Add offset to widget."""
		self.x += val[0]
		self.y += val[1]

	def set_offset(self, val: Point2D) -> None:  # noqa: D102
		"""Set the offset of widget."""
		self.pos = self.start_pos[0] + val[0], self.start_pos[1] + val[1]

	def reset(self) -> None:  # noqa: D102
		"""Reset widget to initial state."""
		self.pos = self.start_pos
		self.anchor = self.start_anchor

	@abstractmethod
	def _calc_anchor(self) -> None:
		"""Calculate new anchor and sync position."""

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_press() method.'
		)

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_release() method.'
		)

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_motion() method.'
		)

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> None:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_drag() method.'
		)

	@abstractmethod
	def enable(self) -> None:
		"""Enable widget."""

	@abstractmethod
	def disable(self) -> None:
		"""Disable widget."""

	@property
	@abstractmethod
	def x(self) -> float:
		"""X of widget's anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""

	@x.setter
	@abstractmethod
	def x(self, val: float) -> None: ...

	@property
	@abstractmethod
	def y(self) -> float:
		"""Y of widget's anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""

	@y.setter
	@abstractmethod
	def y(self, val: float) -> None: ...

	@property
	@abstractmethod
	def pos(self) -> Point2D:
		"""Widget's anchor point."""

	@pos.setter
	@abstractmethod
	def pos(self, val: Point2D) -> None: ...

	@property
	@abstractmethod
	def anchor_x(self) -> float:
		"""X position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""

	@anchor_x.setter
	@abstractmethod
	def anchor_x(self, val: float) -> None: ...

	@property
	@abstractmethod
	def anchor_y(self) -> float:
		"""Y position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""

	@anchor_y.setter
	@abstractmethod
	def anchor_y(self, val: float) -> None: ...

	@property
	@abstractmethod
	def anchor(self) -> Point2D:
		"""Widget anchor offset.

		Can be set in px or dynamic.
		"""

	@anchor.setter
	@abstractmethod
	def anchor(self, val: Anchor) -> None: ...

	@property
	@abstractmethod
	def width(self) -> int | float:
		"""Width of widget."""

	@property
	@abstractmethod
	def height(self) -> int | float:
		"""Height of widget."""
