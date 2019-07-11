import pyglet
from pyglet_gui.buttons import Checkbox, OneTimeButton
from pyglet_gui.containers import VerticalContainer, Wrapper, HorizontalContainer, GridContainer
from pyglet_gui.gui import Frame, SectionHeader, Label
from pyglet_gui.manager import Manager
from pyglet_gui.sliders import HorizontalSlider
from pyglet_gui.theme import Theme
from json import load

from bindings import bind_tablet_key, bind_tablet_x, bind_tablet_y, bind_tablet_p, bind_mouse_key, bind_mouse_x, \
    bind_mouse_y, binding_buttons, binding_labels, binding_devices, bind_mouse_wheel_x, bind_mouse_wheel_y

from monkey_patching import Dropdown, Button, TextInput
from controller import controller


class MainManager(Manager):
    def __init__(self, *, window, **kwargs):
        self.vertex_list = None
        batch = pyglet.graphics.Batch()
        controller.window = window
        controller.manager = self
        
        with open('theme/theme.json') as f:
            theme = Theme(load(f), resources_path='./theme')

        super().__init__(VerticalContainer([
            
            Frame(Wrapper(VerticalContainer([
                SectionHeader("Map Tablet to MIDI outputs"),
                HorizontalContainer([
                    Label("Controller tablet"),
                    binding_devices.bind(Dropdown(controller.tablet_names), 'tablet'),
                ]),
                HorizontalContainer([
                    Label("Map pointer"),
                    bind_tablet_key.bind(Dropdown(controller.tablet_cursor_names), 'cursor'),
                    Label("with"),
                    Label("active button"),
                    bind_tablet_key.bind(Dropdown(controller.tablet_button_names), 'button'),
                    Label("as:")
                ]),
                GridContainer([
                    [
                        bind_tablet_x.bind(Button("X"), 'enabled'),
                        Label("to channel"),
                        bind_tablet_x.bind(Dropdown(controller.midi_channels), 'channel'),
                        
                        Label("as"),
                        HorizontalContainer([
                            bind_tablet_x.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_tablet_x.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_tablet_x.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
    
                        Label("ranging from"),
                        bind_tablet_x.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_tablet_x.bind(TextInput(), 'range_to'),
                        Label("threshold"),
                        bind_tablet_x.bind(HorizontalSlider(min_value=0.0, max_value=100.0, steps=20), 'threshold'),
                    ],
                    [
                        bind_tablet_y.bind(Button("Y"), 'enabled'),
                        Label("to channel"),
                        bind_tablet_y.bind(Dropdown(controller.midi_channels), 'channel'),
                        
                        Label("as"),
                        HorizontalContainer([
                            bind_tablet_y.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_tablet_y.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_tablet_y.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
    
                        Label("ranging from"),
                        bind_tablet_y.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_tablet_y.bind(TextInput(), 'range_to'),
                        Label("threshold"),
                        bind_tablet_y.bind(HorizontalSlider(min_value=0.0, max_value=100.0, steps=20), 'threshold'),
                    ],
                    [
                        bind_tablet_p.bind(Button("Pressure"), 'enabled'),
                        Label("to channel"),
                        bind_tablet_p.bind(Dropdown(controller.midi_channels), 'channel'),
                        
                        Label("as"),
                        HorizontalContainer([
                            bind_tablet_p.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_tablet_p.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_tablet_p.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
    
                        Label("ranging from"),
                        bind_tablet_p.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_tablet_p.bind(TextInput(), 'range_to'),
                        Label("threshold"),
                        bind_tablet_p.bind(HorizontalSlider(min_value=0.0, max_value=1.0, steps=15), 'threshold'),
                    ],
                ]),
            ]))),
            
            Frame(Wrapper(VerticalContainer([
                SectionHeader("Map Mouse to MIDI outputs"),
                HorizontalContainer([
                    Label("Map mouse with active button"),
                    bind_mouse_key.bind(Dropdown(controller.mouse_button_names), 'button'),
                    Label("as:"),
                ]),
                GridContainer([
                    [
                        bind_mouse_x.bind(Button("X"), 'enabled'),
                        Label("to channel"),
                        bind_mouse_x.bind(Dropdown(controller.midi_channels), 'channel'),
    
                        Label("as"),
                        HorizontalContainer([
                            bind_mouse_x.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_mouse_x.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_mouse_x.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
    
                        Label("ranging from"),
                        bind_mouse_x.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_mouse_x.bind(TextInput(), 'range_to'),
                        Label("threshold"),
                        bind_mouse_x.bind(HorizontalSlider(min_value=0.0, max_value=100.0, steps=20), 'threshold'),
                    ],
                    [
                        bind_mouse_y.bind(Button("Y"), 'enabled'),
                        Label("to channel"),
                        bind_mouse_y.bind(Dropdown(controller.midi_channels), 'channel'),
                        
                        Label("as"),
                        HorizontalContainer([
                            bind_mouse_y.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_mouse_y.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_mouse_y.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
    
                        Label("ranging from"),
                        bind_mouse_y.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_mouse_y.bind(TextInput(), 'range_to'),
                        Label("threshold"),
                        bind_mouse_y.bind(HorizontalSlider(min_value=0.0, max_value=100.0, steps=20), 'threshold'),
                    ],
                ]),
                HorizontalContainer([
                    Label("Map mouse wheel as:"),
                ]),
                GridContainer([
                    [
                        bind_mouse_wheel_x.bind(Button("X"), 'enabled'),
                        Label("to channel"),
                        bind_mouse_wheel_x.bind(Dropdown(controller.midi_channels), 'channel'),
    
                        Label("as"),
                        HorizontalContainer([
                            bind_mouse_wheel_x.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_mouse_wheel_x.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_mouse_wheel_x.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
    
                        Label("ranging from"),
                        bind_mouse_wheel_x.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_mouse_wheel_x.bind(TextInput(), 'range_to'),
                        Label("step"),
                        bind_mouse_wheel_x.bind(TextInput(), 'step'),
                        Label("value"),
                        bind_mouse_wheel_x.bind(HorizontalSlider(min_value=0.0, max_value=100.0, steps=20), 'value'),
                        bind_mouse_wheel_x.bind(Checkbox('pull back'), 'pull_back'),
                    ],
                    [
                        bind_mouse_wheel_y.bind(Button("Y"), 'enabled'),
                        Label("to channel"),
                        bind_mouse_wheel_y.bind(Dropdown(controller.midi_channels), 'channel'),
    
                        Label("as"),
                        HorizontalContainer([
                            bind_mouse_wheel_y.bind(Dropdown(controller.midi_message_types), 'message_type'),
                            bind_mouse_wheel_y.widget(
                                HorizontalContainer([
                                    Label("for"),
                                    bind_mouse_wheel_y.bind(Dropdown(controller.midi_control_types), 'control_type'),
                                ], hidden=True), 'control_group'),
                        ]),
                        
                        Label("ranging from"),
                        bind_mouse_wheel_y.bind(TextInput(), 'range_from'),
                        Label("to"),
                        bind_mouse_wheel_y.bind(TextInput(), 'range_to'),
                        Label("step"),
                        bind_mouse_wheel_y.bind(TextInput(), 'step'),
                        Label("value"),
                        bind_mouse_wheel_y.bind(HorizontalSlider(min_value=0.0, max_value=100.0, steps=20), 'value'),
                        bind_mouse_wheel_y.bind(Checkbox('pull back'), 'pull_back'),
                    ],
                ]),
            ]))),
            
            HorizontalContainer([
                binding_buttons.bind(Button(label="Tablet Input On"), 'tablet_on'),
                binding_buttons.bind(Button(label="Mouse Input On"), 'mouse_on'),
                Button(label="Fullscreen", on_press=controller.toggle_fullscreen),
                OneTimeButton('All Notes Off', on_release=controller.midi_all_notes_off),
                OneTimeButton('Hide', on_release=controller.toggle_gui)
            ]),
            
            Frame(Wrapper(VerticalContainer([
                SectionHeader("Output Device"),
                GridContainer([
                    [
                        Label("Output MIDI port"),
                        binding_devices.bind(Dropdown(controller.midi_ports), 'output_midi_port_name'),
                    ],
                ]),
                HorizontalContainer([
                    binding_buttons.bind(Button(label="MIDI Output On"), 'midi_output_on'),
                    binding_buttons.bind(Button(label="Log Output"), 'log_output_on'),
                    binding_buttons.bind(Button(label="Log Input"), 'log_input_on'),
                ]),
            ]))),
            
            Frame(Wrapper(VerticalContainer([
                SectionHeader("Status"),
                Label("Input:", bold=True),
                binding_labels.bind(Label("---"), 'touch_status'),
                binding_labels.bind(Label("---"), 'mouse_status'),
                Label("Output:", bold=True),
                binding_labels.bind(Label("---"), 'output_status'),
            ]))),

        ]), theme=theme, window=window, batch=batch, **kwargs)
        
        controller.start_listen_bindings()
        controller.update_widgets()
        
        @window.event
        def on_resize(width, height):
            controller.clear_scale_cache()
            controller.calculate_grid()

        if __debug__:
            fps_display = pyglet.clock.ClockDisplay()
        
        @window.event
        def on_draw():
            window.clear()

            if self.vertex_list:
                self.vertex_list.draw(pyglet.gl.GL_LINES)
                
            if controller.gui_visible:
                batch.draw()
            
            if __debug__:
                fps_display.draw()

        @window.event
        def on_text(text):
            controller.on_keyboard_input(text)
