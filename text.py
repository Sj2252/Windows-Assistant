import win32gui

def enum_windows_callback(hwnd, windows):
    # Check if window is visible
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:  # Only keep windows with a title
            windows.append((hwnd, title))

windows = []
win32gui.EnumWindows(enum_windows_callback, windows)

for hwnd, title in windows:
    print(f"HWND:{hwnd} | Title: {title}")
