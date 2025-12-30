# 📦 pyglet-gamemaker

<!-- (add your badges here) -->

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
  - Menus: Easily create visuals + widgets
- Main Window class handles switching of scenes

### ✍️ Authors

I'm [Steven Robles](https://github.com/Badnameee) and I am a high school student with a *small?* passion for making games.


## 🚀 Usage

<!-- *Show off what your software looks like in action! Try to limit it to one-liners if possible and don't delve into API specifics.* -->

A simple program to render an empty Menu:
```py
>>> import pyglet_gamemaker as pgm
>>> from pyglet_gamemaker.types import Color
>>> 
>>> 
>>> class Menu(pgm.Menu):
>>>     # Create widgets here
>>>     def create_widgets(self): ...
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

Example Menu showing all features
```py
>>> import pyglet_gamemaker as pgm
>>> from pyglet_gamemaker.types import Color
>>> 
>>> 
>>> class Menu(pgm.Menu):
>>>     # Store scaled positions (x, y) relative to window size
>>>     #   (0.5, 0.5) is center
>>>     WIDGET_POS = {
>>>         'Text': (0.25, 0.25),
>>>         'Button': (0.5, 0.5),
>>>         'TextButton': (0.65, 0.65)
>>>     }
>>> 
>>>     # Set default font information here
>>>     default_font_info = None, 40
>>>     
>>>     def create_widgets(self):
>>>         
>>>         # Create a sprite sheet with image assets
>>>         #   This image, found in /test, has 3 images (bottom to top):
>>>         #   Unpressed, Hover, and Pressed
>>>         self.sheet = pgm.sprite.SpriteSheet('test/Default Button.png', 3, 1)
>>>         
>>>         # Create a solid background with the given color
>>>         self.create_bg(Color.RED)
>>> 
>>>         # Create separate text and button
>>>         self.create_text(
>>>             'Text', 'Test',
>>>             ('center', 'center'), color=Color.BLACK
>>>         )
>>>         self.create_button(
>>>             'Button', self.sheet, 0,
>>>             ('center', 'center'),
>>>             # In this test, we don't need to monitor button status
>>>             dispatch=False
>>>         )
>>> 
>>>         # A textbutton combines text and a button
>>>         #   Hover enlarge makes text larger when hovering
>>>         #   Works well with using larger hover sprite for button
>>>         self.create_text_button(
>>>             'TextButton', 'Text',
>>>             self.sheet, 0,
>>>             ('center', 'center'), ('center', 'center'),
>>>             hover_enlarge=5,
>>>             # In this test, we don't need to monitor button status
>>>             dispatch=False
>>>         )
>>>     
>>>     def enable(self):
>>>         # Enable all widgets
>>>         for widget in self.widgets.values():
>>>             widget.enable()
>>> 
>>>     def disable(self):
>>>         # Disable all widgets
>>>         for widget in self.widgets.values():
>>>             widget.enable()
```


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