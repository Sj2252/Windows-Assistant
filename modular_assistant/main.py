import datetime
import re
import threading
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import webbrowser
import os
import signal
from voice_engine import speak, start_listening, command_queue
from app_control import open_app, close_app_by_name, maximize_window, minimize_window, restore_window
from system_control import set_volume_percentage, set_brightness, control_media
from web_interaction import search_web

# --- API Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_dashboard():
    return FileResponse("static/index.html")

@app.post("/shutdown")
async def shutdown():
    """Endpoint to trigger system shutdown"""
    speak("Shutting down the assistant. Goodbye!")
    # Send signal to terminate the process
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "shutting down"}

@app.get("/apps")
async def get_apps():
    """Endpoint to get the list of supported applications"""
    from config import APPS
    return {"apps": list(APPS.keys())}

# Global for connected UI clients
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

async def notify_ui(event_type, data):
    """Send updates to all connected UI clients"""
    if not connected_clients:
        return
    message = {"type": event_type, "data": data}
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            pass

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

def main():
    # Start API in a background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Auto-open the dashboard in the browser
    webbrowser.open("http://localhost:8000")
    
    # Greeting
    speak("Hello, I am Iris your Windows voice assistant. Say Arise to wake me up.")
    
    # Start background listening
    listener = start_listening()
    if not listener:
        print("Failed to start listener.")
        return

    # Create an event loop for async notifications within the main thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # State variables
    session_active = False  # Has user said "Arise"?
    listening_for_command = False  # Did user say just "Iris" and we're waiting for command?
    
    print("State: Dormant - Say 'Arise' to activate")

    # Main loop
    while True:
        try:
            # Block until a command is available
            command = command_queue.get()
            
            # Send raw text to UI
            loop.run_until_complete(notify_ui("transcript", command))
            
            # --- State 1: Dormant (waiting for "Arise") ---
            if not session_active:
                if "arise" in command or "arice" in command:
                    print("Session activated!")
                    session_active = True
                    loop.run_until_complete(notify_ui("state", "active"))
                    speak("I am ready. Say Iris followed by your command.")
                    print("State: Active Session - Waiting for 'Iris'")
                else:
                    continue  # Ignore everything else
            
            # --- State 2: Active Session ---
            elif session_active:
                # --- State 2a: Listening for Command (after "Iris" alone) ---
                if listening_for_command:
                    print(f"Executing command: {command}")
                    listening_for_command = False
                    # Fall through to command processing
                
                # --- State 2b: Waiting for "Iris" prefix ---
                elif "iris" in command:
                    # Strip "iris" from command
                    command = command.replace("iris", "").strip()
                    
                    # Check if there's a command after "iris"
                    if command:
                        print(f"Executing command: {command}")
                        loop.run_until_complete(notify_ui("state", "listening"))
                        # Fall through to command processing
                    else:
                        # User said just "Iris", enter listening mode
                        print("Entering listening mode...")
                        listening_for_command = True
                        loop.run_until_complete(notify_ui("state", "listening"))
                        speak("Listening")
                        continue
                else:
                    # In active session but no "iris" prefix - ignore
                    continue
            
            # --- Command Processing ---
            
            if any(k in command for k in ["exit", "quit", "shutdown", "stop assistant", "stop the assistant"]):
                speak("Thank you. Goodbye!")
                break

            elif "time" in command:
                time_str = datetime.datetime.now().strftime("%H:%M")
                speak(f"The time is {time_str}")

            elif "search" in command:
                query = command.replace("search for ", "").replace("search ", "").strip()
                if query:
                    search_web(query)
                else:
                    speak("What would you like to search for?")
                    pass 

            elif "open" in command:
                # Remove "open" prefix(es)
                app_name = re.sub(r'^(open\s*)+', '', command).strip()
                if app_name:
                    open_app(app_name)
                else:
                    speak("What application would you like me to open?")

            elif "close" in command or "stop" in command:
                # Remove "close" or "stop" prefix(es)
                app_name = re.sub(r'^(close\s*|stop\s*)+', '', command).strip()
                if app_name:
                    close_app_by_name(app_name)
                else:
                    speak("Which application should I close?")

            elif "max" in command or "maximize" in command:
                app_name = re.sub(r'^(maximize\s*|max\s*)+', '', command).strip()
                if app_name:
                    if maximize_window(app_name):
                        speak(f"Maximized {app_name}")
                else:
                    speak("Which window would you like me to maximize?")

            elif "min" in command or "minimize" in command:
                app_name = re.sub(r'^(minimize\s*|min\s*)+', '', command).strip()
                if app_name:
                    if minimize_window(app_name):
                        speak(f"Minimized {app_name}")
                else:
                    speak("Which window would you like me to minimize?")

            elif "volume" in command or "sound" in command:
                numbers = re.findall(r'\d+', command)
                if numbers:
                    volume_percent = int(numbers[0])
                    set_volume_percentage(volume_percent)
                    loop.run_until_complete(notify_ui("volume", volume_percent))

            elif "brightness" in command:
                numbers = re.findall(r'\d+', command)
                if numbers:
                    level = int(numbers[0])
                    set_brightness(level)
                    loop.run_until_complete(notify_ui("brightness", level))
                elif "increase" in command:
                    set_brightness(80)
                    loop.run_until_complete(notify_ui("brightness", 80))
                elif "decrease" in command:
                    set_brightness(30)
                    loop.run_until_complete(notify_ui("brightness", 30))

            elif "sleep" in command or "go to sleep" in command:
                speak("Going to sleep. Say Arise to wake me.")
                session_active = False
                listening_for_command = False
                loop.run_until_complete(notify_ui("state", "dormant"))
                print("State: Dormant - Say 'Arise' to activate")

            elif "play" in command and "music" in command:
                control_media("play")
            
            elif "pause" in command and "music" in command:
                control_media("pause")
            
            elif "next" in command and "song" in command:
                control_media("next")
            
            elif "previous" in command and "song" in command:
                control_media("previous")

            elif "spotify" in command:
                if "open" in command:
                    open_app("spotify")
                elif "close" in command or "stop" in command:
                    close_app_by_name("spotify")
                elif "play" in command:
                    control_media("play")
                elif "pause" in command:
                    control_media("pause")
                elif "next" in command:
                    control_media("next")
                elif "previous" in command:
                    control_media("previous")


            # After command, return to active session waiting for "Iris"
            if session_active and not listening_for_command:
                loop.run_until_complete(notify_ui("state", "active"))
                print("State: Active Session - Waiting for 'Iris'")
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
