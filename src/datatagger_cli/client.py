"""HTTP/API-Helper: nutzt die Auth- und Request-Logik der datatagger-mcp Bibliothek.

Die Bibliothek stellt `make_fdm_request` bereit (Bearer-Auth aus FDM_TOKEN/FDM_BASE_URL,
Fehlerbehandlung, 204-Handling). Für Endpunkte, die die MCP-Library nicht abdeckt,
gehen wir hier durch denselben Helfer – so bleibt Auth/Fehlerverhalten konsistent.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

import httpx

from datatagger_mcp.api import get_auth_config, make_fdm_request

USER_AGENT = "datatagger-cli/0.1.0"


async def req(
    method: str,
    path: str,
    params: Optional[dict] = None,
    body: Optional[dict] = None,
) -> Any:
    """Generic API call via the MCP library logic (auth + error formatting)."""
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    return await make_fdm_request(
        path, method=method.upper(), params=params, json_payload=body
    )


def parse_json_arg(value: str) -> Any:
    """JSON-Argument parsen; '@pfad/datei.json' liest aus Datei."""
    if value.startswith("@"):
        with open(value[1:], encoding="utf-8") as f:
            value = f.read()
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ungültiges JSON: {e}") from e


def parse_description(value: Optional[str]) -> Any:
    """Beschreibungen sind in der aktuellen API JSON-Objekte (z. B. {'en': '…'}).

    - JSON-Objekt (@datei oder Inline) wird unverändert übernommen.
    - Einfacher Text wird als {'en': <text>} gewrappt (String würde beim
      Create vom Server mit 500 abgelehnt).
    """
    if value is None:
        return None
    v = value.strip()
    if v.startswith("@"):
        with open(v[1:], encoding="utf-8") as f:
            v = f.read()
    try:
        parsed = json.loads(v)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {"en": v}


def parse_kv_query(values: Optional[list[str]]) -> Optional[dict]:
    """Query-Parameter aus 'k=v' Strings bauen."""
    if not values:
        return None
    out: dict = {}
    for item in values:
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v
        else:
            raise ValueError(f"Query-Param muss 'k=v' sein, bekam: {item}")
    return out


async def multipart_post(
    path: str,
    file_path: str,
    field: str = "file",
    data: Optional[dict] = None,
) -> Any:
    """Multipart-Upload (z. B. metadata-template-container/import/)."""
    try:
        token, base_url = get_auth_config()
    except ValueError as e:
        return str(e)
    if not os.path.exists(file_path):
        return f"Error: File not found exactly at {file_path}."
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT}
    with open(file_path, "rb") as f:
        files = {field: (os.path.basename(file_path), f, "application/octet-stream")}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    url, headers=headers, data=data, files=files
                )
                resp.raise_for_status()
                if resp.status_code == 204:
                    return "Operation successful (204 No Content)"
                ct = resp.headers.get("content-type", "")
                return resp.json() if "json" in ct.lower() else resp.text
        except httpx.HTTPStatusError as e:
            return f"API Error ({e.response.status_code}): {e.response.text}"
        except Exception as e:
            return f"Error making POST request to API: {e}"
