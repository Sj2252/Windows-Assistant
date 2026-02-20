import datetime
import re
from voice_engine import speak, start_listening, command_queue
from app_control import open_app, close_app_by_name, maximize_window, minimize_window, restore_window
from system_control import set_volume_percentage, set_brightness
from web_interaction import search_web

def main():
    # Greeting
    speak("Hello, I am your Windows voice assistant.")
    
    # Start background listening
    listener = start_listening()
    if not listener:
        print("Failed to start listener.")
        return

    # State variables
    session_active = False  # Has user said "Arise"?
    listening_for_command = False  # Did user say just "Iris" and we're waiting for command?
    
    print("State: Dormant - Say 'Arise' to activate")

    # Main loop
    while True:
        try:
            # Block until a command is available
            command = command_queue.get()
            
            # --- State 1: Dormant (waiting for "Arise") ---
            if not session_active:
                if "arise" in command or "arice" in command:
                    print("Session activated!")
                    session_active = True
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
                        # Fall through to command processing
                    else:
                        # User said just "Iris", enter listening mode
                        print("Entering listening mode...")
                        listening_for_command = True
                        speak("Listening")
                        continue
                else:
                    # In active session but no "iris" prefix - ignore
                    continue
            
            # --- Command Processing ---
            
            if "time" in command:
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
                app_name = command.replace("open ", "").strip()
                if app_name:
                    open_app(app_name)

            elif "close" in command or "stop" in command:
                app_name = command.replace("close ", "").replace("stop ", "").strip()
                if app_name:
                    close_app_by_name(app_name)

            elif "max" in command or "maximize" in command:
                app_name = command.replace("maximize ", "").replace("max ", "").strip()
                if app_name:
                    if maximize_window(app_name):
                        speak(f"Maximized {app_name}")

            elif "min" in command or "minimize" in command:
                app_name = command.replace("minimize ", "").replace("min ", "").strip()
                if app_name:
                    if minimize_window(app_name):
                        speak(f"Minimized {app_name}")

            elif "volume" in command or "sound" in command:
                numbers = re.findall(r'\d+', command)
                if numbers:
                    volume_percent = int(numbers[0])
                    set_volume_percentage(volume_percent)

            elif "brightness" in command:
                numbers = re.findall(r'\d+', command)
                if numbers:
                    level = int(numbers[0])
                    set_brightness(level)
                elif "increase" in command:
                    set_brightness(80)
                elif "decrease" in command:
                    set_brightness(30)

            elif "sleep" in command or "go to sleep" in command:
                speak("Going to sleep. Say Arise to wake me.")
                session_active = False
                listening_for_command = False
                print("State: Dormant - Say 'Arise' to activate")

            elif "exit" in command or "quit" in command or "shutdown" in command:
                speak("Thank you. Goodbye!")
                break
            
            # After command, return to active session waiting for "Iris"
            if session_active and not listening_for_command:
                print("State: Active Session - Waiting for 'Iris'")
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
