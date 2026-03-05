# Windows Voice Assistant - Project Documentation (Full Logic)

**Project Name:** Windows Voice Assistant  
**Date:** March 5, 2026  
**Repository:** Sj2252/Windows-Assistant

---

## 1. Overview
This project is a modular Windows voice assistant with a modern web dashboard. It listens continuously, converts speech to text, routes intent, and executes system/app actions. The system is built around:
- A background listener thread
- A thread-safe queue
- A robust state machine
- Specialized control modules
- A FastAPI web interface

---

## 2. High-Level Flow
```
Microphone -> Speech Recognition -> Callback -> Queue -> State Manager -> Router -> Handler -> TTS -> Speaker
                                                       |
                                                       -> WebSocket -> Web Dashboard
```

1. The voice engine listens in the background.
2. The speech recognizer fires a callback with recognized text.
3. The callback pushes text into a thread-safe queue.
4. The main loop blocks on the queue, then processes commands.
5. The state machine determines whether the system is dormant, active, or listening.
6. The router detects intent using regex to clean redundant keywords.
7. The handler verifies the request (e.g., checking if an app exists) and executes the action.
8. Feedback is spoken via TTS and sent to the dashboard via WebSockets.

---

## 3. Modules and Logic

### 3.1 `voice_engine.py`
**Responsibilities:**
- Initialize text-to-speech (TTS) via Windows SAPI
- Start continuous speech recognition
- Push recognized text into a shared queue

**Core logic:**
- `speak(text)`: wraps Windows SAPI COM voice.
- `start_listening()`: chooses Google or Azure based on config.
- `callback_google(...)`: converts audio to text and puts it in the queue.

---

### 3.2 `main.py`
**Responsibilities:**
- Main event loop and FastAPI server management
- State machine for activation (Arise -> Iris -> Command)
- Advanced intent routing and command cleaning

**Command Parsing Logic:**
- Uses **Regex** to remove redundant prefixes (e.g., "open open word" becomes "word").
- Handles combined commands and state transitions.
- Includes a dedicated "stop assistant" command for instant shutdown.

**Intent routing:**
- `stop assistant` -> Immediate termination
- `open` -> app control (with verification)
- `close` / `stop` -> app control
- `maximize` / `minimize` -> app control
- `volume` -> system control
- `brightness` -> system control
- `play` / `pause` / `next` / `previous` -> media control
- `search` -> web interaction

---

### 3.3 `app_control.py`
**Responsibilities:**
- Launch apps with pre-launch verification
- Close apps and window management

**Launch logic:**
1. Check `APPS` registry in `config.py`.
2. If unknown, use `shutil.which` to check if it exists in the system PATH.
3. If valid, launch via `os.system` (system) or COM (office).
4. If invalid, notify the user that the application was not found.

---

### 3.4 `system_control.py`
**Responsibilities:**
- Volume control (via `pycaw`)
- Brightness control (via `wmi`)
- Global media playback control (via `win32api`)

---

## 4. Concurrency and Thread Safety
- **Listening**: Runs in a background thread.
- **Web Server**: FastAPI runs in a background thread using Uvicorn.
- **Communication**: Thread-safe `queue.Queue` for commands and async WebSockets for UI updates.

---

## 5. Design Patterns Used
- **State Machine**: activation and listening modes.
- **Factory**: app launching by type (System vs Office).
- **Observer/Notify**: Real-time dashboard updates via WebSockets.
- **Strategy**: Pluggable speech recognition providers.

---

## 6. Dependencies
- `SpeechRecognition`, `PyAudio` (Recognition)
- `pywin32`, `WMI`, `pycaw` (System Control)
- `fastapi`, `uvicorn` (Web Dashboard)

---

## 7. Troubleshooting & Common Fixes
- **Office Apps Won't Open**: 
  - Corrupted templates: Delete or rename `Normal.dotm` for Word.
  - Corrupted toolbars: Rename `.xlb` files in AppData for Excel.
  - Printer Issues: Ensure a valid default printer (like "Microsoft Print to PDF") is selected.
- **Microphone Not Detected**: Check Windows Privacy Settings for Microphone access and ensure `PyAudio` is correctly installed.

---

## 8. Changelog
- **v1.0** Initial modular implementation.
- **v1.1** Added brightness control and media keys.
- **v1.2** Added Web Dashboard and WebSocket integration.
- **v1.3** Improved command parsing (Regex), application verification (`shutil`), and "stop assistant" command.

---

## 9. Code Structure
```
Voice_Assistant/
|-- modular_assistant/
|   |-- main.py (Entry point & Router)
|   |-- voice_engine.py (Audio I/O)
|   |-- app_control.py (App/Window mgmt)
|   |-- system_control.py (OS Hardware)
|   |-- web_interaction.py (Web search)
|   `-- config.py (Settings & App list)
|-- static/ (Dashboard UI)
|-- README.md
`-- PROJECT_DOCUMENTATION.md
```

---

**End of Document**
