"""DataTagger CLI commands.

Own high-level command layer for the TUM DataTagger API. Authentication and
HTTP live in `client.py` (Bearer token from FDM_TOKEN); commands stay
high-level and grouped for a simple user experience.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import logging
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.json import JSON

# suppress httpx INFO logs from the HTTP layer (only show errors)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from .client import (
    download_file,
    multipart_post,
    parse_description,
    parse_json_arg,
    parse_kv_query,
    req,
    upload_file_tus,
)


# --- High-level API helpers.
#     Own implementation (no datatagger-mcp dependency): auth + HTTP live in
#     client.py. The command layer talks exclusively to these wrappers; their
#     signatures match the datatagger-mcp tool functions that used to back
#     them, so commands stay high-level and readable.

_SEARCH_RESULT_TYPES = [
    "project", "folder", "dataset", "dataset_version", "file", "template", "template_version",
]


async def search_datatagger(term: str, limit: int = 25) -> Any:
    return await req("POST", "/api/v1/search/global/", body={
        "search_text": term, "limit": limit, "result_types": _SEARCH_RESULT_TYPES})


async def list_projects(limit: int = 100, offset: int = 0, search: str = "") -> Any:
    return await req("GET", "/api/v1/project/", params={
        "limit": limit, "offset": offset, "search": search})


async def get_project(project_id: str) -> Any:
    return await req("GET", f"/api/v1/project/{project_id}/")


async def create_project(name: str) -> Any:
    return await req("POST", "/api/v1/project/", body={"name": name})


async def delete_project(project_id: str, confirm_danger: bool = False) -> Any:
    return await req("DELETE", f"/api/v1/project/{project_id}/")


async def list_folders(project: str = "", limit: int = 100, offset: int = 0, search: str = "") -> Any:
    return await req("GET", "/api/v1/folder/", params={
        "project": project, "limit": limit, "offset": offset, "search": search})


async def get_folder(folder_id: str) -> Any:
    return await req("GET", f"/api/v1/folder/{folder_id}/")


async def create_folder(project_id: str, name: str) -> Any:
    return await req("POST", "/api/v1/folder/", body={"project": project_id, "name": name})


async def delete_folder(folder_id: str, confirm_danger: bool = False) -> Any:
    return await req("DELETE", f"/api/v1/folder/{folder_id}/")


async def list_datasets(folder_id: str = "", limit: int = 100, offset: int = 0, search: str = "") -> Any:
    return await req("GET", "/api/v1/uploads-dataset/", params={
        "folder": folder_id, "limit": limit, "offset": offset, "search": search})


async def create_dataset(name: str, folder_id: Optional[str] = None) -> Any:
    body = {"name": name}
    if folder_id:
        body["folder"] = folder_id
    return await req("POST", "/api/v1/uploads-dataset/", body=body)


async def delete_dataset(dataset_id: str, confirm_danger: bool = False) -> Any:
    return await req("DELETE", f"/api/v1/uploads-dataset/{dataset_id}/")


async def publish_dataset(dataset_id: str) -> Any:
    return await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/publish/", body={})


async def restore_dataset_version(dataset_id: str, uploads_version_id: str) -> Any:
    return await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/restore/",
                     body={"uploads_version": uploads_version_id})


async def compare_dataset_versions(version_id: str, compare_to_id: str) -> Any:
    """Diff between two dataset versions (GET endpoint of the current API)."""
    return await req("GET", f"/api/v1/uploads-version/{version_id}/diff/",
                     params={"compare": compare_to_id})


async def upload_dataset_file(dataset_id: str, source_path: str) -> Any:
    return await upload_file_tus(f"/api/v1/uploads-dataset/{dataset_id}/file/", source_path)


async def download_fdm_file(endpoint: str, dest_path: str, overwrite: bool = False) -> Any:
    return await download_file(endpoint, dest_path, overwrite)


async def get_folder_permissions(folder_id: str) -> Any:
    return await req("GET", "/api/v1/folder-permission/", params={"folder": folder_id})


async def set_folder_permissions(folder_id: str, folder_users: List[Dict[str, Any]]) -> Any:
    return await req("PUT", f"/api/v1/folder/{folder_id}/permissions/",
                     body={"folder_users": folder_users})


async def list_metadata(search: str = "", limit: int = 100) -> Any:
    return await req("GET", "/api/v1/metadata/", params={"limit": limit, "search": search})


async def add_metadata_to_dataset(dataset_id: str, metadata_items: List[Dict[str, Any]]) -> Any:
    return await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/version/",
                     body={"metadata": metadata_items})

class AsyncTyper(typer.Typer):
    """Typer subclass that runs async command functions in asyncio.run() automatically."""

    def command(self, *args: Any, **kwargs: Any):
        decorator = super().command(*args, **kwargs)

        def wrap(fn: Any):
            if inspect.iscoroutinefunction(fn):

                @functools.wraps(fn)
                def sync_wrapper(*a: Any, **kw: Any):
                    return asyncio.run(fn(*a, **kw))

                return decorator(sync_wrapper)
            return decorator(fn)

        return wrap


console = Console()
app = AsyncTyper(
    help="DataTagger CLI – full API access with high-level commands for the TUM DataTagger API.\n\nAuth: FDM_TOKEN (Bearer) + FDM_BASE_URL (default https://datatagger.ub.tum.de) as environment variables.",
    no_args_is_help=True,
)


# ---------------------------------------------------------------- Output-Helfer

def out(result: Any) -> None:
    """Display result: dict/list/JSON with syntax highlighting, errors in red.

    soft_wrap=True prevents rich from wrapping lines inside JSON strings
    (otherwise the output becomes machine-unreadable).
    """
    if result is None:
        console.print("[yellow]No response (None)[/yellow]")
        return
    if isinstance(result, str):
        low = result.lower()
        if low.startswith(("error", "api error", "no authentication")):
            console.print(f"[bold red]{result}[/bold red]")
            return
        if not result.strip():
            console.print("[green]OK (empty response – 2xx without body)[/green]")
            return
        try:
            console.print(JSON(result), soft_wrap=True)
            return
        except Exception:
            console.print(result, soft_wrap=True)
            return
    if isinstance(result, (dict, list)):
        console.print(JSON(json.dumps(result, indent=2, ensure_ascii=False)), soft_wrap=True)
        return
    console.print(result)


def _action(resource: str, rid: str, action: str, body: Optional[dict] = None) -> Any:
    """POST /api/v1/<resource>/<id>/<action>/ with an optional body."""
    return req("POST", f"/api/v1/{resource}/{rid}/{action}/", body=body)


def _confirm(confirm: bool, what: str) -> None:
    if not confirm:
        console.print(
            f"[bold red]ABORTED: {what} requires --confirm.[/bold red]"
        )
        raise typer.Exit(2)


# ================================================================ SEARCH / RAW

@app.command("search")
async def search(
    term: str = typer.Argument(..., help="Search term"),
    limit: int = typer.Option(25, help="Max. results (1–100)"),
):
    """Search globally across projects, folders, datasets, files and templates."""
    out(await search_datatagger(term=term, limit=limit))


@app.command("raw")
async def raw(
    method: str = typer.Argument(..., help="HTTP method: GET/POST/PUT/PATCH/DELETE"),
    path: str = typer.Argument(..., help="API path, e.g. /api/v1/settings/"),
    data: Optional[str] = typer.Option(None, "--data", help="JSON body or @file.json"),
    query: Optional[List[str]] = typer.Option(None, "--query", help="Query param k=v (repeatable)"),
):
    """Arbitrary API call (escape hatch for anything without a dedicated command)."""
    body = parse_json_arg(data) if data else None
    params = parse_kv_query(query)
    out(await req(method, path, params=params, body=body))


# ================================================================ AUTH

auth_app = AsyncTyper(help="Authentication", no_args_is_help=True)
app.add_typer(auth_app, name="auth")


@auth_app.command("login")
async def auth_login(
    username: str = typer.Argument(..., help="TUM ID / email"),
    password: Optional[str] = typer.Option(None, "--password", prompt=True, hide_input=True, help="Password (prompted)"),
):
    """Log in with username/password and print access & refresh tokens."""
    out(await req("POST", "/api/v1/auth/", body={"username": username, "password": password}))


@auth_app.command("verify")
async def auth_verify(
    token: Optional[str] = typer.Option(None, "--token", help="Token to verify (default: FDM_TOKEN)"),
):
    """Verify the current token."""
    import os

    tok = token or os.environ.get("FDM_TOKEN", "")
    if not tok:
        console.print("[bold red]No token: set --token or FDM_TOKEN.[/bold red]")
        raise typer.Exit(2)
    out(await req("POST", "/api/v1/authverify/", body={"token": tok}))


@auth_app.command("refresh")
async def auth_refresh(
    refresh: str = typer.Argument(..., help="Refresh token"),
):
    """Exchange a refresh token for a new access token."""
    out(await req("POST", "/api/v1/authrefresh/", body={"refresh": refresh}))


@auth_app.command("jwt-cookie")
async def auth_jwt_cookie(
    token: Optional[str] = typer.Option(None, "--token", help="Token (default: FDM_TOKEN)"),
):
    """Convert a JWT into an HTTP cookie (web UI auth)."""
    import os

    tok = token or os.environ.get("FDM_TOKEN", "")
    if not tok:
        console.print("[bold red]No token: set --token or FDM_TOKEN.[/bold red]")
        raise typer.Exit(2)
    out(await req("POST", "/api/v1/authjwtcookie/", body={"token": tok}))


# ================================================================ PROJECT

project_app = AsyncTyper(help="Projects", no_args_is_help=True)
app.add_typer(project_app, name="project")


@project_app.command("list")
async def project_list(
    limit: int = typer.Option(100, help="Max. entries"),
    offset: int = typer.Option(0, help="Offset"),
    search: str = typer.Option("", help="Search filter"),
):
    out(await list_projects(limit=limit, offset=offset, search=search))


@project_app.command("get")
async def project_get(project_id: str = typer.Argument(..., help="Project UUID")):
    out(await get_project(project_id))


@project_app.command("create")
async def project_create(
    name: str = typer.Argument(..., help="Project name"),
    description: Optional[str] = typer.Option(None, "--description"),
    folder_name: Optional[str] = typer.Option(None, "--folder-name", help="Create an initial folder"),
    users: Optional[str] = typer.Option(None, "--users", help="project_users as JSON or @file"),
    metadata: Optional[str] = typer.Option(None, "--metadata", help="Metadata as JSON or @file"),
):
    """Create a project (MCP high-level for the name; extended fields optional)."""
    if not (description or folder_name or users or metadata):
        out(await create_project(name=name))
        return
    body: dict = {"name": name}
    if description is not None:
        body["description"] = parse_description(description)
    if folder_name is not None:
        body["folder_name"] = folder_name
    if users:
        body["project_users"] = parse_json_arg(users)
    if metadata:
        body["metadata"] = parse_json_arg(metadata)
    out(await req("POST", "/api/v1/project/", body=body))


@project_app.command("update")
async def project_update(
    project_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    description: Optional[str] = typer.Option(None, "--description"),
    metadata: Optional[str] = typer.Option(None, "--metadata"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = parse_description(description)
    if metadata:
        body["metadata"] = parse_json_arg(metadata)
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/project/{project_id}/", body=body))


@project_app.command("delete")
async def project_delete(
    project_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm deletion"),
):
    _confirm(confirm, "Delete project")
    out(await delete_project(project_id, confirm_danger=True))


@project_app.command("folders")
async def project_folders(
    project_id: str = typer.Argument(...),
    limit: int = typer.Option(100),
    offset: int = typer.Option(0),
):
    """List the folders of a project."""
    out(await req("GET", f"/api/v1/project/{project_id}/folders/", params={"limit": limit, "offset": offset}))


@project_app.command("members")
async def project_members(project_id: str = typer.Argument(...)):
    """List the memberships of a project (client-side filtered)."""
    result = await req("GET", "/api/v1/project-membership/")
    if isinstance(result, dict) and "results" in result:
        result = {**result, "results": [r for r in result["results"] if str(r.get("project", "")) == project_id]}
    out(result)


@project_app.command("members-set")
async def project_members_set(
    project_id: str = typer.Argument(...),
    users: str = typer.Argument(..., help="project_users as JSON or @file"),
):
    """Replace the member array of a project (warning: replaces everything!)."""
    out(await req("PUT", f"/api/v1/project/{project_id}/members/", body={"project_users": parse_json_arg(users)}))


@project_app.command("lock")
async def project_lock(project_id: str = typer.Argument(...)):
    out(await _action("project", project_id, "lock"))


@project_app.command("unlock")
async def project_unlock(project_id: str = typer.Argument(...)):
    out(await _action("project", project_id, "unlock"))


@project_app.command("status")
async def project_status(project_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/project/{project_id}/status/"))


@project_app.command("metadata-templates")
async def project_metadata_templates(project_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/project/{project_id}/metadata-templates/"))


@project_app.command("template-container-pool")
async def project_template_container_pool(project_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/project/{project_id}/metadata-template-container-pool/"))


# --- project-membership CRUD (admin) ---

@project_app.command("membership-list")
async def project_membership_list(
    limit: int = typer.Option(100),
    offset: int = typer.Option(0),
):
    out(await req("GET", "/api/v1/project-membership/", params={"limit": limit, "offset": offset}))


@project_app.command("membership-create")
async def project_membership_create(
    project_id: str = typer.Argument(...),
    member: str = typer.Argument(..., help="User ID or email"),
    is_project_admin: bool = typer.Option(False),
    can_create_folders: bool = typer.Option(True),
    is_metadata_template_admin: bool = typer.Option(False),
):
    out(await req("POST", "/api/v1/project-membership/", body={
        "project": project_id, "member": member,
        "is_project_admin": is_project_admin,
        "can_create_folders": can_create_folders,
        "is_metadata_template_admin": is_metadata_template_admin,
    }))


@project_app.command("membership-update")
async def project_membership_update(
    membership_id: str = typer.Argument(...),
    is_project_admin: Optional[bool] = typer.Option(None),
    can_create_folders: Optional[bool] = typer.Option(None),
    is_metadata_template_admin: Optional[bool] = typer.Option(None),
):
    body = {k: v for k, v in {
        "is_project_admin": is_project_admin,
        "can_create_folders": can_create_folders,
        "is_metadata_template_admin": is_metadata_template_admin,
    }.items() if v is not None}
    out(await req("PATCH", f"/api/v1/project-membership/{membership_id}/", body=body))


@project_app.command("membership-delete")
async def project_membership_delete(
    membership_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm"),
):
    _confirm(confirm, "Delete membership")
    out(await req("DELETE", f"/api/v1/project-membership/{membership_id}/"))


# ================================================================ FOLDER

folder_app = AsyncTyper(help="Folders", no_args_is_help=True)
app.add_typer(folder_app, name="folder")


@folder_app.command("list")
async def folder_list(
    project: str = typer.Option("", "--project", help="Filter by project UUID"),
    limit: int = typer.Option(100),
    offset: int = typer.Option(0),
    search: str = typer.Option(""),
):
    out(await list_folders(project=project, limit=limit, offset=offset, search=search))


@folder_app.command("get")
async def folder_get(folder_id: str = typer.Argument(...)):
    out(await get_folder(folder_id))


@folder_app.command("create")
async def folder_create(
    project_id: str = typer.Argument(...),
    name: str = typer.Argument(...),
    description: Optional[str] = typer.Option(None, "--description"),
    storage: Optional[str] = typer.Option(None, "--storage"),
    metadata: Optional[str] = typer.Option(None, "--metadata"),
    users: Optional[str] = typer.Option(None, "--users"),
):
    """Create a folder (MCP high-level for name+project; extended fields optional)."""
    if not (description or storage or metadata or users):
        out(await create_folder(project_id=project_id, name=name))
        return
    body: dict = {"project": project_id, "name": name}
    if description is not None:
        body["description"] = parse_description(description)
    if storage is not None:
        body["storage"] = storage
    if metadata:
        body["metadata"] = parse_json_arg(metadata)
    if users:
        body["folder_users"] = parse_json_arg(users)
    out(await req("POST", "/api/v1/folder/", body=body))


@folder_app.command("update")
async def folder_update(
    folder_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    description: Optional[str] = typer.Option(None, "--description"),
    storage: Optional[str] = typer.Option(None, "--storage"),
    metadata: Optional[str] = typer.Option(None, "--metadata"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = parse_description(description)
    if storage is not None:
        body["storage"] = storage
    if metadata:
        body["metadata"] = parse_json_arg(metadata)
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/folder/{folder_id}/", body=body))


@folder_app.command("delete")
async def folder_delete(
    folder_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm"),
):
    _confirm(confirm, "Delete folder")
    out(await delete_folder(folder_id, confirm_danger=True))


@folder_app.command("lock")
async def folder_lock(folder_id: str = typer.Argument(...)):
    out(await _action("folder", folder_id, "lock"))


@folder_app.command("unlock")
async def folder_unlock(folder_id: str = typer.Argument(...)):
    out(await _action("folder", folder_id, "unlock"))


@folder_app.command("status")
async def folder_status(folder_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/folder/{folder_id}/status/"))


@folder_app.command("permissions")
async def folder_permissions(folder_id: str = typer.Argument(...)):
    """List the active user permissions of a folder."""
    out(await get_folder_permissions(folder_id))


@folder_app.command("set-permissions")
async def folder_set_permissions(
    folder_id: str = typer.Argument(...),
    users: str = typer.Argument(..., help="folder_users as JSON or @file"),
):
    """Set the permission array of a folder."""
    out(await set_folder_permissions(folder_id, parse_json_arg(users)))


@folder_app.command("metadata-templates")
async def folder_metadata_templates(folder_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/folder/{folder_id}/metadata-templates/"))


@folder_app.command("template-container-pool")
async def folder_template_container_pool(folder_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/folder/{folder_id}/metadata-template-container-pool/"))


# ================================================================ DATASET

dataset_app = AsyncTyper(help="Datasets (uploads)", no_args_is_help=True)
app.add_typer(dataset_app, name="dataset")


@dataset_app.command("list")
async def dataset_list(
    folder: str = typer.Option("", "--folder", help="Filter by folder UUID"),
    name: Optional[str] = typer.Option(None, "--name", help="Filter by name"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (e.g. PUBLISHED)"),
    locked: Optional[bool] = typer.Option(None, "--locked/--unlocked"),
    created_by: Optional[int] = typer.Option(None, "--created-by"),
    ordering: Optional[str] = typer.Option(None, "--ordering", help="e.g. -creation_date"),
    limit: int = typer.Option(100),
    offset: int = typer.Option(0),
    search: str = typer.Option(""),
):
    params = {"folder": folder, "limit": limit, "offset": offset, "search": search,
              "name": name, "status": status, "locked": locked, "created_by": created_by,
              "ordering": ordering}
    out(await req("GET", "/api/v1/uploads-dataset/", params=params))


@dataset_app.command("get")
async def dataset_get(dataset_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/uploads-dataset/{dataset_id}/"))


@dataset_app.command("create")
async def dataset_create(
    name: str = typer.Argument(...),
    folder_id: Optional[str] = typer.Option(None, "--folder", help="Folder UUID (otherwise draft)"),
):
    out(await create_dataset(name=name, folder_id=folder_id))


@dataset_app.command("update")
async def dataset_update(
    dataset_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    metadata_template: Optional[str] = typer.Option(None, "--metadata-template"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if metadata_template is not None:
        body["metadata_template"] = metadata_template
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/uploads-dataset/{dataset_id}/", body=body))


@dataset_app.command("delete")
async def dataset_delete(
    dataset_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm"),
):
    _confirm(confirm, "Delete dataset")
    out(await delete_dataset(dataset_id, confirm_danger=True))


@dataset_app.command("publish")
async def dataset_publish(
    dataset_id: str = typer.Argument(...),
    folder: Optional[str] = typer.Option(None, "--folder", help="Optional target folder"),
):
    """Finalize/publish a dataset."""
    if folder:
        out(await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/publish/", body={"folder": folder}))
    else:
        out(await publish_dataset(dataset_id))


@dataset_app.command("restore")
async def dataset_restore(
    dataset_id: str = typer.Argument(...),
    version_id: str = typer.Argument(..., help="uploads_version UUID"),
):
    """Restore a dataset to a historical version."""
    out(await restore_dataset_version(dataset_id, version_id))


@dataset_app.command("compare")
async def dataset_compare(
    version_id: str = typer.Argument(...),
    compare_to_id: str = typer.Argument(..., help="other uploads_version UUID"),
):
    """Diff between two dataset versions (GET endpoint of the current API)."""
    out(await compare_dataset_versions(version_id, compare_to_id))


@dataset_app.command("upload")
async def dataset_upload(
    dataset_id: str = typer.Argument(...),
    source_path: str = typer.Argument(..., help="Local file (TUS resumable)"),
):
    """Upload a file into a dataset (TUS protocol, like the web UI)."""
    out(await upload_dataset_file(dataset_id, source_path))


@dataset_app.command("file-upload")
async def dataset_file_upload(
    dataset_id: str = typer.Argument(...),
    source_path: str = typer.Argument(...),
):
    """Upload a file via legacy multipart (POST /file/)."""
    out(await multipart_post(f"/api/v1/uploads-dataset/{dataset_id}/file/", source_path, field="file"))


@dataset_app.command("add-metadata")
async def dataset_add_metadata(
    dataset_id: str = typer.Argument(...),
    metadata: str = typer.Argument(..., help="Metadata items as JSON or @file"),
):
    """Append metadata tags to a dataset (creates a new version)."""
    out(await add_metadata_to_dataset(dataset_id, parse_json_arg(metadata)))


@dataset_app.command("new-version")
async def dataset_new_version(
    dataset_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    metadata: Optional[str] = typer.Option(None, "--metadata"),
):
    """Create a new version of a dataset."""
    body: dict = {}
    if name is not None:
        body["name"] = name
    if metadata:
        body["metadata"] = parse_json_arg(metadata)
    out(await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/version/", body=body))


@dataset_app.command("reference")
async def dataset_reference(
    dataset_id: str = typer.Argument(...),
    filepath: str = typer.Argument(..., help="Path to an existing file on the storage"),
):
    """Reference an existing storage file."""
    out(await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/reference/", body={"filepath": filepath}))


@dataset_app.command("lock")
async def dataset_lock(dataset_id: str = typer.Argument(...)):
    out(await _action("uploads-dataset", dataset_id, "lock"))


@dataset_app.command("unlock")
async def dataset_unlock(dataset_id: str = typer.Argument(...)):
    out(await _action("uploads-dataset", dataset_id, "unlock"))


@dataset_app.command("status")
async def dataset_status(dataset_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/uploads-dataset/{dataset_id}/status/"))


@dataset_app.command("bulk-delete")
async def dataset_bulk_delete(
    dataset_ids: List[str] = typer.Argument(..., help="Dataset UUIDs"),
    confirm: bool = typer.Option(False, "--confirm"),
):
    _confirm(confirm, "Bulk-delete datasets")
    out(await req("POST", "/api/v1/uploads-dataset/bulk-delete/", body={"uploads_datasets": dataset_ids}))


@dataset_app.command("bulk-publish")
async def dataset_bulk_publish(
    folder: str = typer.Argument(..., help="Target folder UUID"),
    dataset_ids: List[str] = typer.Argument(..., help="Dataset UUIDs"),
):
    out(await req("POST", "/api/v1/uploads-dataset/bulk-publish/", body={"uploads_datasets": dataset_ids, "folder": folder}))


@dataset_app.command("bulk-upgrade")
async def dataset_bulk_upgrade(
    dataset_ids: List[str] = typer.Argument(..., help="Dataset UUIDs"),
):
    """Bulk: trigger a metadata template upgrade."""
    out(await req("POST", "/api/v1/uploads-dataset/bulk-upgrade-metadata/", body={"uploads_datasets": dataset_ids}))


@dataset_app.command("upgrade")
async def dataset_upgrade(
    dataset_id: str = typer.Argument(...),
    status: bool = typer.Option(False, "--status", help="Query upgrade status"),
    payload: bool = typer.Option(False, "--payload", help="Query upgrade payload"),
    submit: bool = typer.Option(False, "--submit", help="Run upgrade"),
    resolve_conflict: bool = typer.Option(False, "--resolve-conflict", help="Resolve conflict"),
    json_data: Optional[str] = typer.Option(None, "--json", help="JSON for --resolve-conflict (base_version_pk, resolutions)"),
):
    """Metadata template upgrade of a dataset (one mode required)."""
    if status:
        out(await req("GET", f"/api/v1/uploads-dataset/{dataset_id}/upgrade-metadata-status/"))
    elif payload:
        out(await req("GET", f"/api/v1/uploads-dataset/{dataset_id}/upgrade-metadata-payload/"))
    elif resolve_conflict:
        out(await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/resolve-upgrade-metadata-conflict/", body=parse_json_arg(json_data or "{}")))
    elif submit:
        out(await req("POST", f"/api/v1/uploads-dataset/{dataset_id}/upgrade-metadata/"))
    else:
        console.print("[yellow]Specify a mode: --status | --payload | --submit | --resolve-conflict[/yellow]")
        raise typer.Exit(2)

# ================================================================ VERSION

version_app = AsyncTyper(help="Upload versions", no_args_is_help=True)
app.add_typer(version_app, name="version")


@version_app.command("list")
async def version_list(
    dataset: str = typer.Option("", "--dataset", help="Filter by dataset UUID"),
    dataset_folder: str = typer.Option("", "--dataset-folder", help="Filter by dataset__folder"),
    limit: int = typer.Option(100),
    offset: int = typer.Option(0),
    search: str = typer.Option(""),
):
    out(await req("GET", "/api/v1/uploads-version/", params={
        "dataset": dataset, "dataset__folder": dataset_folder,
        "limit": limit, "offset": offset, "search": search}))


@version_app.command("get")
async def version_get(version_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/uploads-version/{version_id}/"))


@version_app.command("update")
async def version_update(
    version_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    status: Optional[str] = typer.Option(None, "--status", help="SCHEDULED/IN_PROGRESS/ERROR/FINISHED"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if status is not None:
        body["status"] = status
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/uploads-version/{version_id}/", body=body))


@version_app.command("status")
async def version_status(version_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/uploads-version/{version_id}/status/"))


@version_app.command("download")
async def version_download(
    version_id: str = typer.Argument(...),
    dest_path: str = typer.Argument(..., help="Local destination path"),
    overwrite: bool = typer.Option(False, "--overwrite"),
):
    out(await download_fdm_file(f"/api/v1/uploads-version/{version_id}/download/", dest_path, overwrite))


@version_app.command("diff")
async def version_diff(
    version_id: str = typer.Argument(...),
    compare: str = typer.Argument(..., help="Version to compare (uploads_version UUID)"),
):
    """Diff between two versions (GET endpoint of the current API)."""
    out(await req("GET", f"/api/v1/uploads-version/{version_id}/diff/", params={"compare": compare}))


# ================================================================ VERSION-FILE

versionfile_app = AsyncTyper(help="Version files & parser processing", no_args_is_help=True)
app.add_typer(versionfile_app, name="version-file")


@versionfile_app.command("get")
async def versionfile_get(file_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/uploads-version-file/{file_id}/"))


@versionfile_app.command("parser-processing")
async def versionfile_parser_processing(file_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/uploads-version-file/{file_id}/parser-processing/"))


@versionfile_app.command("retrigger-parser")
async def versionfile_retrigger_parser(
    file_id: str = typer.Argument(...),
    parser_type: Optional[str] = typer.Option(None, "--parser-type", help="e.g. CSV_VALUE"),
):
    body = {"parser_type": parser_type} if parser_type else {}
    out(await req("POST", f"/api/v1/uploads-version-file/{file_id}/retrigger-parser-processing/", body=body))


@versionfile_app.command("retry-processing")
async def versionfile_retry_processing(file_id: str = typer.Argument(...)):
    out(await req("POST", f"/api/v1/uploads-version-file/{file_id}/retry-processing/", body={}))


# ================================================================ METADATA

metadata_app = AsyncTyper(help="Metadata", no_args_is_help=True)
app.add_typer(metadata_app, name="metadata")


@metadata_app.command("list")
async def metadata_list(
    search: str = typer.Option(""),
    limit: int = typer.Option(100),
):
    out(await list_metadata(search=search, limit=limit))


@metadata_app.command("get")
async def metadata_get(metadata_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata/{metadata_id}/"))


@metadata_app.command("tags")
async def metadata_tags(limit: int = typer.Option(100), search: str = typer.Option("")):
    out(await req("GET", "/api/v1/metadata-tag/", params={"limit": limit, "search": search}))


@metadata_app.command("tag")
async def metadata_tag(tag_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-tag/{tag_id}/"))


@metadata_app.command("fields")
async def metadata_fields(limit: int = typer.Option(100), search: str = typer.Option("")):
    out(await req("GET", "/api/v1/metadata-field/", params={"limit": limit, "search": search}))


@metadata_app.command("field")
async def metadata_field(field_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-field/{field_id}/"))


@metadata_app.command("bulk-add")
async def metadata_bulk_add(
    dataset_ids: List[str] = typer.Argument(..., help="Dataset UUIDs"),
    metadata: str = typer.Argument(..., help="Metadata items as JSON or @file"),
):
    """Apply metadata to multiple datasets at once."""
    out(await req("POST", "/api/v1/metadata/bulk-add-to-uploads-datasets/", body={
        "uploads_datasets": dataset_ids, "metadata": parse_json_arg(metadata)}))


# --- metadata template ---

template_app = AsyncTyper(help="Metadata templates", no_args_is_help=True)
metadata_app.add_typer(template_app, name="template")


@template_app.command("list")
async def template_list(limit: int = typer.Option(100), search: str = typer.Option("")):
    out(await req("GET", "/api/v1/metadata-template/", params={"limit": limit, "search": search}))


@template_app.command("get")
async def template_get(template_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-template/{template_id}/"))


@template_app.command("update")
async def template_update(
    template_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/metadata-template/{template_id}/", body=body))


@template_app.command("diff")
async def template_diff(
    template_id: str = typer.Argument(...),
    compare: str = typer.Argument(..., help="Template UUID to compare"),
):
    out(await req("GET", f"/api/v1/metadata-template/{template_id}/diff/", params={"compare": compare}))


@template_app.command("lock")
async def template_lock(template_id: str = typer.Argument(...)):
    out(await _action("metadata-template", template_id, "lock"))


@template_app.command("unlock")
async def template_unlock(template_id: str = typer.Argument(...)):
    out(await _action("metadata-template", template_id, "unlock"))


@template_app.command("status")
async def template_status(template_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-template/{template_id}/status/"))


# --- metadata template container ---

container_app = AsyncTyper(help="Metadata template containers", no_args_is_help=True)
metadata_app.add_typer(container_app, name="container")


@container_app.command("list")
async def container_list(limit: int = typer.Option(100), search: str = typer.Option("")):
    out(await req("GET", "/api/v1/metadata-template-container/", params={"limit": limit, "search": search}))


@container_app.command("get")
async def container_get(container_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-template-container/{container_id}/"))


@container_app.command("create")
async def container_create(
    name: str = typer.Argument(...),
    assigned_to_content_type: Optional[str] = typer.Option(None, "--content-type"),
    assigned_to_object_id: Optional[str] = typer.Option(None, "--object-id"),
    fields: Optional[str] = typer.Option(None, "--fields", help="metadata_template_fields as JSON or @file"),
):
    body: dict = {"name": name}
    if assigned_to_content_type is not None:
        body["assigned_to_content_type"] = assigned_to_content_type
    if assigned_to_object_id is not None:
        body["assigned_to_object_id"] = assigned_to_object_id
    if fields:
        body["metadata_template_fields"] = parse_json_arg(fields)
    out(await req("POST", "/api/v1/metadata-template-container/", body=body))


@container_app.command("update")
async def container_update(
    container_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    fields: Optional[str] = typer.Option(None, "--fields"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if fields:
        body["metadata_template_fields"] = parse_json_arg(fields)
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/metadata-template-container/{container_id}/", body=body))


@container_app.command("clone")
async def container_clone(
    container_id: str = typer.Argument(...),
    assigned_to_content_type: Optional[str] = typer.Option(None, "--content-type"),
    assigned_to_object_id: Optional[str] = typer.Option(None, "--object-id"),
):
    body: dict = {}
    if assigned_to_content_type is not None:
        body["assigned_to_content_type"] = assigned_to_content_type
    if assigned_to_object_id is not None:
        body["assigned_to_object_id"] = assigned_to_object_id
    out(await req("POST", f"/api/v1/metadata-template-container/{container_id}/clone/", body=body))


@container_app.command("lock")
async def container_lock(container_id: str = typer.Argument(...)):
    out(await _action("metadata-template-container", container_id, "lock"))


@container_app.command("unlock")
async def container_unlock(container_id: str = typer.Argument(...)):
    out(await _action("metadata-template-container", container_id, "unlock"))


@container_app.command("status")
async def container_status(container_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-template-container/{container_id}/status/"))


@container_app.command("version")
async def container_version(
    container_id: str = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    fields: Optional[str] = typer.Option(None, "--fields"),
):
    body: dict = {}
    if name is not None:
        body["name"] = name
    if fields:
        body["metadata_template_fields"] = parse_json_arg(fields)
    out(await req("POST", f"/api/v1/metadata-template-container/{container_id}/version/", body=body))


@container_app.command("restore")
async def container_restore(
    container_id: str = typer.Argument(...),
    template_id: str = typer.Argument(..., help="metadata_template UUID (target version)"),
):
    out(await req("POST", f"/api/v1/metadata-template-container/{container_id}/restore/", body={"metadata_template": template_id}))


@container_app.command("import")
async def container_import(
    file_path: str = typer.Argument(..., help="Template file (.json)"),
    assigned_to_content_type: Optional[str] = typer.Option(None, "--content-type"),
    assigned_to_object_id: Optional[str] = typer.Option(None, "--object-id"),
):
    """Import a template container from a file (multipart)."""
    data = {}
    if assigned_to_content_type is not None:
        data["assigned_to_content_type"] = assigned_to_content_type
    if assigned_to_object_id is not None:
        data["assigned_to_object_id"] = assigned_to_object_id
    out(await multipart_post("/api/v1/metadata-template-container/import/", file_path, field="file", data=data or None))


@container_app.command("pool")
async def container_pool(
    resource_type: str = typer.Argument(..., help="project | folder | dataset"),
    resource_id: str = typer.Argument(...),
):
    """Query the available template container pool of a resource."""
    out(await req("GET", f"/api/v1/{resource_type}/{resource_id}/metadata-template-container-pool/"))


# --- metadata template export ---

templateexport_app = AsyncTyper(help="Metadata template export", no_args_is_help=True)
metadata_app.add_typer(templateexport_app, name="export")


@templateexport_app.command("list")
async def templateexport_list(limit: int = typer.Option(100), offset: int = typer.Option(0)):
    out(await req("GET", "/api/v1/metadata-template-export/", params={"limit": limit, "offset": offset}))


@templateexport_app.command("get")
async def templateexport_get(export_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/metadata-template-export/{export_id}/"))


@templateexport_app.command("download")
async def templateexport_download(
    export_id: str = typer.Argument(...),
    dest_path: str = typer.Argument(...),
    overwrite: bool = typer.Option(False, "--overwrite"),
):
    out(await download_fdm_file(f"/api/v1/metadata-template-export/{export_id}/download/", dest_path, overwrite))


@templateexport_app.command("create")
async def templateexport_create(
    container_ids: List[str] = typer.Argument(..., help="Container UUIDs"),
    format: str = typer.Option("json", "--format", help="json | csv | xml"),
):
    out(await req("POST", "/api/v1/metadata-template-export/", body={
        "metadata_template_containers": container_ids, "metadata_format": format}))


# ================================================================ PARSER-CONFIG

parser_app = AsyncTyper(help="File parser configurations", no_args_is_help=True)
app.add_typer(parser_app, name="parser-config")


@parser_app.command("list")
async def parser_list(limit: int = typer.Option(100)):
    out(await req("GET", "/api/v1/file-parser-configuration/", params={"limit": limit}))


@parser_app.command("get")
async def parser_get(config_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/file-parser-configuration/{config_id}/"))


@parser_app.command("available-types")
async def parser_available_types():
    out(await req("GET", "/api/v1/file-parser-configuration/available-types/"))


@parser_app.command("create")
async def parser_create(
    assigned_to_object_id: str = typer.Argument(..., help="Resource UUID"),
    assigned_to_content_type: str = typer.Argument(..., help="e.g. project, folder, uploadsdataset"),
    parser_type: str = typer.Argument(..., help="e.g. CSV_VALUE"),
    enabled: bool = typer.Option(True, "--enabled/--disabled"),
    config: Optional[str] = typer.Option(None, "--config", help="Parser config as JSON or @file"),
):
    body: dict = {
        "assigned_to_object_id": assigned_to_object_id,
        "assigned_to_content_type": assigned_to_content_type,
        "parser_type": parser_type,
        "enabled": enabled,
    }
    if config:
        body["config"] = parse_json_arg(config)
    out(await req("POST", "/api/v1/file-parser-configuration/", body=body))


@parser_app.command("update")
async def parser_update(
    config_id: str = typer.Argument(...),
    enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled"),
    config: Optional[str] = typer.Option(None, "--config"),
):
    body: dict = {}
    if enabled is not None:
        body["enabled"] = enabled
    if config:
        body["config"] = parse_json_arg(config)
    if not body:
        console.print("[yellow]No fields to update provided.[/yellow]")
        raise typer.Exit(2)
    out(await req("PATCH", f"/api/v1/file-parser-configuration/{config_id}/", body=body))


@parser_app.command("delete")
async def parser_delete(
    config_id: str = typer.Argument(...),
    confirm: bool = typer.Option(False, "--confirm"),
):
    _confirm(confirm, "Delete parser configuration")
    out(await req("DELETE", f"/api/v1/file-parser-configuration/{config_id}/"))


# ================================================================ EXPORT (data jobs)

export_app = AsyncTyper(help="Export jobs (datasets)", no_args_is_help=True)
app.add_typer(export_app, name="export")


@export_app.command("list")
async def export_list(limit: int = typer.Option(100), offset: int = typer.Option(0)):
    out(await req("GET", "/api/v1/export/", params={"limit": limit, "offset": offset}))


@export_app.command("get")
async def export_get(export_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/export/{export_id}/"))


@export_app.command("download")
async def export_download(
    export_id: str = typer.Argument(...),
    dest_path: str = typer.Argument(...),
    overwrite: bool = typer.Option(False, "--overwrite"),
):
    out(await download_fdm_file(f"/api/v1/export/{export_id}/download/", dest_path, overwrite))


@export_app.command("create")
async def export_create(
    export_type: str = typer.Argument(..., help="projects.project | folders.folder | uploads.uploadsdataset | uploads.uploadsversion"),
    uuids: List[str] = typer.Argument(..., help="UUIDs of the objects to export"),
    format: str = typer.Option("json", "--format", help="json | csv | xml"),
    include_version_file: bool = typer.Option(False, "--include-file"),
    include_version_file_metadata: bool = typer.Option(False, "--include-file-metadata"),
):
    out(await req("POST", "/api/v1/export/", body={
        "export_type": export_type,
        "uuids": uuids,
        "metadata_format": format,
        "include_uploads_version_file": include_version_file,
        "include_uploads_version_file_metadata": include_version_file_metadata,
    }))


# ================================================================ STORAGE

storage_app = AsyncTyper(help="Storage systems", no_args_is_help=True)
app.add_typer(storage_app, name="storage")


@storage_app.command("list")
async def storage_list(limit: int = typer.Option(100)):
    out(await req("GET", "/api/v1/storage/", params={"limit": limit}))


@storage_app.command("get")
async def storage_get(storage_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/storage/{storage_id}/"))


@storage_app.command("create")
async def storage_create(
    name: str = typer.Argument(...),
    storage_type: str = typer.Argument(...),
    local_path: str = typer.Argument(..., help="local_private_dss_path"),
    description: Optional[str] = typer.Option(None, "--description"),
):
    body = {"name": name, "storage_type": storage_type, "local_private_dss_path": local_path}
    if description is not None:
        body["description"] = description
    out(await req("POST", "/api/v1/storage/", body=body))


# ================================================================ APPROVAL-QUEUE

approval_app = AsyncTyper(help="Approval queue (publication approvals)", no_args_is_help=True)
app.add_typer(approval_app, name="approval-queue")


@approval_app.command("list")
async def approval_list(limit: int = typer.Option(100)):
    out(await req("GET", "/api/v1/approval_queue/", params={"limit": limit}))


@approval_app.command("get")
async def approval_get(approval_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/approval_queue/{approval_id}/"))


@approval_app.command("approve")
async def approval_approve(approval_id: str = typer.Argument(...)):
    """Approve (warning: real approval action!)."""
    out(await req("GET", f"/api/v1/approval_queue/{approval_id}/approve/"))


# ================================================================ USER

user_app = AsyncTyper(help="Users", no_args_is_help=True)
app.add_typer(user_app, name="user")


@user_app.command("list")
async def user_list(limit: int = typer.Option(100), search: str = typer.Option("")):
    out(await req("GET", "/api/v1/user/", params={"limit": limit, "search": search}))


@user_app.command("get")
async def user_get(user_id: str = typer.Argument(...)):
    out(await req("GET", f"/api/v1/user/{user_id}/"))


@user_app.command("me")
async def user_me():
    out(await req("GET", "/api/v1/user/me/"))


@user_app.command("me-update")
async def user_me_update(
    settings: Optional[str] = typer.Option(None, "--settings", help="Settings as JSON or @file"),
):
    body: dict = {}
    if settings:
        body["settings"] = parse_json_arg(settings)
    out(await req("PATCH", "/api/v1/user/me/", body=body))


# ================================================================ SYSTEM (Dashboard/Settings/CMS/FAQ)

system_app = AsyncTyper(help="Dashboard, Settings, CMS, FAQ", no_args_is_help=True)
app.add_typer(system_app, name="system")


@system_app.command("dashboard")
async def system_dashboard():
    out(await req("GET", "/api/v1/dashboard/"))


@system_app.command("settings")
async def system_settings(key: Optional[str] = typer.Argument(None, help="Optional settings key")):
    if key:
        out(await req("GET", f"/api/v1/settings/{key}/"))
    else:
        out(await req("GET", "/api/v1/settings/"))


@system_app.command("cms")
async def system_cms(slug: Optional[str] = typer.Argument(None, help="Optional slug")):
    if slug:
        out(await req("GET", f"/api/v1/cms/{slug}/"))
    else:
        out(await req("GET", "/api/v1/cms/"))


@system_app.command("cms-slugs")
async def system_cms_slugs():
    out(await req("GET", "/api/v1/cms/slugs/"))


@system_app.command("faq")
async def system_faq(faq_id: Optional[str] = typer.Argument(None, help="Optional FAQ ID")):
    if faq_id:
        out(await req("GET", f"/api/v1/faq/{faq_id}/"))
    else:
        out(await req("GET", "/api/v1/faq/"))


@system_app.command("search-schema")
async def system_search_schema():
    out(await req("GET", "/api/v1/search/global/schema/"))


@system_app.command("metadata-keys")
async def system_metadata_keys(
    template_id: Optional[str] = typer.Option(None, "--template-id", help="Required: template UUID"),
):
    out(await req("GET", "/api/v1/search/metadata-keys/", params={"template_id": template_id}))


@system_app.command("metadata-choice-options")
async def system_metadata_choice_options(
    template_id: Optional[str] = typer.Option(None, "--template-id", help="Required: template UUID"),
):
    out(await req("GET", "/api/v1/search/metadata-choice-options/", params={"template_id": template_id}))


if __name__ == "__main__":
    app()
