"""Own HTTP/API layer for the DataTagger API.

No dependency on the datatagger-mcp library: authentication (Bearer token from
``FDM_TOKEN``), error formatting, 204 handling, TUS uploads and file downloads
are implemented here directly. Error semantics are kept stable (``API Error
(<code>): <body>``) so tooling and tests can rely on them.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from typing import Any, Optional

import httpx

USER_AGENT = "datatagger-cli/0.1.0"
DEFAULT_BASE_URL = "https://datatagger.ub.tum.de"


def get_auth_config() -> tuple[str, str]:
    """Resolve (token, base_url) from the environment. Raises ValueError if no token."""
    token = os.environ.get("FDM_TOKEN", "")
    base_url = os.environ.get("FDM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if not token:
        raise ValueError(
            "No authentication configured. Set the FDM_TOKEN environment variable."
        )
    return token, base_url


def _headers(token: str) -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


async def req(
    method: str,
    path: str,
    params: Optional[dict] = None,
    body: Optional[dict] = None,
) -> Any:
    """Generic API call: returns parsed JSON (dict/list), text, None or an
    error string formatted as ``API Error (<code>): <body>``."""
    try:
        token, base_url = get_auth_config()
    except ValueError as e:
        return str(e)

    if not path.startswith("/"):
        path = "/" + path
    url = f"{base_url}{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None}

    async with httpx.AsyncClient() as client:
        try:
            req_kwargs = {"headers": _headers(token), "timeout": 30.0}
            if params:
                req_kwargs["params"] = params
            if body is not None:
                req_kwargs["json"] = body

            response = await client.request(method.upper(), url, **req_kwargs)
            response.raise_for_status()

            if response.status_code == 204:
                return "Operation successful (204 No Content)"

            content_type = response.headers.get("content-type", "")
            if "json" in content_type.lower():
                return response.json()
            return response.text
        except httpx.HTTPStatusError as e:
            return f"API Error ({e.response.status_code}): {e.response.text}"
        except Exception as e:
            return f"Error making {method.upper()} request to API: {e}"


async def download_file(
    endpoint: str, dest_path: str, overwrite: bool = False
) -> str:
    """Stream a file from the API to a local destination path."""
    if os.path.exists(dest_path) and not overwrite:
        return f"Error: File already exists at {dest_path} and overwrite is False."

    try:
        token, base_url = get_auth_config()
    except ValueError as e:
        return str(e)

    url = f"{base_url}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET", url, headers=_headers(token), timeout=300.0
            ) as response:
                response.raise_for_status()
                with open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
        return f"File successfully downloaded to: {dest_path}"
    except httpx.HTTPStatusError as e:
        return f"API Error ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"Error downloading file: {e}"


async def upload_file_tus(endpoint: str, file_path: str) -> str:
    """Upload a file via the TUS resumable protocol (same as the DataTagger
    web UI), so the dataset is finalised properly and appears in its folder.

    Step 1: POST /api/v1/uploads-dataset/<id>/tus/ with TUS headers.
    Step 2: PATCH to the returned Location header with the raw file bytes.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found exactly at {file_path}."

    try:
        token, base_url = get_auth_config()
    except ValueError as e:
        return str(e)

    api_base = base_url + "/api/v1"
    upload_endpoint = endpoint.lstrip("/")
    if upload_endpoint.startswith("api/v1/"):
        upload_endpoint = upload_endpoint[len("api/v1/"):]
    if not upload_endpoint.startswith("uploads-dataset/"):
        return f"Error: TUS upload requires an uploads-dataset endpoint, got: {endpoint}"
    ds_id = upload_endpoint.split("/")[1]

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    fname_b64 = base64.b64encode(filename.encode()).decode()
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    ftype_b64 = base64.b64encode(mime_type.encode()).decode()

    async with httpx.AsyncClient() as client:
        try:
            # Step 1: initialise the TUS upload
            init_headers = {
                **_headers(token),
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(file_size),
                "Upload-Metadata": f"filename {fname_b64},filetype {ftype_b64}",
            }
            init_resp = await client.post(
                f"{api_base}/uploads-dataset/{ds_id}/tus/",
                headers=init_headers,
                timeout=30.0,
            )
            init_resp.raise_for_status()

            location = init_resp.headers.get("Location", "")
            if not location:
                return "Error: TUS init returned no Location header."
            tus_url = location
            if tus_url.startswith("/"):
                tus_url = f"{base_url}{tus_url}"

            # Step 2: upload the raw bytes
            with open(file_path, "rb") as f:
                file_data = f.read()
            patch_headers = {
                **_headers(token),
                "Tus-Resumable": "1.0.0",
                "Upload-Offset": "0",
                "Content-Type": "application/offset+octet-stream",
            }
            patch_resp = await client.patch(
                tus_url,
                headers=patch_headers,
                content=file_data,
                timeout=600.0,
            )
            patch_resp.raise_for_status()

            return (
                f"File uploaded successfully via TUS: {filename} (dataset {ds_id})"
            )
        except httpx.HTTPStatusError as e:
            return f"API Error ({e.response.status_code}): {e.response.text}"
        except Exception as e:
            return f"Error uploading file via TUS: {e}"


async def multipart_post(
    path: str,
    file_path: str,
    field: str = "file",
    data: Optional[dict] = None,
) -> Any:
    """Multipart upload (e.g. metadata-template-container/import/)."""
    try:
        token, base_url = get_auth_config()
    except ValueError as e:
        return str(e)
    if not os.path.exists(file_path):
        return f"Error: File not found exactly at {file_path}."
    url = f"{base_url.rstrip('/')}{path}"
    with open(file_path, "rb") as f:
        files = {field: (os.path.basename(file_path), f, "application/octet-stream")}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    url, headers=_headers(token), data=data, files=files
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


def parse_json_arg(value: str) -> Any:
    """Parse a JSON argument; '@path/to/file.json' reads from a file."""
    if value.startswith("@"):
        with open(value[1:], encoding="utf-8") as f:
            value = f.read()
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


def parse_description(value: Optional[str]) -> Any:
    """Descriptions are JSON objects in the current API (e.g. {'en': '…'}).

    - A JSON object (inline or @file) is passed through unchanged.
    - Plain text is wrapped as {'en': <text>} (a raw string is rejected by the
      server with a 500 on create).
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
    """Build query params from 'k=v' strings."""
    if not values:
        return None
    out: dict = {}
    for item in values:
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v
        else:
            raise ValueError(f"Query param must be 'k=v', got: {item}")
    return out
