import speech_recognition as sr
import win32com.client
import os
import sys
import queue
import threading

# Try importing Azure, but don't fail if it's not installed yet
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

from config import AZURE_SPEECH_KEY, AZURE_SERVICE_REGION, USE_AZURE_SPEECH

# Initialize TTS engine for Windows (Offline)
try:
    windows_speaker = win32com.client.Dispatch("SAPI.SpVoice")
except:
    windows_speaker = None

# Global queue for commands
command_queue = queue.Queue()

def speak(text):
    """Speak the given text using Windows voice"""
    if windows_speaker:
        try:
            windows_speaker.Speak(text)
        except Exception as e:
            print(f"Error speaking: {e}")
    else:
        print(f"Speaker not initialized: {text}")

def callback_google(recognizer, audio):
    """Callback function for Google Speech Recognition background listener"""
    try:
        # Use recognize_google directly on the audio data
        print("Recognizing...")
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"Detected: {text}")
        command_queue.put(text.lower())
    except sr.UnknownValueError:
        pass # Silence is fine, don't clutter logs
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        speak("Connection error")

def start_listening_google():
    """Starts background listening using Google Speech Recognition"""
    r = sr.Recognizer()
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8

    try:
        mic = sr.Microphone()
        with mic as source:
            print("Calibrating microphone...")
            r.adjust_for_ambient_noise(source, duration=0.5)
        
        # This starts a background thread that calls callback_google when phrase is detected
        stop_listening = r.listen_in_background(mic, callback_google)
        print("Background listening started (Google)...")
        return stop_listening
    except Exception as e:
        print(f"Error accessing microphone: {e}")
        return None

def start_listening_azure():
    """Starts background listening using Azure Speech SDK"""
    if not speechsdk:
        print("Azure Speech SDK not installed.")
        return None
        
    if "YOUR_KEY_HERE" in AZURE_SPEECH_KEY:
        print("Please set your Azure keys in config.py")
        return None

    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SERVICE_REGION)
    speech_config.speech_recognition_language="en-US"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Azure Detected: {evt.result.text}")
            command_queue.put(evt.result.text.lower())

    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.start_continuous_recognition()
    print("Background listening started (Azure)...")
    
    return speech_recognizer

def start_listening():
    """Main entry point to start the appropriate background listener"""
    if USE_AZURE_SPEECH:
        return start_listening_azure()
    else:
        return start_listening_google()
