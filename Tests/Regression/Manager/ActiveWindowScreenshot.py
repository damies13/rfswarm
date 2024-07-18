# import pygetwindow as gw
# from PIL import ImageGrab

# def get_screenshot_of_the_active_window(path):
#     active_window = gw.getActiveWindow()

#     if active_window:
#         # Get the bounding box of the active window
#         bbox = (active_window.left, active_window.top, active_window.right, active_window.bottom)
#         # Capture the screenshot of the active window
#         screenshot = ImageGrab.grab(bbox)
#         # Save the screenshot
#         screenshot.save(path)
        
#         print(f"Screenshot saved as {path}")
#     else:
#         print("No active window found.")

import sys
import pyautogui
from PIL import Image
import platform

def get_active_window_linux():
    import Xlib
    d = Xlib.display.Display()
    root = d.screen().root
    window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), Xlib.X.AnyPropertyType).value[0]
    window = d.create_resource_object('window', window_id)
    geom = window.get_geometry()
    return geom.x, geom.y, geom.width, geom.height

def get_active_window_mac():
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    options = kCGWindowListOptionOnScreenOnly
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
    for window in window_list:
        if window['kCGWindowLayer'] == 0 and window['kCGWindowOwnerName'] != 'Dock':
            bounds = window['kCGWindowBounds']
            return bounds['X'], bounds['Y'], bounds['Width'], bounds['Height']
    return None

def get_active_window_windows():
    import win32gui
    window = win32gui.GetForegroundWindow()
    rect = win32gui.GetWindowRect(window)
    return rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

def get_screenshot_of_the_active_window(filename):
    system = platform.system()

    if system == 'Linux':
        left, top, width, height = get_active_window_linux()
    elif system == 'Darwin':
        active_window = get_active_window_mac()
        if active_window is None:
            raise Exception("Cant find active window")
        left, top, width, height = active_window
    elif system == 'Windows':
        left, top, width, height = get_active_window_windows()
    else:
        raise Exception(f"Unsupported os: {system}")

    screenshot = pyautogui.screenshot()
    active_window_screenshot = screenshot.crop((left, top, left + width, top + height))
    active_window_screenshot.save(filename)

# if __name__ == "__main__":
#     filename = ""
#     capture_active_window_screenshot(filename)

