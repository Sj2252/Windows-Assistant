# Windows Voice Assistant - Project Documentation (Technical Summary)

**Project Name:** Windows Voice Assistant  
**Date:** March 5, 2026  
**Repository:** Sj2252/Windows-Assistant

---

## Architecture (Condensed)
```
Mic -> SR -> Background Thread -> Queue -> Regex Router -> Control Modules -> TTS
                                             |
                                             -> FastAPI -> WebSockets -> Dashboard
```

---

## Modules + Key Logic

### `voice_engine.py` (Audio I/O)
- **SAPI TTS**: `win32com.client.Dispatch("SAPI.SpVoice")`
- **Speech Recognition**: Uses `recognize_google` or `start_listening_azure` in background.

### `main.py` (Entry & Router)
- **Queue Reading**: `command_queue.get()` blocks.
- **Regex Routing**: Uses `re.sub(r'^(prefix\s*)+', '', command)` to clean input.
- **Web UI**: Serves static dashboard and pushes events via `notify_ui` (async WebSockets).
- **Termination**: Explicit `top-of-router` check for "stop assistant".

### `app_control.py` (App Management)
- **Shutil Check**: `shutil.which(app_name)` verifies executable existence.
- **Launch Strategy**: Registry lookup -> System start -> COM Automation.
- **Win32 API**: Uses `ShowWindow` and `PostMessage` for window state management.

### `system_control.py` (OS Hardware)
- **Audio**: `pycaw` sets Master scalar (0.0-1.0).
- **Brightness**: `wmi` sets monitor percentage level.
- **Media**: `win32api` sends virtual key codes for hardware media buttons.

---

## Key Patterns
- **State Machine**: (Dormant -> Active -> Listening) manages wake-word persistence.
- **WebSocket Observer**: Pushes all state changes and transcripts to the frontend.
- **Regex Sanitization**: Handles the "open open" and redundant keyword errors.
- **Audio Visualizer**: Uses Web Audio API `AnalyserNode` for real-time Fourier analysis.
- **3D CSS Transforms**: Implements `perspective` and `rotate3d` for the holographic HUD.

---

## Dependencies
- `fastapi`, `uvicorn` (Server)
- `SpeechRecognition`, `PyAudio` (Audio)
- `pywin32`, `WMI`, `pycaw` (Windows API)

---

## Example Snippets
```python
# Regex prefix cleaning
app_name = re.sub(r'^(open\s*)+', '', command).strip()

# Verification before launch
if shutil.which(app_lower):
    subprocess.Popen(app_lower, shell=True)
```

---

**End of Document**
