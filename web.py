"""
SnapDiet Web Service Entrypoint for Vercel Multi-Service Deployment.
Provides the entrypoint callable 'app' and 'handler' for the 'app' service,
reading the bound 'API_URL' to communicate with the internal 'api' service.
"""
import os
import ssl
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

def get_api_status():
    api_url = os.environ.get("API_URL", "").rstrip("/")
    if not api_url:
        return {"status": "not_bound", "message": "API_URL environment variable is not set"}
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(f"{api_url}/", headers={"User-Agent": "SnapDiet-AppService"})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {"status": "connected", "api_url": api_url, "response": data}
    except Exception as e:
        try:
            req = urllib.request.Request(f"{api_url}/api", headers={"User-Agent": "SnapDiet-AppService"})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                data = json.loads(response.read().decode("utf-8"))
                return {"status": "connected", "api_url": api_url, "response": data}
        except Exception:
            return {"status": "configured", "api_url": api_url, "note": str(e)}

def build_status_payload():
    api_info = get_api_status()
    return json.dumps({
        "service": "SnapDiet Web App",
        "version": "1.0.0",
        "binding": api_info,
        "status": "healthy"
    }, indent=2).encode("utf-8")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SnapDiet - AI Nutrition & Health Platform</title>
  <style>
    :root {
      --primary: #10B981;
      --primary-dark: #059669;
      --bg: #0F172A;
      --card-bg: #1E293B;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --border: #334155;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      max-width: 680px;
      width: 100%;
      padding: 32px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 16px;
    }
    .badge-service {
      background: rgba(16, 185, 129, 0.15);
      color: var(--primary);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    h1 {
      font-size: 28px;
      font-weight: 800;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #34D399 0%, #10B981 50%, #059669 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p.subtitle {
      color: var(--text-muted);
      font-size: 15px;
      line-height: 1.5;
      margin-bottom: 20px;
    }
    .status-panel {
      background: #0B1120;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 18px;
      margin-bottom: 20px;
    }
    .status-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 0;
      font-size: 13px;
    }
    .status-row:not(:last-child) {
      border-bottom: 1px solid rgba(51, 65, 85, 0.5);
    }
    .status-label { color: var(--text-muted); }
    .status-val { font-weight: 600; font-family: monospace; }
    .links {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }
    .btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 16px;
      border-radius: 10px;
      text-decoration: none;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.2s ease;
    }
    .btn-primary {
      background: var(--primary);
      color: #0F172A;
    }
    .btn-primary:hover {
      background: var(--primary-dark);
      color: #FFF;
    }
    .btn-secondary {
      background: #334155;
      color: var(--text);
    }
    .btn-secondary:hover {
      background: #475569;
    }
    .btn-full {
      grid-column: span 2;
    }
    .output-box {
      background: #0B1120;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      margin-top: 12px;
      font-family: monospace;
      font-size: 12px;
      color: #38BDF8;
      display: none;
      white-space: pre-wrap;
      word-break: break-all;
      max-height: 200px;
      overflow-y: auto;
    }
    @media (max-width: 600px) {
      .card { padding: 20px; }
      .links { grid-template-columns: 1fr; }
      .btn-full { grid-column: span 1; }
    }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge badge-service">Vercel Multi-Service Project</span>
    <h1>🥗 SnapDiet</h1>
    <p class="subtitle">
      AI-Powered Personal Nutrition, Diet Planning & Health Platform.
      Multi-service deployment with isolated <code>app</code> and <code>api</code> services.
    </p>

    <div class="status-panel">
      <div class="status-row">
        <span class="status-label">Service</span>
        <span class="status-val">app (Root)</span>
      </div>
      <div class="status-row">
        <span class="status-label">Internal API Binding</span>
        <span class="status-val" style="color: __API_COLOR__;">__API_STATUS__</span>
      </div>
      <div class="status-row">
        <span class="status-label">FastAPI Backend</span>
        <span class="status-val"><a href="/api" target="_blank" style="color: #38BDF8; text-decoration: none;">/api ↗</a></span>
      </div>
      <div class="status-row">
        <span class="status-label">Swagger Docs</span>
        <span class="status-val"><a href="/api/docs" target="_blank" style="color: #38BDF8; text-decoration: none;">/api/docs ↗</a></span>
      </div>
    </div>

    <div class="links">
      <a class="btn btn-primary" href="/api/docs" target="_blank">
        📖 Open Swagger Docs
      </a>
      <button class="btn btn-secondary" onclick="testApi()">
        ⚡ Test API Live
      </button>
      <a class="btn btn-secondary btn-full" href="/status" target="_blank">
        🔍 Service Health (JSON)
      </a>
    </div>

    <div id="output" class="output-box"></div>
  </div>

  <script>
    async function testApi() {
      const out = document.getElementById('output');
      out.style.display = 'block';
      out.textContent = 'Calling /api ...';
      try {
        const res = await fetch('/api');
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        out.textContent = 'Error: ' + err.message;
      }
    }
  </script>
</body>
</html>"""

def build_html():
    api_info = get_api_status()
    is_connected = api_info.get("status") == "connected"
    api_color = "#10B981" if is_connected else "#F59E0B"
    api_text = "Connected & Active" if is_connected else (
        "Internal Binding Active" if os.environ.get("API_URL") else "Standalone Mode"
    )
    return HTML_TEMPLATE.replace("__API_COLOR__", api_color).replace("__API_STATUS__", api_text).encode("utf-8")

# --- WSGI Callable ---
def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    query_string = environ.get("QUERY_STRING", "")

    if path in ["/status", "/health"] or "format=json" in query_string:
        body = build_status_payload()
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
        ]
        start_response("200 OK", headers)
        return [body]

    body = build_html()
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response("200 OK", headers)
    return [body]

# --- BaseHTTPRequestHandler Class ---
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/status", "/health"] or "format=json" in self.path:
            body = build_status_payload()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        body = build_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return
