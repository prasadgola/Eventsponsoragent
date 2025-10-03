#!/usr/bin/env python3

import os
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.error import HTTPError

class FrontendHandler(BaseHTTPRequestHandler):
    ADK_SERVER_URL = os.getenv("ADK_SERVER_URL", "http://127.0.0.1:8000")
    
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                html_content = html_content.replace(
                    "const API_BASE = 'http://localhost:8080';", 
                    "const API_BASE = '';"
                )
                
                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
                return
            except FileNotFoundError:
                self.send_response(404)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "HTML not found"}).encode())
                return
        
        if self.path == '/health':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            try:
                req = urllib.request.Request(f"{self.ADK_SERVER_URL}/docs", timeout=3)
                with urllib.request.urlopen(req) as response:
                    adk_status = "healthy" if response.status == 200 else "unhealthy"
            except:
                adk_status = "unavailable"
            
            health_data = {
                "status": "running",
                "adk_server": self.ADK_SERVER_URL,
                "adk_status": adk_status
            }
            
            self.wfile.write(json.dumps(health_data).encode())
            return
        
        self._forward_to_adk('GET')
    
    def do_POST(self):
        print(f"📨 POST request: {self.path}")
        
        if self.path == '/run':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                request_json = json.loads(post_data.decode())
                
                response_data = self._run_agent(post_data)
                
                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_data)
                
            except HTTPError as e:
                if e.code == 404:
                    print("🤔 Session not found, creating...")
                    self._create_session(request_json)
                    
                    print("🔄 Retrying...")
                    response_data = self._run_agent(post_data)
                    
                    self.send_response(200)
                    self._set_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response_data)
                else:
                    self._handle_error(e)
            except Exception as e:
                self._handle_error(e)

        elif self.path == '/upload-document':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # Forward to services /upload endpoint (not /analyze)
                req = urllib.request.Request(
                    'http://localhost:8001/documents/upload',
                    data=post_data,
                    headers={'Content-Type': content_type}
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    response_data = response.read()
                    
                    self.send_response(200)
                    self._set_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response_data)
                    
            except Exception as e:
                print(f"Upload error: {e}")
                self._handle_error(e)
            return
        

    def _run_agent(self, post_data):
        req = urllib.request.Request(
            f"{self.ADK_SERVER_URL}/run",
            data=post_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"▶️ Running agent...")
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read()

    def _create_session(self, request_json):
        app_name = request_json.get("app_name")
        user_id = request_json.get("user_id")
        session_id = request_json.get("session_id")
        
        session_url = f"{self.ADK_SERVER_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        session_data = json.dumps({"state": {}}).encode()
        
        req = urllib.request.Request(
            session_url,
            data=session_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        print(f"✨ Creating session...")
        with urllib.request.urlopen(req) as response:
            print(f"✅ Session created")

    def _handle_error(self, e):
        print(f"❌ Error: {e}")
        self.send_response(500)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _forward_to_adk(self, method):
        try:
            url = f"{self.ADK_SERVER_URL}{self.path}"
            
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else None
                req = urllib.request.Request(url, data=post_data, headers={'Content-Type': 'application/json'})
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = response.read()
                
                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.end_headers()
                self.wfile.write(response_data)
        except Exception as e:
            self._handle_error(e)

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    
    print(f"🚀 Frontend Server")
    print(f"📍 http://{HOST}:{PORT}")
    print(f"🔗 ADK: {os.getenv('ADK_SERVER_URL', 'http://127.0.0.1:8000')}")
    
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, FrontendHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()