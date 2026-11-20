"""
SnapDiet - Internal API Client Module
Uses the API_URL environment variable injected by Vercel Service Bindings
to communicate privately between internal services.
"""

import os
import requests
from typing import Any, Dict, Optional

# Vercel injects the bound service's internal base URL into API_URL
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")

def get_service_url(path: str = "") -> str:
    """Resolve an absolute path against the bound API service URL."""
    clean_path = path.lstrip("/")
    return f"{API_BASE_URL}/{clean_path}" if clean_path else API_BASE_URL

def call_api(
    method: str,
    path: str,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
) -> requests.Response:
    """Make an internal HTTP request to the bound API service."""
    url = get_service_url(path)
    return requests.request(
        method=method.upper(),
        url=url,
        json=json_data,
        params=params,
        timeout=timeout,
    )
