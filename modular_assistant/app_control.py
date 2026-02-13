import win32gui
import win32con
import win32com.client
import os
import subprocess
from config import APPS
from voice_engine import speak

def maximize_window(name):
    hwnd = win32gui.FindWindow(None, name)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return True
    else:
        # Try to find by partial title if exact match fails
        def callback(hwnd, windows):
             if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if name.lower() in title.lower():
                    windows.append(hwnd)
        windows = []
        win32gui.EnumWindows(callback, windows)
        if windows:
            win32gui.ShowWindow(windows[0], win32con.SW_MAXIMIZE)
            return True
            
        speak(f"Could not find window {name}")
        return False

def restore_window(name):
    hwnd = win32gui.FindWindow(None, name)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return True
    else:
        speak(f"Could not find window {name}")
        return False

def minimize_window(name):
    hwnd = win32gui.FindWindow(None, name)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True
    else:
        speak(f"Could not find window {name}")
        return False

def close_app_window(window_title):
    """Close an application by window title (exact or partial)"""
    # Try exact match first
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        return True
    
    # Try partial match
    found_windows = []
    def callback(hwnd, windows):
         if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and window_title.lower() in title.lower():
                windows.append(hwnd)
    
    win32gui.EnumWindows(callback, found_windows)
    
    if found_windows:
        count = 0
        for hwnd in found_windows:
             try:
                win32gui.PostMessage(hwnd, 0x0010, 0, 0)
                count += 1
             except: pass
        return count > 0
        
    return False

def open_system_app(command, app_name):
    """Open a system application"""
    try:
        os.system(f"start {command}")
        speak(f"Opening {app_name}")
        return True
    except Exception as e:
        speak(f"Error opening {app_name}")
        print(f"Error: {e}")
        return False

def open_office_app(office_app, app_name):
    """Open an Office application"""
    try:
        if office_app.endswith(".Application"):
            prog_id = office_app
        else:
            prog_id = f"{office_app}.Application"
        app = win32com.client.Dispatch(prog_id)
        app.Visible = True
        if office_app == "Excel.Application":
            try:
                app.Workbooks.Add()
            except: pass
        elif office_app == "Word.Application":
             try:
                app.Documents.Add()
             except: pass
        elif office_app == "PowerPoint.Application":
             try:
                app.Presentations.Add()
             except: pass
        speak(f"Opening {app_name}")
        return True
    except Exception as e:
        speak(f"Error opening {app_name}")
        print(f"Error: {e}")
        return False

def open_app(app_name):
    """Open any application dynamically"""
    app_lower = app_name.lower().strip()
    
    if app_lower in APPS:
        app_config = APPS[app_lower]
        if app_config["type"] == "system":
            return open_system_app(app_config["command"], app_lower)
        elif app_config["type"] == "office":
            return open_office_app(app_config["office_app"], app_lower)
    else:
        # Try to open as generic command
        try:
            subprocess.Popen(app_lower, shell=True)
            speak(f"Opening {app_lower}")
            return True
        except:
            speak(f"Application {app_lower} not found")
            return False

def close_app_by_name(app_name):
    """Close any application by name"""
    app_lower = app_name.lower().strip()
    
    if app_lower in APPS:
        app_config = APPS[app_lower]
        window_title = app_config.get("window_title", app_lower)
        if close_app_window(window_title):
            speak(f"Closed {app_lower}")
            return True
        else:
            # Fallback for some processes if window title close doesn't work or isn't exact
            try:
                # Be careful with taskkill
                # subprocess.run(f"taskkill /f /im {app_config['command']}", shell=True)
                pass
            except:
                pass
            
            speak(f"{app_lower} window not found")
            return False
    else:
        speak(f"Unknown application: {app_lower}")
        return False
