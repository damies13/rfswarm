import threading
import time
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/status")
def get_status():
    return {"status": "running"}


# Global variable to store our server instance
api_server = None


def run_api():
    global api_server

    # 1. Configure the server instead of using uvicorn.run directly
    config = uvicorn.Config(
        app, host="127.0.0.1", port=8000, log_level="info", loop="asyncio"
    )
    api_server = uvicorn.Server(config)

    # 2. Run the server (this blocks the thread until told to exit)
    api_server.run()


def on_closing():
    global api_server
    print("\n[Shutdown] Shutting down application components...")

    # 3. Tell the Uvicorn server to stop cleanly
    if api_server is not None:
        print("[Shutdown] Stopping FastAPI server...")
        api_server.should_exit = True

    print("[Shutdown] Cleanup complete.")


if __name__ == "__main__":
    # Start FastAPI in a background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    print("Main application is processing data... (Press Ctrl+C to simulate closing)")

    try:
        # Simulate your application's lifecycle loop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 4. Trigger your closing function
        on_closing()
