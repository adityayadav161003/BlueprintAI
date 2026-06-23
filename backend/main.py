import os
import sys
import json
import time
import socketserver

# Ensure the parent directory is in sys.path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


# Simple custom .env loader to avoid external dependencies
def load_env():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        # Strip optional quotes
                        if val.startswith('"') and val.endswith('"'):
                            val = val[1:-1]
                        elif val.startswith("'") and val.endswith("'"):
                            val = val[1:-1]
                        if key not in os.environ:
                            os.environ[key] = val

# Load environment
load_env()
# Ensure system variables (like Docker overridden ones) have precedence
if "PORT" in os.environ:
    pass
else:
    # If not overridden by Docker, load_env already loaded from .env
    pass

# Import local components (now dependency-free)
from backend.models.model_provider import ModelProvider
from backend.memory.conversation_store import ConversationStore
from backend.agents.business_analyst import BusinessAnalyst
from backend.agents.product_manager import ProductManager
from backend.agents.qa_critic import QACritic
from backend.agents.synthesis import Synthesis

# Initialize singleton instances (uses ModelProvider for hybrid online/offline orchestration)
groq_client = ModelProvider()
store = ConversationStore()

class BlueprintAIRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for all responses
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Route: GET /api/history
        if path == "/api/history":
            try:
                history = store.list_generations()
                response_data = json.dumps(history).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_data)))
                self.end_headers()
                self.wfile.write(response_data)
            except Exception as e:
                self.send_error_response(500, f"Error listing history: {str(e)}")
            return

        # Route: GET /api/history/{id}
        elif path.startswith("/api/history/"):
            try:
                project_id = path.split("/")[-1]
                data = store.get_generation(project_id)
                if not data:
                    self.send_error_response(404, "Generation session not found")
                    return
                response_data = json.dumps(data).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_data)))
                self.end_headers()
                self.wfile.write(response_data)
            except Exception as e:
                self.send_error_response(500, f"Error retrieving history details: {str(e)}")
            return

        # Route: Serve static files
        else:
            self.serve_static_file(path)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Route: POST /api/generate
        if path == "/api/generate":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                req_json = json.loads(post_data.decode('utf-8'))
                prompt = req_json.get("prompt", "").strip()
                industry = req_json.get("industry", "").strip()
            except Exception:
                self.send_error_response(400, "Invalid JSON payload")
                return

            if not prompt or not industry:
                self.send_error_response(400, "Prompt and Industry are required")
                return

            # Start SSE Stream
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            self.handle_sse_stream(prompt, industry)
            return

        else:
            self.send_error_response(404, "API endpoint not found")

    def handle_sse_stream(self, prompt: str, industry: str):
        """
        Executes the multi-agent pipeline and writes real-time SSE events to the client.
        """
        ba_output = ""
        pm_output = ""
        qa_output = ""
        final_prd = ""

        try:
            # Helper to write SSE event line
            def send_event(event_name, text_value=None, project_id=None):
                payload = {"event": event_name}
                if text_value is not None:
                    payload["text"] = text_value
                if project_id is not None:
                    payload["project_id"] = project_id
                
                line = f"data: {json.dumps(payload)}\n\n"
                self.wfile.write(line.encode('utf-8'))
                self.wfile.flush()

            # --- STAGE 1: Business Analyst ---
            send_event("status", "Business Analyst is analyzing the market & competitors...")
            send_event("ba_start")
            
            ba_agent = BusinessAnalyst()
            for chunk in ba_agent.run(groq_client, prompt, industry):
                ba_output += chunk
                send_event("ba_chunk", chunk)
            send_event("ba_done", ba_output)
            time.sleep(0.5)

            # --- STAGE 2: Product Manager ---
            send_event("status", "Product Manager is drafting the initial PRD spec...")
            send_event("pm_start")
            
            pm_agent = ProductManager()
            for chunk in pm_agent.run(groq_client, ba_output, prompt, industry):
                pm_output += chunk
                send_event("pm_chunk", chunk)
            send_event("pm_done", pm_output)
            time.sleep(0.5)

            # --- STAGE 3: QA Critic ---
            send_event("status", "QA Critic is stress-testing requirements for gaps and risks...")
            send_event("qa_start")
            
            qa_agent = QACritic()
            for chunk in qa_agent.run(groq_client, pm_output, prompt, industry):
                qa_output += chunk
                send_event("qa_chunk", chunk)
            send_event("qa_done", qa_output)
            time.sleep(0.5)

            # --- STAGE 4: Synthesis ---
            send_event("status", "Synthesis Agent is compiling feedback and generating the final board-ready PRD...")
            send_event("syn_start")
            
            syn_agent = Synthesis()
            for chunk in syn_agent.run(groq_client, ba_output, pm_output, qa_output, prompt, industry):
                final_prd += chunk
                send_event("syn_chunk", chunk)
            send_event("syn_done", final_prd)
            time.sleep(0.5)

            # --- SAVE TO STORAGE ---
            send_event("status", "Saving complete session documents to local store...")
            project_id = store.save_generation(
                prompt=prompt,
                industry=industry,
                ba_output=ba_output,
                pm_output=pm_output,
                qa_output=qa_output,
                final_prd=final_prd
            )
            
            send_event("done", project_id=project_id)

        except Exception as e:
            try:
                send_event("error", f"Pipeline failed: {str(e)}")
            except Exception:
                pass # Client disconnected

    def serve_static_file(self, path: str):
        """
        Serves HTML/CSS/JS frontend files.
        """
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(os.path.dirname(backend_dir), "frontend")
        
        # Normalize and prevent directory traversal
        if path == "/" or not path:
            path = "/index.html"
            
        # Strip leading slash and resolve
        safe_path = os.path.normpath(path.lstrip("/"))
        file_path = os.path.join(frontend_dir, safe_path)
        
        # Security check: verify that the resolved path lies within the frontend directory
        if not os.path.commonpath([frontend_dir]) == os.path.commonpath([frontend_dir, file_path]):
            self.send_error_response(403, "Access Denied")
            return

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.send_error_response(404, "File Not Found")
            return

        # Determine Content-Type
        _, ext = os.path.splitext(file_path)
        content_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".json": "application/json",
            ".ico": "image/x-icon"
        }
        content_type = content_types.get(ext.lower(), "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error_response(500, f"Error reading static asset: {str(e)}")

    def send_error_response(self, code: int, message: str):
        response_data = json.dumps({"error": message}).encode('utf-8')
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)


def run(port=8000):
    server_address = ('', port)
    # ThreadingHTTPServer spawns a new thread for each connection, allowing concurrent requests
    # and streaming SSE responses without blocking other users or static file reads.
    httpd = ThreadingHTTPServer(server_address, BlueprintAIRequestHandler)
    print(f"BlueprintAI Web Application running locally on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    run(port)
