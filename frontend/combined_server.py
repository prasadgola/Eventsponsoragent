#!/usr/bin/env python3

import os
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.error import HTTPError

class CombinedServerHandler(BaseHTTPRequestHandler):
    # ADK server URL - internal communication
    ADK_SERVER_URL = os.getenv("ADK_SERVER_URL", "http://127.0.0.1:8000")
    
    def _set_cors_headers(self):
        """Set CORS headers for all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        
        # Serve the frontend HTML at root path
        if self.path == '/' or self.path == '/index.html':
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                # Replace the API_BASE in the HTML to use relative URLs
                # This ensures the frontend talks to the same server it's served from
                html_content = html_content.replace(
                    "const API_BASE = 'http://localhost:8080';", 
                    "const API_BASE = '';"  # Use relative URLs
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
                error_data = {"error": "Frontend HTML file not found"}
                self.wfile.write(json.dumps(error_data).encode())
                return
        
        # Health check endpoint
        if self.path == '/health':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Quick health check
            try:
                req = urllib.request.Request(f"{self.ADK_SERVER_URL}/docs", timeout=3)
                with urllib.request.urlopen(req) as response:
                    adk_status = "healthy" if response.status == 200 else "unhealthy"
            except:
                adk_status = "unavailable"
            
            health_data = {
                "status": "running",
                "adk_server": self.ADK_SERVER_URL,
                "adk_status": adk_status,
                "port": os.getenv('PORT', '8080'),
                "frontend": "embedded"
            }
            
            self.wfile.write(json.dumps(health_data).encode())
            return
        
        # API info endpoint
        if self.path == '/api' or self.path == '/api/info':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            info_data = {
                "service": "ADK Event Sponsor Assistant",
                "status": "running",
                "endpoints": {
                    "GET /": "Frontend UI (HTML page)",
                    "POST /run": "Send message to agent",
                    "GET /health": "Health check",
                    "GET /debug": "Debug information"
                },
                "adk_server": self.ADK_SERVER_URL,
                "mode": "combined_server"
            }
            
            self.wfile.write(json.dumps(info_data, indent=2).encode())
            return
        
        # Debug endpoint
        if self.path == '/debug':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            debug_data = {
                "proxy_server": self.ADK_SERVER_URL,
                "mode": "combined_server",
                "environment": {
                    "PORT": os.getenv('PORT'),
                    "HOST": os.getenv('HOST', '0.0.0.0'),
                    "ADK_SERVER_URL": self.ADK_SERVER_URL
                }
            }
            
            # Test ADK endpoints
            test_endpoints = ['/docs', '/openapi.json', '/list-apps']
            for endpoint in test_endpoints:
                try:
                    req = urllib.request.Request(f"{self.ADK_SERVER_URL}{endpoint}", timeout=2)
                    with urllib.request.urlopen(req) as response:
                        debug_data[f"adk_{endpoint.replace('/', '_')}"] = {"status": response.status, "available": True}
                except Exception as e:
                    debug_data[f"adk_{endpoint.replace('/', '_')}"] = {"available": False, "error": str(e)[:100]}
            
            self.wfile.write(json.dumps(debug_data, indent=2).encode())
            return
        
        # Forward other GET requests to ADK
        self._forward_to_adk('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        
        print(f"📨 Received POST request to: {self.path}")
        
        if self.path == '/run':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                request_json = json.loads(post_data.decode())
                
                # First, try to run the agent
                response_data = self._run_agent(post_data)
                
                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_data)
                
            except HTTPError as e:
                # If the session doesn't exist (404), create it and retry
                if e.code == 404:
                    print("🤔 Session not found. Creating a new one...")
                    self._create_session(request_json)
                    
                    print("🔄 Retrying to run the agent...")
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
        else:
            self._forward_to_adk('POST')

    def _run_agent(self, post_data):
        """Forwards the request to the ADK's /run endpoint."""
        req = urllib.request.Request(
            f"{self.ADK_SERVER_URL}/run",
            data=post_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"▶️  Running agent with payload: {post_data.decode()[:200]}...")
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read()

    def _create_session(self, request_json):
        """Creates a new session using the details from the request."""
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
        print(f"✨ Creating session at: {session_url}")
        with urllib.request.urlopen(req) as response:
            print(f"✅ Session created with status: {response.status}")

    def _handle_error(self, e):
        """Sends a generic error response."""
        print(f"❌ Error: {e}")
        self.send_response(500)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        error_data = {"error": str(e)}
        self.wfile.write(json.dumps(error_data).encode())

    def _forward_to_adk(self, method):
        """Generic method to forward requests to ADK server"""
        try:
            url = f"{self.ADK_SERVER_URL}{self.path}"
            
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else None
                
                req = urllib.request.Request(
                    url,
                    data=post_data,
                    headers={'Content-Type': self.headers.get('Content-Type', 'application/json')}
                )
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = response.read()
                
                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.end_headers()
                self.wfile.write(response_data)
                
        except HTTPError as e:
            self._handle_error(e)
            
        except Exception as e:
            self._handle_error(e)

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

if __name__ == '__main__':
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    
    print(f"🚀 Starting ADK Combined Server (Frontend + API)")
    print(f"📍 Listening on: http://{HOST}:{PORT}")
    print(f"🌐 Frontend UI: http://{HOST}:{PORT}/")
    print(f"🔗 ADK Server: {os.getenv('ADK_SERVER_URL', 'http://127.0.0.1:8000')}")
    print(f"🎯 API endpoint: POST /run")
    print(f"❤️  Health check: GET /health")
    
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, CombinedServerHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()