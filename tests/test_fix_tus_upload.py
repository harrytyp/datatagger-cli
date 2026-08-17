"""Targeted tests for the two fixes (no network, no live API).

1. _resource_id: pk extraction, name rejection, error-string rejection
2. upload_file_tus: uuid guard + Location strip (mocked httpx)
"""
import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from datatagger_cli import cli  # noqa: E402
from datatagger_cli import client  # noqa: E402

FAIL = []


def check(name, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got={got!r}")
    if not ok:
        FAIL.append(name)


# ---------------------------------------------------------------- _resource_id
rid = cli._resource_id

UUID = "12345678-1234-1234-1234-123456789012"
check("dict with pk (hint differs)", rid({"pk": UUID, "name": "X"}, "project_id"), UUID)
check("dict with id fallback", rid({"id": UUID, "name": "X"}, "project_id"), UUID)
check("dict with only name -> None (old bug!)",
      rid({"name": "test-folder-1"}, "folder_id"), None)
check("dict without any id -> None", rid({"status": 201}, "dataset_id"), None)
check("error string -> None (old bug!)",
      rid("API Error (500):\n<!doctype html>\n<html>...</html>", "dataset_id"), None)
check("bare valid id string", rid("abc-123", "dataset_id"), "abc-123")
check("None -> None", rid(None, "dataset_id"), None)
check("hint key preferred", rid({"dataset_id": "A", "pk": "B"}, "dataset_id"), "A")


# ---------------------------------------------------------------- upload_file_tus
class FakeResp:
    def __init__(self, status=201, headers=None, text=""):
        self.status_code = status
        self.headers = headers or {}
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise client.httpx.HTTPStatusError(
                f"err {self.status_code}", request=None, response=self)


class FakeClient:
    """Records calls; post returns init response, patch returns 204."""
    def __init__(self, init_headers):
        self.init_headers = init_headers
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, **kw):
        self.calls.append(("POST", url, kw))
        return FakeResp(201, self.init_headers)

    async def patch(self, url, **kw):
        self.calls.append(("PATCH", url, kw))
        return FakeResp(204)


async def run_tus(endpoint, fname, init_headers):
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, fname)
        with open(fp, "wb") as f:
            f.write(b"hello tus")
        os.environ["FDM_TOKEN"] = "testtoken"
        real_client = client.httpx.AsyncClient
        client.httpx.AsyncClient = lambda *a, **k: FakeClient(init_headers)
        try:
            return await client.upload_file_tus(endpoint, fp)
        finally:
            client.httpx.AsyncClient = real_client
            del os.environ["FDM_TOKEN"]


async def main():
    # Old failure mode: error-string dataset id -> clean error, no URL build
    garbage = "API Error (500):\n<!doctype html>\n<html lang=\"en\">\n<body>\n</body>\n</html>"
    r = await run_tus(f"/api/v1/uploads-dataset/{garbage}/file/", "x.txt", {})
    check("garbage ds_id -> clean error", r.startswith("Error: TUS upload requires a valid dataset UUID"), True)

    # Not a uuid at all
    r = await run_tus("/api/v1/uploads-dataset/not-a-uuid/file/", "x.txt", {})
    check("non-uuid ds_id -> clean error", r.startswith("Error: TUS upload requires a valid dataset UUID"), True)

    # Location with trailing newline gets stripped -> PATCH uses clean URL
    rel = "/files/tus-abc123\n"
    r = await run_tus(f"/api/v1/uploads-dataset/{UUID}/file/", "x.txt", {"Location": rel})
    check("Location with \\n stripped -> success", "uploaded successfully" in r, True)

    # Absolute Location with trailing CRLF -> success
    r = await run_tus(f"/api/v1/uploads-dataset/{UUID}/file/", "x.txt",
                      {"Location": f"https://datatagger.ub.tum.de/files/x\r\n"})
    check("absolute Location with CRLF -> success", "uploaded successfully" in r, True)

    # No Location header -> clear error
    r = await run_tus(f"/api/v1/uploads-dataset/{UUID}/file/", "x.txt", {})
    check("no Location -> clear error", r == "Error: TUS init returned no Location header.", True)

    print()
    print("FAILURES:", FAIL if FAIL else "none")


asyncio.run(main())