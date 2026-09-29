import threading
import time
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the static directory
# "/static" is the URL path where files will be accessible (e.g., http://localhost:8000/static/css/style.css)
# directory="static" points to the local folder name on your computer
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/status")
def get_status():
    return {"status": "running"}


# --- Server Threading Logic from before ---
api_server = None


def run_api():
    global api_server
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    api_server = uvicorn.Server(config)
    api_server.run()


def on_closing():
    global api_server
    if api_server is not None:
        api_server.should_exit = True


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        on_closing()
