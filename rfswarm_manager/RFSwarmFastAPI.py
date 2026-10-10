# fastapiserver.py
import os
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import the routers
from api import v1

class RFSwarmFastAPI:
    # def __init__(self, core, host="127.0.0.1", port=8000):
    def __init__(self, base, core, host="0.0.0.0", port=8139):
        self.host = host
        self.port = port
        self.thread = None
        self.server = None
        
        base.debugmsg(5, "FastAPI starting")

        # Create the underlying FastAPI instance
        self.app = FastAPI()
        

        # Crucial Step: Attach your parent application's core reference to the app state
        self.app.state.base = base
        self.app.state.core = core
        
        # Setup static files and routers
        # Setup static files 
        # webuidir = os.path.join(os.path.dirname(__file__), "webui")
        # base.debugmsg(5, "webui:", webuidir)
        # self.app.mount("/webui", StaticFiles(directory=webuidir), name="webui")

        # Setup routers
        self.app.include_router(v1.router)

        base.debugmsg(5, "FastAPI started")

    def _run(self):
        config = uvicorn.Config(
            self.app, host=self.host, port=self.port, log_level="info"
        )
        self.server = uvicorn.Server(config)
        self.server.run()

    def start(self):
        """Starts the FastAPI server in a background thread."""
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        """Cleanly stops the server."""
        if self.server is not None:
            print("[FastApiServer] Triggering server shutdown...")
            self.server.should_exit = True
