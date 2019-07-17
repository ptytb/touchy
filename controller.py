from datetime import datetime, timedelta

import math
import operator
from functools import reduce
from itertools import groupby, chain, repeat

from autoclass import autoclass, setter_override
import mido
import pyglet
import pyglet.input
import pyglet.graphics
import pyglet.window
import pyglet.clock


from bindings import bind_tablet_key, bind_tablet_x, bind_tablet_y, bind_tablet_p, bind_mouse_key, bind_mouse_x, \
    bind_mouse_y, binding_buttons, binding_labels, binding_devices, bindings_axle, Binding, \
    model, RowBinding, bind_mouse_wheel_x, bind_mouse_wheel_y, table_row_mouse_wheel, bind_mouse_wheel_rows
from midi_codes import MIDI_CONTROL_CODES
from scale import ScaleLinear
from stateful_inputs import ThresholdAxes, AccumulatingAxes


@autoclass
class Controller:
    def __init__(self, window=None, manager=None, gui_visible=True):
        self.midi_ports = mido.get_output_names()
        self.midi_channels = [str(x) for x in range(0, 16)]
        self.midi_message_types = [
            # https://mido.readthedocs.io/en/latest/message_types.html
            # all in 0..127, except pitch in -8192..8191
            # all default 0, except velocity=64
            'note', 'velocity', 'aftertouch', 'polytouch', 'pitch', 'program', 'control', 'song select', 'song position'
        ]
        
        self.midi_control_types = list(MIDI_CONTROL_CODES.keys())
        
        self.tablets = pyglet.input.get_tablets()
        self.tablet_names = [tablet.name for tablet in self.tablets]
        self.selected_tablet_index = 0
        if self.tablets and len(self.tablets):
            self.selected_tablet = self.tablets[self.selected_tablet_index]
            self.tablet_cursor_names = list(set([cursor.name for cursor in (self.selected_tablet.cursors)]))
            self.tablet_button_names = list(map(lambda i: str(i), list(range(len(self.selected_tablet.cursors)))))
        else:
            self.selected_tablet = None
            self.tablet_cursor_names = []
            self.tablet_button_names = []

        # mouses = list(filter(lambda d: 'ouse' in d.name, pyglet.input.get_devices()))
        # buttons = list(filter(lambda b: 'utton' in b.raw_name, mouses[0].controls))
        mouse_button_names = [str(i) for i in range(8)]
        self.mouse_button_names = mouse_button_names
        
        self._canvas = None
        self.port = None
        
        self._scale_cache = dict()
        self._threshold_axes = dict()
        # self._incremental_axes = defaultdict(lambda: AccumulatingAxes())
        self.pull_back_handlers = dict()
        
        self._last_canvas_button = None
        
    def clear_scale_cache(self, *args, **kwargs):
        self._scale_cache.clear()
        
    @setter_override
    def window(self, window = None):
        self._window = window
        if window is None:
            return
        
        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            # self.manager.on_mouse_press(x, y, button, modifiers)
            if binding_buttons.mouse_on:
                button_str = pyglet.window.mouse.buttons_string(button)
                
                if binding_buttons.log_input_on:
                    binding_labels.mouse_status = 'on_mouse_press(%r, %r, %r=%r, %r' % (x, y, button, button_str, modifiers)
                
                self.saturate_thresholds()
                self.process_axes_input(source='mouse', cursor='cursor', button=button,
                                        axis_values={"x": x, "y": y},
                                        domains={"x": (0, self.window.width), "y": (0, self.window.height)})
    
        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            # self.manager.on_mouse_release(x, y, button, modifiers)
            if binding_buttons.mouse_on:
                if binding_buttons.log_input_on:
                    binding_labels.mouse_status = 'on_mouse_release(%r, %r, %r, %r)' % (x, y, button, modifiers)
                    
                self.reset_thresholds()
    
        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            # self.manager.on_mouse_motion(x, y, dx, dy)
            if binding_buttons.mouse_on:
                if binding_buttons.log_input_on:
                    binding_labels.mouse_status = 'on_mouse_motion(%r, %r)' % (x, y)
                    
                self.process_axes_input(source='mouse', cursor='cursor', button=0,
                                        axis_values={"x": x, "y": y},
                                        domains={"x": (0, self.window.width), "y": (0, self.window.height)})
    
        @self.window.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            # self.manager.on_mouse_drag(x, y, dx, dy, button, modifiers)
            if binding_buttons.mouse_on:
                button_str = pyglet.window.mouse.buttons_string(button)

                if binding_buttons.log_input_on:
                    binding_labels.mouse_status = 'on_mouse_drag(%r, %r, %r, %r, %r=%r, %r)' % (
                        x, y, dx, dy, button, button_str, modifiers)
                    
                self.process_axes_input(source='mouse', cursor='cursor', button=button,
                                        axis_values={"x": x, "y": y},
                                        domains={"x": (0, self.window.width), "y": (0, self.window.height)})
    
        @self.window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            if binding_buttons.mouse_on:
                if binding_buttons.log_input_on:
                    binding_labels.mouse_status = 'on_mouse_scroll(%r, %r, %r, %r)' % (x, y, scroll_x, scroll_y)
                    
                value_range = -1, 1
                self.process_axes_input(source='mouse', cursor='wheel', button=0,
                                        axis_values={"x": scroll_x, "y": scroll_y},
                                        domains={"x": value_range, "y": value_range})
        
    def update_widgets(self):
        @self.window.event
        def on_close():
            model.save()
    
        model.load()
        
        binding_devices.output_midi_port_name = self.midi_ports[0]
        if self.tablets and len(self.tablets):
            bind_tablet_key.tablet = self.tablet_names[0]
            bind_tablet_key.cursor = self.tablet_cursor_names[0]
            bind_tablet_key.button = self.tablet_button_names[0]
        bind_mouse_key.button = self.mouse_button_names[0]
        
        bind_tablet_x.notify_widgets()
        bind_tablet_y.notify_widgets()
        bind_tablet_p.notify_widgets()
        bind_mouse_x.notify_widgets()
        bind_mouse_y.notify_widgets()
        model.update_binding_from_table_row(table_row_mouse_wheel)
        bind_mouse_wheel_x.notify_listeners()
        bind_mouse_wheel_y.notify_listeners()
        bind_mouse_wheel_x.notify_widgets()
        bind_mouse_wheel_y.notify_widgets()
        binding_devices.notify_widgets()
        
    def toggle_fullscreen(self, *args):
        self.window.set_fullscreen(not self.window.fullscreen)
        
    def toggle_tablet_input(self, is_on, *, binding):
        if is_on:
            canvas = self.tablets[self.selected_tablet_index].open(self.window)
            self._canvas = canvas
            name = self.selected_tablet.name

            @canvas.event
            def on_enter(cursor):
                if binding_buttons.log_input_on:
                    binding_labels.touch_status = '%s: on_enter(%r)' % (name, cursor)

            @canvas.event
            def on_leave(cursor):
                if binding_buttons.log_input_on:
                    binding_labels.touch_status = '%s: on_leave(%r)' % (name, cursor)

            @canvas.event
            def on_motion(cursor, x, y, pressure, buttons):
                if binding_buttons.log_input_on:
                    text = '%s: on_motion(%r, x=%r, y=%r, pressure=%r, button=%s)' % (name, cursor.name, x, y, pressure, buttons)
                    binding_labels.touch_status = text
                
                if self._last_canvas_button != buttons:
                    self.saturate_thresholds()
                self._last_canvas_button = buttons
                
                self.process_axes_input(source=bind_tablet_key.tablet, cursor=cursor.name, button=buttons,
                                        axis_values={"x": x, "y": y, "z": pressure},
                                        domains={
                                                "x": (0, self.window.width),
                                                "y": (0, self.window.height),
                                                "z": (0, 1)
                                            })
        else:
            if self._canvas:
                self._canvas.close()
                self._canvas = None
                
    def calculate_grid(self, *args, binding=None):
        self.manager.vertex_list = None
        
        if not isinstance(binding, RowBinding):
            binding = None

        if binding and (binding.message_type != 'note' or not binding.range_from or not binding.range_to or not binding.enabled):
            binding = None

        if not binding:
            note_axes = list(filter(lambda b: b.enabled and b.message_type == 'note' and b.range_from and b.range_to, bindings_axle))
            if len(note_axes):
                binding = note_axes[0]
                
        if not binding:
            return
        
        width, height = self.window.width, self.window.height
        range_to, range_from = int(binding.range_to), int(binding.range_from)
        domain = range_to - range_from
        step = int(width / domain)
        
        if step < 1:
            return

        count = domain + 1
        
        if count < 1:
            return
    
        def odd(x):
            return x & 1
        
        def white(x):
            return x % 12 in (0, 2, 4, 5, 7, 9, 11)
        
        xs = list(chain((0,), reduce(operator.add, [list(repeat(i, 2)) for i in range(1, count)]), (count,)))
        lines = reduce(operator.concat, ((step * i, 0 if not odd(i) else height, step * i, height if not odd(i) else 0)
                                         for i in xs))
        colors = reduce(operator.concat, ((100, 100, 100, 80, 80, 80) if white(i // 2 + range_from) else (0, 0, 0, 0, 0, 0)
                                          for i in range(len(xs))))
        vertex_list = pyglet.graphics.vertex_list(2 * len(xs), ('v2i', lines), ('c3B', colors))
        self.manager.vertex_list = vertex_list
    
    def open_midi_port(self, name, *, binding):
        if self.port:
            self.port.close()
        self.port = mido.open_output(name=name)
        
    def process_axes_input(self, source, cursor, button=None, *, axis_values, domains):
        if not binding_buttons.midi_output_on:
            return
        
        # print('generate_midi_messages(): ', source, cursor, button, 'xyz=', axis_values)
        
        key = (source, cursor, str(button))
        generation_rules = model[key]
        
        if not generation_rules:
            return
        
        axes = filter(lambda x: x.enabled and x.axis in axis_values, generation_rules)
        axes = sorted(axes, key=lambda x: x.channel)

        def is_note_related(x):
            return x.message_type in ['note', 'velocity']
        
        for channel, axes in groupby(axes, lambda x: x.channel):
            note_axes = list()
            control_axes = list()

            axes = sorted(axes, key=is_note_related)
            for note_related, group in groupby(axes, is_note_related):
                if note_related:
                    note_axes = list(group)
                else:
                    control_axes = list(group)
                    
            note_axis = None
            note_velocity_axis = None

            for rule in note_axes:
                if rule.message_type == 'note':
                    note_axis = rule
                elif rule.message_type == 'velocity':
                    note_velocity_axis = rule

            if note_axis:
                note = self.get_rule_value(note_axis, axis_values, domains)
                note = self.clamp_rule_value(note_axis, note)
                if note:
                    note_kwargs = {"channel": int(channel)}
                    if note_velocity_axis:
                        velocity = self.get_rule_value(note_velocity_axis, axis_values, domains)
                        velocity = self.clamp_rule_value(note_velocity_axis, velocity)
                        note_kwargs["velocity"] = velocity
                        
                    midi_message = mido.Message(type='note_on', note=note, **note_kwargs)
                    self.port.send(midi_message)
                    
                    if binding_buttons.log_output_on:
                        binding_labels.output_status = str(midi_message)
                
            for rule in control_axes:
                self.generate_midi_control_message(rule, axis_values, domains)

    def get_rule_value(self, rule, axis_values, domains):
        is_incremental = 'step' in rule._fields

        scale = self._scale_cache.get(rule, None)
        if not scale:
            range_ = (int(rule.range_from), int(rule.range_to))
            domain = domains[rule.axis] if not is_incremental else range_
            scale = ScaleLinear(domain, range_)
            self._scale_cache[rule] = scale

        if is_incremental:
            values = {axis: value * int(rule.step) for axis, value in axis_values.items()}
            # incremental_axes = self._incremental_axes[rule]
            # values = incremental_axes.value(stepped_axes)
        else:
            threshold_axes = self._threshold_axes.get(rule)
            if not threshold_axes:
                threshold_axes = ThresholdAxes(rule.threshold if rule.message_type != 'velocity' else 0)
                self._threshold_axes[rule] = threshold_axes
            values = threshold_axes.value(axis_values)

        return scale.value(values[rule.axis]) if values else None

    def generate_midi_control_message(self, rule, axis_values, domains):
        value = self.get_rule_value(rule, axis_values, domains)
    
        if not value:
            return
    
        if 'step' in rule._fields:
            value = self.clamp_rule_value(rule, rule.value + value)
            model.update_row(table_row_mouse_wheel, rule, rule._replace(value=value))
        else:
            value = self.clamp_rule_value(rule, value)
            self.generate_midi_control_message_from_value(rule, value)
        
    def clamp_rule_value(self, rule, value):
        if not value:
            return value
        return max(min(int(value), int(rule.range_to)), int(rule.range_from))
    
    def generate_midi_control_message_from_value(self, rule, value):
        midi_message = None
        kwargs = {"channel": int(rule.channel)}
        
        if rule.message_type == 'pitch':
            midi_message = mido.Message(type='pitchwheel', pitch=value, **kwargs)
        elif rule.message_type == 'control':
            control_type = MIDI_CONTROL_CODES[rule.control_type]
            midi_message = mido.Message(type='control_change', control=control_type, value=value, **kwargs)
        elif rule.message_type == 'program':
            midi_message = mido.Message(type='program_change', program=value, **kwargs)
        elif rule.message_type == 'aftertouch':
            midi_message = mido.Message(type='aftertouch', value=value, **kwargs)
        elif rule.message_type == 'polytouch':
            midi_message = mido.Message(type='polytouch', note=60, value=value, **kwargs)
        elif rule.message_type == 'song select':
            midi_message = mido.Message(type='song_select', song=value, **kwargs)
        elif rule.message_type == 'song position':
            midi_message = mido.Message(type='songpos', pos=value, **kwargs)
    
        if midi_message:
            self.port.send(midi_message)
            
            if binding_buttons.log_output_on:
                binding_labels.output_status = str(midi_message)
            
    def on_wheel_slider_value_changed(self, value, *, binding):
        self.generate_midi_control_message_from_value(binding.to_tuple(), int(value))
        
        if binding.pull_back and id(binding) not in self.pull_back_handlers:
            self.on_wheel_pull_back_checkbox_changed(True, binding=binding)

    def on_wheel_pull_back_checkbox_changed(self, is_on, *, binding):
        handler = self.pull_back_handlers.get(id(binding), None)
        if handler:
            pyglet.clock.unschedule(handler)
            del self.pull_back_handlers[id(binding)]
            
        if is_on:
            def pull_wheel_back(dt):
                value_timestamp = binding.get_timestamp('_value')
                if datetime.now() - value_timestamp < timedelta(seconds=2):
                    return
                
                target_value = 0
                step = math.copysign(int(binding.step), int(binding.value))
                new_value = binding.value - step
                hit_target = new_value >= target_value if step < 0 else new_value <= target_value
                
                binding.timestamp_enabled = False
                binding.value = new_value if not hit_target else target_value
                binding.timestamp_enabled = True
                
                if hit_target:
                    pyglet.clock.unschedule(pull_wheel_back)
                    del self.pull_back_handlers[id(binding)]

            self.pull_back_handlers[id(binding)] = pull_wheel_back
            pyglet.clock.schedule_interval(pull_wheel_back, 0.05)

    def update_wheel_slider_value(self, value, *, binding):
        slider = binding.widgets['value']
        range_from, range_to = int(binding.range_from), int(binding.range_to)
        slider._min_value, slider._max_value = range_from, range_to
        if not range_from <= binding.value <= range_to:
            slider.set_value((range_from + range_to) // 2)
        slider.layout()

    def on_message_type_changed(self, message_type, *, binding):
        control_group = binding.widgets['control_group']
        control_group.hidden = message_type != 'control'
    
    def midi_all_notes_off(self, *args):
        if self.port:
            control_type = MIDI_CONTROL_CODES['All Notes Off']
            midi_message = mido.Message(type='control_change', control=control_type)
            self.port.send(midi_message)
        
    def reset_thresholds(self):
        for threshold_axis in self._threshold_axes.values():
            threshold_axis.reset()
            
    def saturate_thresholds(self):
        for threshold_axis in self._threshold_axes.values():
            threshold_axis.saturate()
            
    def toggle_gui(self, *args):
        self.gui_visible = not self.gui_visible
        self.window.remove_handlers(self.manager)
        if self.gui_visible:
            self.window.push_handlers(self.manager)
        
        # def remove_listeners(widget):
        #     self.window.remove_handlers(widget)
        #     if '_content' in dir(widget):
        #         for child in widget._content:
        #             remove_listeners(child)
        #
        # remove_listeners(self.manager)
        
    def on_keyboard_input(self, text: str):
        text = text.upper()
        if text == 'H':
            self.toggle_gui()
        elif text == 'F':
            self.toggle_fullscreen()
        elif text == ' ':
            self.midi_all_notes_off()
        
    def start_listen_bindings(self):
        binding_buttons.listen('tablet_on', controller.toggle_tablet_input)
        binding_devices.listen('output_midi_port_name', controller.open_midi_port)

        for binding in [bind_tablet_x, bind_tablet_y, bind_tablet_p, bind_mouse_x, bind_mouse_y]:
            binding.listen('message_type', controller.calculate_grid)
            binding.listen('range_from', controller.calculate_grid)
            binding.listen('range_to', controller.calculate_grid)

        bind_tablet_key.listen('*', controller.calculate_grid)
        bind_mouse_key.listen('*', controller.calculate_grid)

        for binding in bind_mouse_wheel_rows:
            binding.listen('range_from', controller.update_wheel_slider_value)
            binding.listen('range_to', controller.update_wheel_slider_value)
            binding.listen('value', controller.on_wheel_slider_value_changed)
            binding.listen('pull_back', controller.on_wheel_pull_back_checkbox_changed)

        for binding in [bind_tablet_x, bind_tablet_y, bind_tablet_p, bind_mouse_x, bind_mouse_y, bind_mouse_wheel_x,
                        bind_mouse_wheel_y]:
            binding.listen('message_type', controller.on_message_type_changed)
            binding.listen('range_from', controller.clear_scale_cache)
            binding.listen('range_to', controller.clear_scale_cache)
            binding.listen('threshold', lambda *args, **kwargs: self._threshold_axes.clear)
            

controller = Controller()
