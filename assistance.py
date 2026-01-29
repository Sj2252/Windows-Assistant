import speech_recognition as sr
import win32com.client
import os
import datetime
import win32gui
import win32con
import subprocess
import win32api
import urllib.parse
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

# Application configuration dictionary
APPS = {
    "notepad": {"command": "notepad", "window_title": "Notepad", "type": "system"},#1
    "calculator": {"command": "calc", "window_title": "Calculator", "type": "system"},#2
    "chrome": {"command": "chrome", "window_title": "Google Chrome", "type": "system"},#3
    "google chrome": {"command": "chrome", "window_title": "Google Chrome", "type": "system"},#4
    "excel": {"type": "office", "office_app": "Excel.Application"},#5
    "word": {"type": "office", "office_app": "Word.Application"},#6
    "powerpoint": {"type": "office", "office_app": "PowerPoint.Application"},#7
    "outlook": {"type": "office", "office_app": "Outlook.Application"},#8
    "paint": {"command": "mspaint", "window_title": "Paint", "type": "system"},#9
    "vlc": {"command": "vlc", "window_title": "VLC media player", "type": "system"},#10
    "explorer": {"command": "explorer", "window_title": "File Explorer", "type": "system"},#11
    "cmd": {"command": "cmd.exe", "window_title": "Command Prompt", "type": "system"},#12
    "microsoft ed": {"command": "msedge", "window_title": "Microsoft Edge", "type": "system"}#13
}

def max(name):
    hwnd2 = win32gui.FindWindow(None, name)
    if hwnd2:
        win32gui.ShowWindow(hwnd2, win32con.SW_MAXIMIZE)
    else:
        speak(f"Could not find {name}")

def res(name):
    hwnd2 = win32gui.FindWindow(None, name)
    if hwnd2:
        win32gui.ShowWindow(hwnd2, win32con.SW_RESTORE)
    else:
        speak(f"Could not find {name}")

def min(name):
    hwnd2 = win32gui.FindWindow(None, name)
    if hwnd2:
        win32gui.ShowWindow(hwnd2, win32con.SW_MINIMIZE)
    else:
        speak(f"Could not find {name}")

def close_app(window_title):
    """Close an application by window title"""
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        return True
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
        app = win32com.client.Dispatch(f"{office_app}.Application")
        app.Visible = True
        if office_app == "Excel.Application":
            app.Workbooks.Add()
        elif office_app == "Word.Application":
            app.Documents.Add()
        elif office_app == "PowerPoint.Application":
            app.Presentations.Add()
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
            subprocess.Popen(app_lower)
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
        if close_app(window_title):
            speak(f"Closed {app_lower}")
            return True
        else:
            speak(f"{app_lower} is not running")
            return False
    else:
        speak(f"Unknown application: {app_lower}")
        return False

def search_web(query):
    """Search the web using Google"""
    try:
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        win32api.ShellExecute(0, "open", url, None, None, 1)
        speak(f"Searching for {query}")
        return True
    except Exception as e:
        speak(f"Error searching for {query}")
        print(f"Error: {e}")
        return False

def set_volume_percentage(percentage):
    """
    Set system volume to a specific percentage (0-100)
    """
    if not 0 <= percentage <= 100:
        print("Error: Volume percentage must be between 0 and 100")
        speak("Volume must be between 0 and 100 percent")
        return False
    
    try:
        # Get the default speaker
        devices = AudioUtilities.GetSpeakers()
        volume_interface = devices.EndpointVolume
        
        # Convert percentage to decimal (0.0 to 1.0)
        volume_level = percentage / 100.0
        
        # Set the volume using scalar (0.0 to 1.0)
        volume_interface.SetMasterVolumeLevelScalar(volume_level, None)
        speak(f"Volume set to {percentage} percent")
        return True
        
    except Exception as e:
        print(f"Error setting volume: {e}")
        speak("Error setting volume")
        return False

# Initialize Windows voice engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    """Speak the given text using Windows voice"""
    speaker.Speak(text)

