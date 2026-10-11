from bottle import Bottle, request, response, abort

class ApiV2Component:
    def __init__(self, core, base):
        self.core = core
        self.base = base
        self.app = Bottle()
        
        # Define a sane limit for standard V2 data (e.g., 2 MB)
        self.MAX_V2_JSON_SIZE = 2 * 1024 * 1024 
        # Define a limit for our streamed uploads (e.g., 50 MB)
        self.MAX_V2_STREAM_SIZE = 50 * 1024 * 1024

        self._setup_routes()

    def _setup_routes(self):
        
        # Example 1: Standard POST request with an engineered limit
        @self.app.route('/update', method='POST')
        def modern_update():
            # 1. Enforce a manual safety ceiling based on Content-Length
            content_length = int(request.environ.get('CONTENT_LENGTH') or 0)
            if content_length > self.MAX_V2_JSON_SIZE:
                abort(413, "Payload exceeds version 2 threshold (Max 2MB).")

            # 2. Safe to parse because it fell below our ceiling threshold
            data = request.json
            if not data:
                response.status = 400
                return {"error": "Invalid or missing JSON payload"}

            return {"message": "Success"}


        # Example 2: Streaming large payloads using chunks with constant memory
        @self.app.route('/upload-file', method='POST')
        def upload_stream():
            # 1. Validate total size allotment before processing chunks
            content_length = int(request.environ.get('CONTENT_LENGTH') or 0)
            if content_length > self.MAX_V2_STREAM_SIZE:
                abort(413, f"Stream size exceeds maximum allocation (Max 50MB).")

            # 2. Access the low-level raw read buffer socket directly
            # This bypasses all internal framework parsing layers completely.
            raw_socket_stream = request.body
            
            bytes_written = 0
            chunk_size = 64 * 1024 # 64 KB memory chunks
            
            # Open up a destination file descriptor on disk
            output_filepath = "uploaded_asset.bin"
            with open(output_filepath, "wb") as output_file:
                while bytes_written < content_length:
                    # Calculate how many bytes are remaining to read cleanly
                    remaining = content_length - bytes_written
                    to_read = min(chunk_size, remaining)
                    
                    chunk = raw_socket_stream.read(to_read)
                    if not chunk:
                        break # Unexpected stream cutoff or disconnection
                    
                    output_file.write(chunk)
                    bytes_written += len(chunk)

            response.status = 201
            return {
                "message": "File streamed successfully using constant memory.",
                "total_bytes_saved": bytes_written
            }
