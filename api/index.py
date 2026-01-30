from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve static files from docs directory
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('docs/index.html', 'text/html')
        elif self.path.startswith('/'):
            # Try to serve file from docs directory
            file_path = 'docs' + self.path
            if os.path.exists(file_path):
                content_type = self.get_content_type(file_path)
                self.serve_file(file_path, content_type)
            else:
                self.send_error(404, 'File not found')
        else:
            self.send_error(404, 'Not found')
    
    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def get_content_type(self, file_path):
        if file_path.endswith('.html'):
            return 'text/html'
        elif file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.json'):
            return 'application/json'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        elif file_path.endswith('.svg'):
            return 'image/svg+xml'
        else:
            return 'application/octet-stream'
