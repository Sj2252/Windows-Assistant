import urllib.parse
import win32api
from voice_engine import speak

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
