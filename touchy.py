import pyglet

from widgets import MainManager

window = pyglet.window.Window(1200, 1000, resizable=True)
window.set_caption('Touchy - Virtual MIDI X-Y Pad')
MainManager(window=window, is_movable=True)
pyglet.app.run()
