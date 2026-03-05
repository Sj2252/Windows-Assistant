import wmi
import win32api
import win32con
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from voice_engine import speak

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

def set_brightness(level):
    """
    Set screen brightness to a specific level (0-100)
    """
    level = max(0, min(100, level))
    try:
        c = wmi.WMI(namespace='wmi')
        methods = c.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(level, 0)
        speak(f"Brightness set to {level} percent")
        return True
    except Exception as e:
        print(f"Error setting brightness: {e}")
        speak("I could not change the brightness on this device.")
        return False

def control_media(action):
    """
    Control media playback (play, pause, next, previous)
    """
    # Key codes for media control
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_PLAY_PAUSE = 0xB3
    
    try:
        if action == "play" or action == "pause" or action == "play/pause":
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
            speak(f"Media {action}")
        elif action == "next":
            win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            speak("Playing next track")
        elif action == "previous":
            win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            speak("Playing previous track")
        return True
    except Exception as e:
        print(f"Error controlling media: {e}")
        return False
