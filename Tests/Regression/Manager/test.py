import tkinter as tk
import threading
import time
import sys

def long_running_task(event):
    while not event.is_set():  # Check if the event is set (signaling to stop)
        # Simulate work
        print("Thread working...")
        root.protocol("WM_DELETE_WINDOW", None)  # Disable the close button
        time.sleep(4)
        root.quit_button = tk.Button(root, text="Quit", command=on_closing)
        root.protocol("WM_DELETE_WINDOW", on_closing)  # Disable the close button
    print("Thread exiting...")

def on_closing():
    print("Shutdown initiated. Waiting for threads to finish...")
    stop_event.set()  # Signal all threads to stop

    # Disable the close button and other GUI elements
    root.quit_button.config(state=tk.DISABLED)
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable the close button
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
        print("joined")
    
    print("All threads have finished.")
    root.destroy()  # Now safely destroy the GUI

root = tk.Tk()

# Create an event to signal threads to stop
stop_event = threading.Event()

# Create and start threads
threads = []
for _ in range(3):
    thread = threading.Thread(target=long_running_task, args=(stop_event,))
    thread.start()
    threads.append(thread)

# Override the window close button event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Add a button to explicitly trigger close event for testing
root.quit_button = tk.Button(root, text="Quit", command=on_closing)
root.quit_button.pack()

try:
    root.mainloop()
except KeyboardInterrupt:
    # Handle Ctrl+C in console to simulate graceful shutdown
    on_closing()
    sys.exit(0)
