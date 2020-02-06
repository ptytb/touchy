import ctypes
from ctypes import Structure, c_uint32, c_int32, c_uint64
from ctypes.wintypes import HANDLE, HWND, POINT, DWORD, RECT
from functools import partial

GetPointerPenInfo = ctypes.windll.user32.GetPointerPenInfo
GetPointerTouchInfo = ctypes.windll.user32.GetPointerTouchInfo
GetPointerInfo = ctypes.windll.user32.GetPointerInfo
ScreenToClient = ctypes.windll.user32.ScreenToClient


def get_flag_names(names, flags):
    buttons = []
    for f, name in names.items():
        if f & flags:
            buttons.append(name)
    return buttons


def get_pointerid_wparam(x):
    return x & 0xFFFF


# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ne-winuser-tagpointer_input_type

PT_POINTER  = 1
PT_TOUCH    = 2
PT_PEN      = 3
PT_MOUSE    = 4
PT_TOUCHPAD = 5

POINTER_MESSAGE_FLAG_NEW               = 0x00000001  # New pointer
POINTER_MESSAGE_FLAG_INRANGE           = 0x00000002  # Pointer has not departed
POINTER_MESSAGE_FLAG_INCONTACT         = 0x00000004  # Pointer is in contact
POINTER_MESSAGE_FLAG_FIRSTBUTTON       = 0x00000010  # Primary action
POINTER_MESSAGE_FLAG_SECONDBUTTON      = 0x00000020  # Secondary action
POINTER_MESSAGE_FLAG_THIRDBUTTON       = 0x00000040  # Third button
POINTER_MESSAGE_FLAG_FOURTHBUTTON      = 0x00000080  # Fourth button
POINTER_MESSAGE_FLAG_FIFTHBUTTON       = 0x00000100  # Fifth button
POINTER_MESSAGE_FLAG_PRIMARY           = 0x00002000  # Pointer is primary
POINTER_MESSAGE_FLAG_CONFIDENCE        = 0x00004000  # Pointer is considered unlikely to be accidental
POINTER_MESSAGE_FLAG_CANCELED          = 0x00008000  # Pointer is departing in an abnormal manner

pointerFlagNames = dict([
    [POINTER_MESSAGE_FLAG_NEW, "new"],
    [POINTER_MESSAGE_FLAG_INRANGE, "in_range"],
    [POINTER_MESSAGE_FLAG_INCONTACT, "in_contact"],
    [POINTER_MESSAGE_FLAG_FIRSTBUTTON, "first"],
    [POINTER_MESSAGE_FLAG_SECONDBUTTON, "second"],
    [POINTER_MESSAGE_FLAG_THIRDBUTTON, "third"],
    [POINTER_MESSAGE_FLAG_FOURTHBUTTON, "fourth"],
    [POINTER_MESSAGE_FLAG_FIFTHBUTTON, "fifth"],
    [POINTER_MESSAGE_FLAG_PRIMARY, "primary"],
    [POINTER_MESSAGE_FLAG_CONFIDENCE, "confidence"],
    [POINTER_MESSAGE_FLAG_CANCELED, "canceled"],
])
get_buttons = partial(get_flag_names, pointerFlagNames)


class POINTER_INFO(Structure):
    _fields_ = [
        ("pointerType", c_uint32),
        ("pointerId", c_uint32),
        ("frameId", c_uint32),
        ("pointerFlags", c_uint32),
        ("sourceDevice", HANDLE),
        ("hwndTarget", HWND),
        ("ptPixelLocation", POINT),
        ("ptHimetricLocation", POINT),
        ("ptPixelLocationRaw", POINT),
        ("ptHimetricLocationRaw", POINT),
        ("dwTime", DWORD),
        ("historyCount", c_uint32),
        ("InputData", c_int32),
        ("dwKeyStates", DWORD),
        ("PerformanceCount", c_uint64),
        ("ButtonChangeType", c_uint32),
    ]


# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-pointer_info

class POINTER_TOUCH_INFO(Structure):
    _fields_ = [
        ("pointerInfo", POINTER_INFO),
        ("touchFlags", c_uint32),
        ("touchMask", c_uint32),
        ("rcContact", RECT),
        ("rcContactRaw", RECT),
        ("orientation", c_uint32),
        ("pressure", c_uint32),
    ]


PEN_FLAG_NONE = 0x00000000
PEN_FLAG_BARREL = 0x00000001
PEN_FLAG_INVERTED = 0x00000002
PEN_FLAG_ERASER = 0x00000004

penTypeFlagNames = dict([
    [PEN_FLAG_BARREL, "barrel"],
    [PEN_FLAG_INVERTED, "inverted"],
    [PEN_FLAG_ERASER, "eraser"],
])
get_pen_type = partial(get_flag_names, penTypeFlagNames)

PEN_MASK_NONE = 0x00000000
PEN_MASK_PRESSURE = 0x00000001
PEN_MASK_ROTATION = 0x00000002
PEN_MASK_TILT_X = 0x00000004
PEN_MASK_TILT_Y = 0x00000008


class POINTER_PEN_INFO(Structure):
    _fields_ = [
        ("pointerInfo", POINTER_INFO),
        ("penFlags", c_uint32),
        ("penMask", c_uint32),
        ("pressure", c_uint32),
        ("rotation", c_uint32),
        ("tiltX", c_int32),
        ("tiltY", c_int32),
    ]


WM_TOUCH                     =  0x0240
WM_NCPOINTERUPDATE           =  0x0241
WM_NCPOINTERDOWN             =  0x0242
WM_NCPOINTERUP               =  0x0243
WM_POINTERUPDATE             =  0x0245
WM_POINTERDOWN               =  0x0246
WM_POINTERUP                 =  0x0247
WM_POINTERENTER              =  0x0249
WM_POINTERLEAVE              =  0x024A
WM_POINTERACTIVATE           =  0x024B
WM_POINTERCAPTURECHANGED     =  0x024C
WM_TOUCHHITTESTING           =  0x024D
WM_POINTERWHEEL              =  0x024E
WM_POINTERHWHEEL             =  0x024F
DM_POINTERHITTEST            =  0x0250
