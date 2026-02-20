import wmi
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
