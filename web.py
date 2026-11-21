"""
SnapDiet Web Service Entrypoint for Vercel Multi-Service Deployment.
Provides the entrypoint callable 'app' for the 'app' service,
reading the bound 'API_URL' to communicate with the internal 'api' service.
"""
import os
import ssl
import json
import urllib.request
import urllib.error

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
        # Try /api/ fallback
        try:
            req = urllib.request.Request(f"{api_url}/api", headers={"User-Agent": "SnapDiet-AppService"})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                data = json.loads(response.read().decode("utf-8"))
                return {"status": "connected", "api_url": api_url, "response": data}
        except Exception as inner_e:
            return {"status": "configured", "api_url": api_url, "note": str(e)}

def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    query_string = environ.get("QUERY_STRING", "")

    # JSON status endpoint
    if path in ["/status", "/health"] or "format=json" in query_string:
        api_info = get_api_status()
        body = json.dumps({
            "service": "SnapDiet Web App",
            "version": "1.0.0",
            "binding": api_info,
            "status": "healthy"
        }, indent=2).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
        ]
        start_response("200 OK", headers)
        return [body]

    # HTML Landing Page
    api_info = get_api_status()
    is_connected = api_info.get("status") == "connected"
    api_badge_color = "#10B981" if is_connected else "#F59E0B"
    api_status_text = "Connected & Active" if is_connected else (
        "Internal Binding Active" if os.environ.get("API_URL") else "Standalone Mode"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SnapDiet - AI Nutrition & Health Platform</title>
  <style>
    :root {{
      --primary: #10B981;
      --primary-dark: #059669;
      --bg: #0F172A;
      --card-bg: #1E293B;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --border: #334155;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      max-width: 680px;
      width: 100%;
      padding: 40px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }}
    .badge {{
      display: inline-block;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 16px;
    }}
    .badge-service {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--primary);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    h1 {{
      font-size: 32px;
      font-weight: 800;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #34D399 0%, #10B981 50%, #059669 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    p.subtitle {{
      color: var(--text-muted);
      font-size: 16px;
      line-height: 1.6;
      margin-bottom: 24px;
    }}
    .status-panel {{
      background: #0B1120;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 28px;
    }}
    .status-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      font-size: 14px;
    }}
    .status-row:not(:last-child) {{
      border-bottom: 1px solid rgba(51, 65, 85, 0.5);
    }}
    .status-label {{ color: var(--text-muted); }}
    .status-val {{ font-weight: 600; font-family: monospace; }}
    .links {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 14px 20px;
      border-radius: 10px;
      text-decoration: none;
      font-size: 14px;
      font-weight: 600;
      transition: all 0.2s ease;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #0F172A;
    }}
    .btn-primary:hover {{
      background: var(--primary-dark);
      color: #FFF;
    }}
    .btn-secondary {{
      background: #334155;
      color: var(--text);
    }}
    .btn-secondary:hover {{
      background: #475569;
    }}
    @media (max-width: 600px) {{
      .card {{ padding: 24px; }}
      .links {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="card">
    <span class="badge badge-service">Vercel Multi-Service Project</span>
    <h1>🥗 SnapDiet</h1>
    <p class="subtitle">
      AI-Powered Personal Nutrition, Diet Planning & Health Platform.
      Deployed on Vercel with dedicated <code>app</code> and <code>api</code> microservices and internal service bindings.
    </p>

    <div class="status-panel">
      <div class="status-row">
        <span class="status-label">Service</span>
        <span class="status-val">app (Root)</span>
      </div>
      <div class="status-row">
        <span class="status-label">Internal API Binding</span>
        <span class="status-val" style="color: {api_badge_color};">{api_status_text}</span>
      </div>
      <div class="status-row">
        <span class="status-label">FastAPI Backend</span>
        <span class="status-val"><a href="/api" style="color: #38BDF8; text-decoration: none;">/api</a></span>
      </div>
      <div class="status-row">
        <span class="status-label">Swagger Documentation</span>
        <span class="status-val"><a href="/api/docs" style="color: #38BDF8; text-decoration: none;">/api/docs</a></span>
      </div>
    </div>

    <div class="links">
      <a class="btn btn-primary" href="/api/docs">
        📖 API Documentation
      </a>
      <a class="btn btn-secondary" href="/status">
        ⚡ Service Status (JSON)
      </a>
    </div>
  </div>
</body>
</html>"""

    body = html.encode("utf-8")
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response("200 OK", headers)
    return [body]
