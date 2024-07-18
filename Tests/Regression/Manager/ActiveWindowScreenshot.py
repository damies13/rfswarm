import pygetwindow as gw
from PIL import ImageGrab

def get_screenshot_of_the_active_window(path):
    active_window = gw.getActiveWindow()

    if active_window:
        # Get the bounding box of the active window
        bbox = (active_window.left, active_window.top, active_window.right, active_window.bottom)
        # Capture the screenshot of the active window
        screenshot = ImageGrab.grab(bbox)
        # Save the screenshot
        screenshot.save(path)
        
        print(f"Screenshot saved as {path}")
    else:
        print("No active window found.")
