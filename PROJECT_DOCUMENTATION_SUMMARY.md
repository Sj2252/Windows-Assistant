# Windows Voice Assistant - Project Documentation (Module Summary)

**Project Name:** Windows Voice Assistant  
**Date:** February 13, 2026  
**Repository:** Sj2252/Windows-Assistant

---

## Purpose
A Windows voice assistant that listens continuously and executes system/app actions based on voice commands.

---

## Modules (What They Do)
- `voice_engine.py`: Speech recognition + text-to-speech, pushes commands to a queue.
- `main.py`: State machine + intent routing.
- `app_control.py`: Launch/close apps, window control.
- `system_control.py`: Volume control.
- `web_interaction.py`: Open web search in browser.
- `config.py`: App registry + API configuration.

---

## Core Logic (Short)
1. Background listener recognizes speech.
2. Callback puts text into queue.
3. Main loop reads queue and checks state.
4. Router detects intent and calls handler.
5. Handler performs action and speaks feedback.

---

## Key Patterns
- State machine for activation
- Producer/consumer queue
- Factory pattern for app launching

---

**End of Document**
