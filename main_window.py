import pyglet
from pyglet.window.win32 import Win32EventHandler, ViewEventHandler, byref

from windows_ink import GetPointerPenInfo, GetPointerTouchInfo, GetPointerInfo, ScreenToClient, get_pointerid_wparam, \
    get_buttons, POINTER_INFO, POINTER_TOUCH_INFO, get_pen_type, POINTER_PEN_INFO, WM_TOUCH, WM_POINTERUPDATE, \
    WM_POINTERDOWN, WM_POINTERUP, WM_POINTERENTER, WM_POINTERLEAVE, WM_POINTERCAPTURECHANGED


class MainWindow(pyglet.window.Window):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_types.append("on_ink")
        self.event_types.append("on_ink_end")
        self.event_types.append("on_ink_begin")

    @ViewEventHandler
    @Win32EventHandler(WM_TOUCH)
    @Win32EventHandler(WM_POINTERENTER)
    @Win32EventHandler(WM_POINTERLEAVE)
    @Win32EventHandler(WM_POINTERDOWN)
    @Win32EventHandler(WM_POINTERUP)
    @Win32EventHandler(WM_POINTERUPDATE)
    @Win32EventHandler(WM_POINTERCAPTURECHANGED)
    def _touch_handler(self, msg, w_param, l_param):
        pointer_id = get_pointerid_wparam(w_param)
        
        # pointer_info = POINTER_INFO()
        # ok = GetPointerInfo(pointer_id, byref(pointer_info))
        #
        # pointer_touch_info = POINTER_TOUCH_INFO()
        # ok = GetPointerTouchInfo(pointer_id, byref(pointer_touch_info))

        pointer_pen_info = POINTER_PEN_INFO()
        ok = GetPointerPenInfo(pointer_id, byref(pointer_pen_info))
        
        location = pointer_pen_info.pointerInfo.ptPixelLocation
        ScreenToClient(self._hwnd, byref(pointer_pen_info.pointerInfo.ptPixelLocation))
        buttons = get_buttons(pointer_pen_info.pointerInfo.pointerFlags)
        pen_type = get_pen_type(pointer_pen_info.penFlags)
        pressure = pointer_pen_info.pressure / 1024
        
        if 'in_range' not in buttons:
            self.dispatch_event('on_ink_end')
        elif 'new' in buttons:
            self.dispatch_event('on_ink_begin')
        
        self.dispatch_event('on_ink', location.x, location.y, pressure,
                            buttons, pen_type)

        return 0