def take_command(timeout=10, phrase_time_limit=None, retries=2):
    """
    Listen to user command using multiple recognition engines for better accuracy
    - Uses Google Cloud Speech Recognition as primary (most accurate)
    - Falls back to Sphinx (offline) if Google fails
    - Implements noise reduction and adaptive listening
    - Retries on failure
    """
    r = sr.Recognizer()
    
    # Optimize recognizer settings for better accuracy
    r.energy_threshold = 4000  # Reduce false positives from background noise
    r.dynamic_energy_threshold = True  # Automatically adjust threshold
    r.pause_threshold = 0.8  # Time before considering speech finished
    r.non_speaking_duration = 0.3  # Time to consider speech has paused
    
    # Use first available microphone
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if len(mic_list) == 0:
            print("No microphones found!")
            speak("No microphones found. Please connect one.")
            return ""
        mic = sr.Microphone(device_index=0)
    except Exception as e:
        print("Error accessing microphone:", e)
        speak("Microphone not accessible")
        return ""

    for attempt in range(retries):
        try:
            with mic as source:
                # Adaptive noise adjustment - longer duration for better calibration
                print("Calibrating microphone...")
                r.adjust_for_ambient_noise(source, duration=1.0)
                
                print("Listening...")
                speak("Listening")
                
                # Listen with timeout and phrase time limit
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            # Try Google Cloud Speech Recognition (most accurate, requires internet)
            try:
                command = r.recognize_google(audio, language='en-US')
                print(f"You said: {command}")
                return command.lower()
            except sr.UnknownValueError:
                print(f"Attempt {attempt + 1}: Google - Could not understand audio")
                
                # Fallback to Sphinx (offline, decent accuracy)
                try:
                    print("Trying offline recognition...")
                    command = r.recognize_sphinx(audio)
                    print(f"You said (Sphinx): {command}")
                    return command.lower()
                except sr.UnknownValueError:
                    print("Sphinx: Could not understand audio")
                    if attempt < retries - 1:
                        speak("Sorry, I did not understand. Please repeat.")
                    continue
                except sr.RequestError as e:
                    print(f"Sphinx error: {e}")
                    if attempt < retries - 1:
                        speak("Having trouble with voice recognition. Please try again.")
                    continue
                    
            except sr.RequestError:
                print("Google: No internet connection or service unavailable")
                speak("Could not reach speech recognition service. Check your internet.")
                
                # Try offline Sphinx as fallback
                try:
                    print("Trying offline recognition...")
                    command = r.recognize_sphinx(audio)
                    print(f"You said (Sphinx): {command}")
                    return command.lower()
                except:
                    pass
                
                if attempt < retries - 1:
                    speak("Please try again.")
                continue
                
        except sr.RequestError as e:
            print(f"Microphone/Audio error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                speak("Microphone error. Please try again.")
                continue
            else:
                speak("Unable to record audio. Please check your microphone.")
                return ""
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                speak("An error occurred. Please try again.")
                continue
            else:
                speak("Unable to process voice command.")
                return ""
    
    speak("Voice recognition failed. Please try again.")
    return ""

# Greeting
speak("Hello, I am your Windows voice assistant. How can I help you?")

# Main loop
while True:
    command = take_command()

    if not command:
        continue  # Retry if nothing detected

    if "time" in command:
        time_str = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {time_str}")

    elif "search" in command:
        # Extract search query from command like "search for python tutorials"
        query = command.replace("search for ", "").replace("search ", "").strip()
        if query:
            search_web(query)
        else:
            speak("What would you like to search for?")
            query = take_command()
            if query:
                search_web(query)

    elif "open" in command:
        # Extract app name from command like "open notepad" or "open chrome"
        app_name = command.replace("open ", "").strip()
        if app_name:
            open_app(app_name)
        else:
            speak("Which application would you like to open?")
            app_name = take_command()
            if app_name:
                open_app(app_name)

    elif "close" in command or "stop" in command:
        # Extract app name from command like "close notepad" or "stop chrome"
        app_name = command.replace("close ", "").replace("stop ", "").strip()
        if app_name:
            close_app_by_name(app_name)
        else:
            speak("Which application would you like to close?")
            app_name = take_command()
            if app_name:
                close_app_by_name(app_name)

    elif "max" in command:
        speak("Which application would you like to maximize?")
        name = take_command()
        if name:
            max(name)
            speak(f"Maximized {name}")

    elif "res" in command:
        speak("Which application would you like to restore?")
        name = take_command()
        if name:
            res(name)
            speak(f"Restored {name}")

    elif "min" in command:
        speak("Which application would you like to minimize?")
        name = take_command()
        if name:
            min(name)
            speak(f"Minimized {name}")

    elif "volume" in command or "sound" in command:
        # Extract volume percentage from command like "set volume to 50" or "volume 75"
        import re
        # Try to find a number in the command
        numbers = re.findall(r'\d+', command)
        if numbers:
            volume_percent = int(numbers[0])
            set_volume_percentage(volume_percent)
        else:
            speak("What volume level would you like? Say a number between 0 and 100.")
            vol_command = take_command()
            try:
                vol_numbers = re.findall(r'\d+', vol_command)
                if vol_numbers:
                    volume_percent = int(vol_numbers[0])
                    set_volume_percentage(volume_percent)
                else:
                    speak("I did not understand the volume level.")
            except Exception as e:
                print(f"Error: {e}")
                speak("Error setting volume")

    elif "off assistant" in command or "exit" in command or "quit" in command or "mute" in command:
        speak("Thank you. Goodbye!")
        break

    else:
        speak("Command not recognized. Try again.")
