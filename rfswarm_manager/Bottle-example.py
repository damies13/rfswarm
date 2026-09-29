import os
import threading
import time
from wsgiref.simple_server import make_server, WSGIServer
from bottle import Bottle, request, static_file, WSGIRefServer

# Create explicit Bottle instance
app = Bottle()

# Define the absolute path to your static files directory
# (Creates a folder named 'public' in the same directory as this script)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

# 1. Route to serve static files
@app.route('/static/<filepath:path>')
def server_static(filepath):
    """Serves files (HTML, CSS, JS, Images) from the static directory."""
    return static_file(filepath, root=STATIC_DIR)

# 2. Dynamic status API route
@app.route('/api/status')
def status():
    return {"status": "running", "threads": threading.active_count()}


# 3. Custom Server class to expose shutdown functionality
class ShareableWSGIServer(WSGIRefServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = None

    def run(self, app):
        # We override run to save a reference to the underlying server instance
        handler_cls = self.options.get('handler_class', self.quiet_handler if self.quiet else None)
        server_cls = self.options.get('server_class', WSGIServer)
        
        self.server = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.server.serve_forever()

    def stop(self):
        # Gracefully stops the serve_forever loop and closes the socket
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("[Bottle] Web server completely stopped.")


# Global server instance tracking wrapper
server_instance = ShareableWSGIServer(host='localhost', port=8080, quiet=True)

def run_embedded_server():
    print("[Bottle] Starting background server at http://localhost:8080/static/index.html")
    # Launch bottle using our custom server manager
    app.run(server=server_instance)

def on_closing():
    """Trigger this function when your main application is closing (e.g., WM_DELETE_WINDOW)."""
    print("\n[Main App] shutdown event detected. Cleaning up web server...")
    
    # 1. Stop the web server loop cleanly
    server_instance.stop()
    
    # 2. Wait for background thread to exit cleanly if required
    server_thread.join(timeout=3)
    print("[Main App] Cleanup complete. Exiting application safely.")

if __name__ == '__main__':
    # Setup dummy static directory and file for testing
    os.makedirs(STATIC_DIR, exist_ok=True)
    with open(os.path.join(STATIC_DIR, 'index.html'), 'w') as f:
        f.write("<h1>Hello from Embedded Static Files Folder!</h1>")

    # Start the web server thread
    server_thread = threading.Thread(target=run_embedded_server, daemon=True)
    server_thread.start()

    # Simulate main application life cycle
    try:
        print("[Main App] Working... (Press Ctrl+C to trigger on_closing)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Pass control directly to your custom closing trigger
        on_closing()
