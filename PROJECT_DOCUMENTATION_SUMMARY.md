# Windows Voice Assistant - Project Documentation (Module Summary)

**Project Name:** Windows Voice Assistant  
**Date:** March 5, 2026  
**Repository:** Sj2252/Windows-Assistant

---

## Purpose
A premium Windows voice assistant with a real-time web dashboard. It listens continuously and executes system/app actions based on voice commands with high precision.

---

## Modules (What They Do)
- `voice_engine.py`: Speech recognition + TTS + Queue management.
- `main.py`: Event loop + FastAPI Server + Regex Router.
- `app_control.py`: Verified app launching + Window management.
- `system_control.py`: Volume, Brightness, and Media control.
- `web_interaction.py`: Web searches.
- `config.py`: Settings, API keys, and App Registry.

---

## Core Logic (Short)
1. **Listen**: Background thread recognizes speech.
2. **Clean**: Regex removes redundant keywords (e.g., "open open").
3. **Verify**: Checks if application exists before announcing "Opening".
4. **Route**: Intent matches calls specialized handler.
5. **Update**: Dashboard reflects action via WebSockets.
6. **Speak**: Confirms action via Windows TTS.

---

## Key Patterns
- **Dormant/Active States** with 3D status feedback.
- **WebSocket Observer** for real-time UI synchronization.
- **Dynamic Audio Visualizer** for instant mic feedback.
- **3D JARVIS Globe** with multi-axis holographic rotation.
- **Regex Routing** for robust command recognition.

---

**End of Document**

