import pyglet

from main_window import MainWindow
from widgets import MainManager

window = MainWindow(1200, 1000, resizable=True)
window.set_caption('Touchy - Virtual MIDI X-Y Pad')

MainManager(window=window, is_movable=True)
pyglet.app.run()
