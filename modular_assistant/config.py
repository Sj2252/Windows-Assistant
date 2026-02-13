APPS = {
    "notepad": {"command": "notepad", "window_title": "Notepad", "type": "system"},
    "calculator": {"command": "calc", "window_title": "Calculator", "type": "system"},
    "chrome": {"command": "chrome", "window_title": "Google Chrome", "type": "system"},
    "google chrome": {"command": "chrome", "window_title": "Google Chrome", "type": "system"},
    "excel": {"type": "office", "office_app": "Excel.Application"},
    "word": {"type": "office", "office_app": "Word.Application"},
    "powerpoint": {"type": "office", "office_app": "PowerPoint.Application"},
    "outlook": {"type": "office", "office_app": "Outlook.Application"},
    "paint": {"command": "mspaint", "window_title": "Paint", "type": "system"},
    "vlc": {"command": "vlc", "window_title": "VLC media player", "type": "system"},
    "explorer": {"command": "explorer", "window_title": "File Explorer", "type": "system"},
    "cmd": {"command": "cmd.exe", "window_title": "Command Prompt", "type": "system"},
    "microsoft edge": {"command": "msedge", "window_title": "Microsoft Edge", "type": "system"},
    "edge": {"command": "msedge", "window_title": "Microsoft Edge", "type": "system"}
}

# Azure Configuration
# 1. Create a free account at https://portal.azure.com/
# 2. Search for "Speech Services" and create a resource.
# 3. Go to "Keys and Endpoint" in the resource menu.
# 4. Paste your Key 1 and Location/Region below.
AZURE_SPEECH_KEY = "YOUR_KEY_HERE"
AZURE_SERVICE_REGION = "eastus"  # e.g., "eastus", "westus", "centralindia"
USE_AZURE_SPEECH = False # Set to True once you have entered your keys
