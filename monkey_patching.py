import ctypes

import pyglet
from pyglet.input.wintab import WintabTabletCanvas
from pyglet_gui.constants import ANCHOR_TOP_LEFT, VALIGN_TOP
from pyglet_gui.containers import VerticalContainer, HorizontalContainer, Container
from pyglet_gui.controllers import Selector
from pyglet_gui.gui import Frame, Label
from pyglet_gui.manager import Manager as Manager
from pyglet_gui.option_selectors import OptionButton
from pyglet.libs.win32 import libwintab as wintab
from pyglet_gui.scrollable import Scrollable
from pyglet_gui.sliders import Slider
from pyglet_gui.option_selectors import Dropdown as _Dropdown
from pyglet_gui.text_input import TextInput as _TextInput
from pyglet_gui.buttons import Button, OneTimeButton, Checkbox

lib = wintab.lib


def monkey_patching_OptionButton_on_mouse_press(self, x, y, button, modifiers):
    self.select()
    return True


OptionButton.on_mouse_press = monkey_patching_OptionButton_on_mouse_press


@pyglet.window.win32.Win32EventHandler(0)
def monkey_patching_WintabTabletCanvas_event_wt_packet(self, msg, wParam, lParam):
    if lParam != self._context:
        return
    
    packet = wintab.PACKET()
    if lib.WTPacket(self._context, wParam, ctypes.byref(packet)) == 0:
        return
    
    if not packet.pkChanged:
        return
    
    window_x, window_y = self.window.get_location() # TODO cache on window
    window_y = self.window.screen.height - window_y - self.window.height
    x = packet.pkX - window_x
    y = packet.pkY - window_y
    pressure = (packet.pkNormalPressure + self._pressure_bias) * \
               self._pressure_scale
    
    if self._current_cursor is None:
        self._set_current_cursor(packet.pkCursor)
    
    buttons = packet.pkButtons
    self.dispatch_event('on_motion', self._current_cursor,
                        x, y, pressure, buttons)


WintabTabletCanvas._event_wt_packet = monkey_patching_WintabTabletCanvas_event_wt_packet


def monkey_patching_Slider_set_value(self, value):
    if self._min_value <= value <= self._max_value:
        super(Slider, self).set_value(value)
        self.layout()


Slider.set_value = monkey_patching_Slider_set_value


class Dropdown(_Dropdown):
    def __init__(self, options, labels=None, max_height=400, align=VALIGN_TOP, on_select=None):
        if options and len(options):
            Selector.__init__(self, options, labels, on_select=on_select, selected=options[0])
        else:
            self._options = []
            self._selected = None
        OneTimeButton.__init__(self)

        self.max_height = max_height
        self.align = align

        self._pulldown_menu = None
        
    def load_graphics(self):
        if self._selected:
            self.label = self._options[self._selected].label
        else:
            self.label = ''
        OneTimeButton.load_graphics(self)
    
    def on_gain_highlight(self):
        self._delete_pulldown_menu()
    
    def on_lose_highlight(self):
        self._delete_pulldown_menu()
    
    def on_mouse_press(self, x, y, button, modifiers):
        if not self._is_loaded or not self._options or len(self._options) == 0:
            return
        
        """
        A mouse press is going to create a manager with the options.
        """
        # if it's already opened, we just close it.
        if self._pulldown_menu is not None:
            self._delete_pulldown_menu()
            return
        
        # the function we pass to the manager.
        def on_escape(_):
            self._delete_pulldown_menu()
        
        width, height = self._manager.window.get_size()
        x = self.x
        y = -(height - self.y - 1) + self.height
        
        # we set the manager
        self._pulldown_menu = Manager(
            Frame(Scrollable(VerticalContainer(list(self._options.values())),
                             height=self.max_height), path=['dropdown', 'pulldown']),
            window=self._manager.window, batch=self._manager.batch,
            group=self._manager.root_group.parent, theme=self._manager.theme,
            is_movable=False, anchor=ANCHOR_TOP_LEFT, offset=(x, y))
    
    def select(self, option_name):
        if self._is_loaded:
            Selector.select(self, option_name)
            self._delete_pulldown_menu()
            self.reload()
            self.reset_size()
            self.layout()


def monkey_patching_Button_set_state(self, value: bool):
    self._is_pressed = value
    self.reload()
    self.reset_size()
        
    
Button.set_state = monkey_patching_Button_set_state

        
def monkey_patching_Button_change_state(self):
    self._is_pressed = not self._is_pressed
    if self.is_loaded:
        self.reload()
        self.reset_size()
        self._on_press(self._is_pressed)
        

Button.change_state = monkey_patching_Button_change_state


class TextInput(_TextInput):
    def __init__(self, **kwargs):
        _TextInput.__init__(self, **kwargs, max_length=5, length=6)


def set_hidden(self, value):
    self._hidden = value
    
    if self._hidden:
        if self._is_loaded:
            if isinstance(self, Container):
                self.unload()
            else:
                self.unload_graphics()
    else:
        if not self._is_loaded:
            if isinstance(self, Container):
                self.load()
            else:
                self.load_graphics()

    self.reset_size(False)
    Container.reset_size(self)


def monkey_patch_Container_load(self):
    if not self.hidden:
        super(Container, self).load()
        self.load_content()


HorizontalContainer.load = monkey_patch_Container_load


def monkey_patch_Container_reset_size(self, reset_parent=True):
    if not self.hidden:
        if not reset_parent:
            for item in self._content:
                item.reset_size(reset_parent=False)
        super(Container, self).reset_size(reset_parent)


HorizontalContainer.reset_size = monkey_patch_Container_reset_size


for widget in [Button, TextInput, Dropdown, Checkbox, Label, HorizontalContainer]:
    widget.hidden = property(lambda self: self._hidden, set_hidden)
    
    def make_func(compute_size, init, load_graphics, layout):
        
        def monkey_patching_compute_size(self):
            return compute_size(self) if not self.hidden else (0, 0)
        
        def monkey_patching_init(self, *args, **kwargs):
            hidden = None
            if 'hidden' in kwargs:
                hidden = kwargs['hidden']
                del kwargs['hidden']
                
            o = init(self, *args, **kwargs)
            self._hidden = hidden if hidden else False
            return o
        
        def monkey_patching_load_graphics(self):
            if not self.hidden:
                return load_graphics(self)
            
        def monkey_patching_layout(self):
            if not self.hidden:
                return layout(self)
            
        return monkey_patching_compute_size, monkey_patching_init, monkey_patching_load_graphics, monkey_patching_layout

    widget.compute_size, widget.__init__, widget.load_graphics, widget.layout =\
        make_func(widget.compute_size, widget.__init__, widget.load_graphics, widget.layout)



