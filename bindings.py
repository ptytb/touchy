from collections import namedtuple
from datetime import datetime

from autoclass import autoclass
from pyglet_gui.gui import Label
from pyglet_gui.buttons import Checkbox
from pyglet_gui.sliders import HorizontalSlider
from typing import FrozenSet

from model import TableRow, Model
from monkey_patching import Dropdown, Button, TextInput


@autoclass
class Binding:
    
    @property
    def widgets(self):
        return self._widgets
    
    @property
    def model_key(self):
        return tuple(self.values())
    
    @property
    def is_valid(self):
        return all(map(lambda value: value is not None, self.values()))

    widget_bindings = {
        TextInput: ('on_input', 'set_text'),
        Dropdown: ('on_select', 'select'),
        HorizontalSlider: ('on_set', 'set_value'),
        Button: ('on_press', 'set_state'),
        Label: (None, 'set_text'),
        Checkbox: ('on_press', 'set_state')
    }
    
    def __init__(self):
        super().__init__()
        self._subscriptions = dict()
        self._listeners = dict()
        self._listeners.setdefault('*', list())
        self._widgets = dict()
        
        named_tuple_name = type(self).__qualname__ + '_tuple'
        self._to_named_tuple = namedtuple(named_tuple_name, self.keys())
        
        self.defaults = self.to_tuple()
    
    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in self.keys():
            self._notify_widget(key, value)
    
    def _notify_widget(self, key, value):
        if hasattr(self, '_subscriptions') and key in self._subscriptions:
            self._subscriptions[key](value)
    
    def notify_widgets(self):
        for key in self.keys():
            if key in self._subscriptions:
                value = getattr(self, key)
                if value:
                    self._subscriptions[key](value)
    
    def notify_listeners(self):
        for key, value in self.items():
            self._notify_listeners(key, value)
    
    def make_delegated_setter(self, key):
        def setter(value):
            super(Binding, self).__setattr__(key, value)
            self._notify_listeners(key, value)
        return setter
    
    def widget(self, widget, name):
        self._widgets[name] = widget
        return widget
    
    def bind(self, widget, key):
        self._widgets[key] = widget
        callback, setter_method = self.widget_bindings[type(widget)]
        self._subscriptions[key] = getattr(widget, setter_method)
        if callback:
            setattr(widget, f"_{callback}", self.make_delegated_setter(key))
        return widget
    
    def to_dict(self):
        return {key: value for key, value in self.items()}
    
    def from_dict(self, props: dict):
        for key, value in props.items():
            setattr(self, key, value)

    def to_tuple(self):
        return self._to_named_tuple(*self.values())
    
    def from_tuple(self, props: tuple):
        for i, key in enumerate(self.keys()):
            setattr(self, key, props[i])

    def _notify_listeners(self, key, value):
        # print(self.is_valid, key, self)
        listeners = [*self._listeners.get(key, []), *self._listeners['*']]
        for f in listeners:
            f(value, binding=self)
        
    def listen(self, key, callback):
        self._listeners.setdefault(key, list())
        self._listeners[key].append(callback)
        

@autoclass
class TabletKeyBinding(Binding):
    def __init__(self, tablet=None, cursor=None, button=None):
        super().__init__()


@autoclass
class MouseKeyBinding(Binding):
    def __init__(self, button=None):
        super().__init__()

    @property
    def model_key(self):
        return 'mouse', 'cursor', self.button
        

@autoclass
class RowBinding(Binding):
    def __init__(self, enabled, channel, message_type, control_type, range_from, range_to, threshold, axis):
        super().__init__()


@autoclass
class AttrTimestampMixin:
    def __init__(self, timestamp_attrs: FrozenSet[str], timestamp_enabled=True):
        super().__init__()
        self.attr_time = dict()
        
    def __setattr__(self, key, value):
        if '_timestamp_attrs' in self.__dict__ and key in self.timestamp_attrs and self.timestamp_enabled:
            self.attr_time[key] = datetime.now()
        super(AttrTimestampMixin, self).__setattr__(key, value)
        
    def get_timestamp(self, attr_name):
        return self.attr_time.get(attr_name, datetime.min)
        

@autoclass
class RowStepBinding(AttrTimestampMixin, Binding):
    def __init__(self, enabled, channel, message_type, control_type, range_from, range_to, step, value, pull_back, axis):
        super().__init__(timestamp_attrs=frozenset({'_value'}))


@autoclass
class ButtonsBinding(Binding):
    def __init__(self, tablet_on=False, mouse_on=False, midi_output_on=False, log_output_on=False, log_input_on=False):
        super().__init__()
    

@autoclass
class LabelsBinding(Binding):
    def __init__(self, touch_status='', mouse_status='', output_status=''):
        super().__init__()


@autoclass
class DevicesBinding(Binding):
    def __init__(self, output_midi_port_name=None):
        super().__init__()
    
    
def _binding_tablet_row(axis):
    return RowBinding(enabled=False, channel='0', message_type='control', control_type='Bank Select',
                      range_from='0', range_to='127', threshold=0, axis=axis)


def _binding_mouse_row(axis):
    return RowBinding(enabled=False, channel='0', message_type='control', control_type='Bank Select',
                      range_from='0', range_to='127', threshold=5, axis=axis)


def _binding_mouse_wheel_row(axis):
    range_from = -8192
    range_to = 8191
    binding = RowStepBinding(enabled=False, channel='0', message_type='pitch', control_type='Bank Select',
                          range_from=str(range_from), range_to=str(range_to),
                          step='100', value=0, axis=axis, pull_back=False)
    return binding


def _axis(n):
    return chr(ord('x') + n)


bind_tablet_key = TabletKeyBinding()
bind_tablet_rows = [_binding_tablet_row(_axis(i)) for i in range(3)]
bind_tablet_x = bind_tablet_rows[0]
bind_tablet_y = bind_tablet_rows[1]
bind_tablet_p = bind_tablet_rows[2]

bind_mouse_key = MouseKeyBinding()
bind_mouse_rows = [_binding_mouse_row(_axis(i)) for i in range(3)]
bind_mouse_x = bind_mouse_rows[0]
bind_mouse_y = bind_mouse_rows[1]

bind_mouse_wheel_rows = [_binding_mouse_wheel_row(_axis(i)) for i in range(2)]
bind_mouse_wheel_x = bind_mouse_wheel_rows[0]
bind_mouse_wheel_y = bind_mouse_wheel_rows[1]

binding_buttons = ButtonsBinding()
binding_labels = LabelsBinding()
binding_devices = DevicesBinding()

bindings_axle = [bind_tablet_x, bind_tablet_y, bind_tablet_p, bind_mouse_x, bind_mouse_y]


table_row_mouse_wheel = TableRow(('mouse', 'wheel', '0'), [bind_mouse_wheel_x, bind_mouse_wheel_y])

model = Model(
    TableRow(bind_tablet_key, [bind_tablet_x, bind_tablet_y, bind_tablet_p]),
    TableRow(bind_mouse_key, [bind_mouse_x, bind_mouse_y]),
    table_row_mouse_wheel
)
