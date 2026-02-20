# Windows Voice Assistant - Project Documentation (Technical Summary)

**Project Name:** Windows Voice Assistant  
**Date:** February 13, 2026  
**Repository:** Sj2252/Windows-Assistant

---

## Architecture (Condensed)
```
Mic -> SR -> Callback -> Queue -> State -> Router -> Control -> TTS -> Speaker
```

---

## Modules + Key Logic

### `voice_engine.py`
- `speak(text)`: Windows SAPI via COM
- `start_listening()`: Google or Azure based on config
- Background callback: converts audio -> text -> queue

### `main.py`
- `command_queue.get()` blocks until input
- States: Dormant, Active, Listening
- Routes intents via keyword matching

### `app_control.py`
- Reads `APPS` registry
- Launch by type:
  - `system`: `os.system("start ...")`
  - `office`: COM automation
- Window control using Win32 API

### `system_control.py`
- `set_volume_percentage(p)` converts to scalar and sets volume with `pycaw`

### `web_interaction.py`
- URL-encode query and open browser

### `config.py`
- App registry + Azure keys and flags

---

## Key Patterns
- State machine for activation and command scope
- Producer/consumer queue for threading
- Factory for app launch strategy

---

## Dependencies
- `SpeechRecognition`
- `pywin32`
- `pycaw`
- `azure-cognitiveservices-speech` (optional)

---

## Example Snippets
```python
# Start listening with chosen provider
if USE_AZURE_SPEECH:
    start_listening_azure()
else:
    start_listening_google()
```

```python
# Router (simplified)
if "open" in command:
    open_app(name)
elif "volume" in command:
    set_volume_percentage(p)
```

```python
# Volume conversion
volume_interface.SetMasterVolumeLevelScalar(percentage / 100.0, None)
```

---

**End of Document**
