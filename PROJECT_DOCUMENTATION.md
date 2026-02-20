# Windows Voice Assistant - Project Documentation (Full Logic)

**Project Name:** Windows Voice Assistant  
**Date:** February 13, 2026  
**Repository:** Sj2252/Windows-Assistant

---

## 1. Overview
This project is a modular Windows voice assistant. It listens continuously, converts speech to text, routes intent, and executes system/app actions. The system is built around:
- A background listener thread
- A thread-safe queue
- A small state machine
- Specialized control modules

---

## 2. High-Level Flow
```
Microphone -> Speech Recognition -> Callback -> Queue -> State Manager -> Router -> Handler -> TTS -> Speaker
```

1. The voice engine listens in the background.
2. The speech recognizer fires a callback with recognized text.
3. The callback pushes text into a thread-safe queue.
4. The main loop blocks on the queue, then processes commands.
5. The state machine determines whether the system is dormant, active, or listening.
6. The router detects intent and calls the correct module.
7. The handler executes the action and speaks feedback.

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

**Key idea:** the callback runs in a background thread and never blocks the main loop.

---

### 3.2 `main.py`
**Responsibilities:**
- Main event loop
- State machine for activation
- Intent routing

**State machine logic:**
- Dormant: ignores input until wake word.
- Active: accepts commands with prefix.
- Listening: waits for next command after wake word only.

**Core loop behavior:**
1. Block on queue: `command_queue.get()`
2. If dormant, check for "arise" to activate
3. If active, check for "iris" prefix
4. If only wake word, enter listening mode
5. Else parse intent and route

**Intent routing:**
- `open` -> app control
- `close` / `stop` -> app control
- `maximize` / `minimize` / `restore` -> app control
- `volume` -> system control
- `search` -> web interaction

---

### 3.3 `app_control.py`
**Responsibilities:**
- Launch apps
- Close apps
- Window management

**Launch logic (Factory pattern):**
- Check `APPS` registry in `config.py`.
- If type is `system`, launch via shell `start`.
- If type is `office`, launch via COM automation.

**Window control:**
- Locate window by exact or partial title.
- Use Win32 API to maximize, minimize, restore, or close.

---

### 3.4 `system_control.py`
**Responsibilities:**
- Volume control

**Core logic:**
- Validate 0–100 input
- Convert percent to scalar (0.0–1.0)
- Use `pycaw` to set master volume

---

### 3.5 `web_interaction.py`
**Responsibilities:**
- Perform web searches

**Core logic:**
- URL-encode query
- Use ShellExecute to open browser with search URL

---

### 3.6 `config.py`
**Responsibilities:**
- Centralized configuration
- Application registry

**Core logic:**
- `APPS` maps app names to launch metadata
- Azure keys and config flags stored here

---

## 4. Concurrency and Thread Safety
- Recognition runs in a background thread.
- The queue is the only shared state.
- The main loop blocks on queue reads, so CPU usage stays low.

---

## 5. Design Patterns Used
- State Machine: activation and listening modes
- Factory: app launching by type
- Producer/Consumer: background listener + main loop
- Abstraction: simple helper functions hide OS/COM complexity

---

## 6. Dependencies
- `SpeechRecognition`
- `pywin32`
- `pycaw`
- `azure-cognitiveservices-speech` (optional)

---

## 7. Extending the Project
- Add apps by updating `APPS` in `config.py`
- Add commands by extending routing in `main.py`
- Add new modules and import them in `main.py`

---

## 8. Changelog
**v1.0** Initial implementation: voice engine, router, app control, system control, web interaction, config.

---

## 9. Code Structure
```
Voice_Assistant/
|-- modular_assistant/
|   |-- main.py
|   |-- voice_engine.py
|   |-- app_control.py
|   |-- system_control.py
|   |-- web_interaction.py
|   `-- config.py
|-- README.md
`-- PROJECT_DOCUMENTATION.md
```

---

**End of Beginning**
