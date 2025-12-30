# 📦 pyglet-gamemaker

<!-- (add your badges here) -->
[![PyPI version](https://badge.fury.io/py/pyglet-gamemaker.svg)](https://badge.fury.io/py/pyglet-gamemaker)

<!-- > *Your documentation is a direct reflection of your software, so hold it to the same standards.* -->


## ℹ️ Overview

<!-- A paragraph explaining your work, who you are, and why you made it. -->

**pyglet-gamemaker** is an extension of Pyglet that simplifies the process of making games! This project began when I became frustrated at the boilerplate I had to write all the time, and I wanted a cleaner system to quickly add features.


## 🌟 Features

- Hitboxes
  - Fully working convex polygon collision
  - Includes circles
- Spritesheets:
  - Automatically loaded
  - Labelable to allow for indexing by string
- Widgets:
  - Dynamic anchoring for changing size
  - Uses spritesheets instead of individual images
- Scenes:
  - Enabling and disabling handled automatically
  - Menus:
    - Easily create visuals + widgets
    - Widget positions relative to window size
- Main Window class handles switching of scenes

### ✍️ Authors

I'm [Steven Robles](https://github.com/Badnameee) and I am a high school student with a *small?* passion for making games.


## 🚀 Usage

<!-- *Show off what your software looks like in action! Try to limit it to one-liners if possible and don't delve into API specifics.* -->

A simple program to render an empty Menu with button detection:
```py
>>> import pyglet_gamemaker as pgm
>>> from pyglet_gamemaker.types import Color
>>> 
>>> 
>>> class Menu(pgm.Menu):
>>>     # Create widgets here
>>>     def create_widgets(self): ...
>>>     # Code that runs when button is pressed down
>>>     def on_half_click(self, button): ...
>>>     # Code that runs when button is fully clicked and released
>>>     def on_full_click(self, button): ...
>>>     # Code that runs when scene is enabled
>>>     def enable(self): ...
>>>     # Code that runs when scene is disabled
>>>     def disable(self): ...
>>> 
>>> 
>>> scene = Menu('Test')
>>> game = pgm.Window((640, 480))
>>> game.add_scene('Test', scene)
>>> game.run()
```

Creating a spritesheet
```py
>>> # Create a sprite sheet with image assets
>>> #   This image, found in /test, has 3 images (bottom to top):
>>> #   Unpressed, Hover, and Pressed
>>> self.sheet = pgm.sprite.SpriteSheet('test/Default Button.png', rows=3, cols=1)
```

The following should go in `Menu.create_widgets()`:

- Creating text
```py
>>> self.create_text(
>>>     'Text', 'Test',
>>>     ('center', 'center'), color=pgm.types.Color.BLACK
>>> )
```

- Creating a button
```py
>>> self.create_button(
>>>     'Button', self.sheet, 0,
>>>     ('center', 'center'),
>>>     # Event handlers defined in empty Menu class above
>>>     on_half_click=self.on_half_click, on_full_click=self.on_full_click
>>> )
```

- Creating a text and button in one
```py
>>> # A textbutton combines text and a button
>>> #   Hover enlarge makes text larger when hovering
>>> #   Works well with using larger hover sprite for button
>>> self.create_text_button(
>>>     'TextButton', 'Text',
>>>     self.sheet, 0,
>>>     ('center', 'center'), ('center', 'center'),
>>>     # Event handlers defined in empty Menu class above
>>>     on_half_click=self.on_half_click, on_full_click=self.on_full_click
>>> )
```

<img src="/media/demo.gif" width="50%" height="50%"/>


## ⬇️ Installation

Simple, understandable installation instructions!

```bash
pip install pyglet-gamemaker
```

<!-- And be sure to specify any other minimum requirements like Python versions or operating systems. -->
Works in Python >=3.10

<!-- *You may be inclined to add development instructions here, don't.* -->


## 💭 Feedback and Contributing

<!--Add a link to the Discussions tab in your repo and invite users to open issues for bugs/feature requests. -->

To request features or report bugs, open an issue [here](https://github.com/Badnameee/pyglet-gamemaker/issues).

[Contact me directly](mailto:stevenrrobles13@gmail.com)

<!-- This is also a great place to invite others to contribute in any ways that make sense for your project. Point people to your DEVELOPMENT and/or CONTRIBUTING guides if you have them. -->