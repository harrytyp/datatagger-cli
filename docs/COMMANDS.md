# Command Reference

Complete reference for every `datatagger` command. All commands require 
`FDM_TOKEN` (the `token` cookie from datatagger.ub.tum.de, sent as Bearer) 
and optionally `FDM_BASE_URL` as environment variables.

JSON arguments accept inline JSON or `@path/to/file.json`.

Destructive operations require `--confirm`.

## `search`

Search globally across projects, folders, datasets, files and templates.

**Signature:** `datatagger search <term> <limit>`

| Parameter | Type | Description |
|---|---|---|
| `term` | argument **required** | Search term |
| `limit` | argument | Max. results (1–100) (default: 25) |

## `raw`

Arbitrary API call (escape hatch for anything without a dedicated command).

**Signature:** `datatagger raw <method> <path> <data> <query>`

| Parameter | Type | Description |
|---|---|---|
| `method` | argument **required** | HTTP method: GET/POST/PUT/PATCH/DELETE |
| `path` | argument **required** | API path, e.g. /api/v1/settings/ |
| `data` | argument | JSON body or @file.json |
| `query` | argument | Query param k=v (repeatable) |

## `auth`

### `auth login`

Log in with username/password and print access & refresh tokens.

**Signature:** `datatagger auth login <username> <password>`

| Parameter | Type | Description |
|---|---|---|
| `username` | argument **required** | TUM ID / email |
| `password` | argument | Password (prompted) |

### `auth verify`

Verify the current token.

**Signature:** `datatagger auth verify <token>`

| Parameter | Type | Description |
|---|---|---|
| `token` | argument | Token to verify (default: FDM_TOKEN) |

### `auth refresh`

Exchange a refresh token for a new access token.

**Signature:** `datatagger auth refresh <refresh>`

| Parameter | Type | Description |
|---|---|---|
| `refresh` | argument **required** | Refresh token |

### `auth jwt-cookie`

Convert a JWT into an HTTP cookie (web UI auth).

**Signature:** `datatagger auth jwt-cookie <token>`

| Parameter | Type | Description |
|---|---|---|
| `token` | argument | Token (default: FDM_TOKEN) |

## `project`

### `project list`

**Signature:** `datatagger project list <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument | Max. entries (default: 100) |
| `offset` | argument | Offset (default: 0) |
| `search` | argument | Search filter |

### `project get`

**Signature:** `datatagger project get <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** | Project UUID |

### `project create`

Create a project (MCP high-level for the name; extended fields optional).

**Signature:** `datatagger project create <name> <description> <folder_name> <users> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** | Project name |
| `description` | argument |  |
| `folder_name` | argument | Create an initial folder |
| `users` | argument | project_users as JSON or @file |
| `metadata` | argument | Metadata as JSON or @file |

### `project update`

**Signature:** `datatagger project update <project_id> <name> <description> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `name` | argument |  |
| `description` | argument |  |
| `metadata` | argument |  |

### `project delete`

**Signature:** `datatagger project delete <project_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `confirm` | argument | Confirm deletion (default: False) |

### `project folders`

List the folders of a project.

**Signature:** `datatagger project folders <project_id> <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

### `project members`

List the memberships of a project (client-side filtered).

**Signature:** `datatagger project members <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `project members-set`

Replace the member array of a project (warning: replaces everything!).

**Signature:** `datatagger project members-set <project_id> <users>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `users` | argument **required** | project_users as JSON or @file |

### `project lock`

**Signature:** `datatagger project lock <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `project unlock`

**Signature:** `datatagger project unlock <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `project status`

**Signature:** `datatagger project status <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `project metadata-templates`

**Signature:** `datatagger project metadata-templates <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `project template-container-pool`

**Signature:** `datatagger project template-container-pool <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `project membership-list`

**Signature:** `datatagger project membership-list <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

### `project membership-create`

**Signature:** `datatagger project membership-create <project_id> <member> <is_project_admin> <can_create_folders> <is_metadata_template_admin>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `member` | argument **required** | User ID or email |
| `is_project_admin` | argument |  (default: False) |
| `can_create_folders` | argument |  (default: True) |
| `is_metadata_template_admin` | argument |  (default: False) |

### `project membership-update`

**Signature:** `datatagger project membership-update <membership_id> <is_project_admin> <can_create_folders> <is_metadata_template_admin>`

| Parameter | Type | Description |
|---|---|---|
| `membership_id` | argument **required** |  |
| `is_project_admin` | argument |  |
| `can_create_folders` | argument |  |
| `is_metadata_template_admin` | argument |  |

### `project membership-delete`

**Signature:** `datatagger project membership-delete <membership_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `membership_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

## `folder`

### `folder list`

**Signature:** `datatagger folder list <project> <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `project` | argument | Filter by project UUID |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |
| `search` | argument |  |

### `folder get`

**Signature:** `datatagger folder get <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `folder create`

Create a folder (MCP high-level for name+project; extended fields optional).

**Signature:** `datatagger folder create <project_id> <name> <description> <storage> <metadata> <users>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `name` | argument **required** |  |
| `description` | argument |  |
| `storage` | argument |  |
| `metadata` | argument |  |
| `users` | argument |  |

### `folder update`

**Signature:** `datatagger folder update <folder_id> <name> <description> <storage> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |
| `name` | argument |  |
| `description` | argument |  |
| `storage` | argument |  |
| `metadata` | argument |  |

### `folder delete`

**Signature:** `datatagger folder delete <folder_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

### `folder lock`

**Signature:** `datatagger folder lock <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `folder unlock`

**Signature:** `datatagger folder unlock <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `folder status`

**Signature:** `datatagger folder status <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `folder permissions`

List the active user permissions of a folder.

**Signature:** `datatagger folder permissions <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `folder set-permissions`

Set the permission array of a folder.

**Signature:** `datatagger folder set-permissions <folder_id> <users>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |
| `users` | argument **required** | folder_users as JSON or @file |

### `folder metadata-templates`

**Signature:** `datatagger folder metadata-templates <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `folder template-container-pool`

**Signature:** `datatagger folder template-container-pool <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

## `dataset`

### `dataset list`

**Signature:** `datatagger dataset list <folder> <name> <status> <locked> <created_by> <ordering> <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `folder` | argument | Filter by folder UUID |
| `name` | argument | Filter by name |
| `status` | argument | Filter by status (e.g. PUBLISHED) |
| `locked` | argument |  |
| `created_by` | argument |  |
| `ordering` | argument | e.g. -creation_date |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |
| `search` | argument |  |

### `dataset get`

**Signature:** `datatagger dataset get <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `dataset create`

**Signature:** `datatagger dataset create <name> <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** |  |
| `folder_id` | argument | Folder UUID (otherwise draft) |

### `dataset update`

**Signature:** `datatagger dataset update <dataset_id> <name> <metadata_template>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `name` | argument |  |
| `metadata_template` | argument |  |

### `dataset delete`

**Signature:** `datatagger dataset delete <dataset_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

### `dataset publish`

Finalize/publish a dataset.

**Signature:** `datatagger dataset publish <dataset_id> <folder>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `folder` | argument | Optional target folder |

### `dataset restore`

Restore a dataset to a historical version.

**Signature:** `datatagger dataset restore <dataset_id> <version_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `version_id` | argument **required** | uploads_version UUID |

### `dataset compare`

Diff between two dataset versions (GET endpoint of the current API).

**Signature:** `datatagger dataset compare <version_id> <compare_to_id>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `compare_to_id` | argument **required** | other uploads_version UUID |

### `dataset upload`

Upload a file into a dataset (TUS protocol, like the web UI).

**Signature:** `datatagger dataset upload <dataset_id> <source_path>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `source_path` | argument **required** | Local file (TUS resumable) |

### `dataset file-upload`

Upload a file via legacy multipart (POST /file/).

**Signature:** `datatagger dataset file-upload <dataset_id> <source_path>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `source_path` | argument **required** |  |

### `dataset add-metadata`

Append metadata tags to a dataset (creates a new version).

**Signature:** `datatagger dataset add-metadata <dataset_id> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `metadata` | argument **required** | Metadata items as JSON or @file |

### `dataset new-version`

Create a new version of a dataset.

**Signature:** `datatagger dataset new-version <dataset_id> <name> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `name` | argument |  |
| `metadata` | argument |  |

### `dataset reference`

Reference an existing storage file.

**Signature:** `datatagger dataset reference <dataset_id> <filepath>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `filepath` | argument **required** | Path to an existing file on the storage |

### `dataset lock`

**Signature:** `datatagger dataset lock <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `dataset unlock`

**Signature:** `datatagger dataset unlock <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `dataset status`

**Signature:** `datatagger dataset status <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `dataset bulk-delete`

**Signature:** `datatagger dataset bulk-delete <dataset_ids> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_ids` | argument **required** | Dataset UUIDs |
| `confirm` | argument |  (default: False) |

### `dataset bulk-publish`

**Signature:** `datatagger dataset bulk-publish <folder> <dataset_ids>`

| Parameter | Type | Description |
|---|---|---|
| `folder` | argument **required** | Target folder UUID |
| `dataset_ids` | argument **required** | Dataset UUIDs |

### `dataset bulk-upgrade`

Bulk: trigger a metadata template upgrade.

**Signature:** `datatagger dataset bulk-upgrade <dataset_ids>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_ids` | argument **required** | Dataset UUIDs |

### `dataset upgrade`

Metadata template upgrade of a dataset (one mode required).

**Signature:** `datatagger dataset upgrade <dataset_id> <status> <payload> <submit> <resolve_conflict> <json_data>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `status` | argument | Query upgrade status (default: False) |
| `payload` | argument | Query upgrade payload (default: False) |
| `submit` | argument | Run upgrade (default: False) |
| `resolve_conflict` | argument | Resolve conflict (default: False) |
| `json_data` | argument | JSON for --resolve-conflict (base_version_pk, resolutions) |

## `version`

### `version list`

**Signature:** `datatagger version list <dataset> <dataset_folder> <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `dataset` | argument | Filter by dataset UUID |
| `dataset_folder` | argument | Filter by dataset__folder |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |
| `search` | argument |  |

### `version get`

**Signature:** `datatagger version get <version_id>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |

### `version update`

**Signature:** `datatagger version update <version_id> <name> <status>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `name` | argument |  |
| `status` | argument | SCHEDULED/IN_PROGRESS/ERROR/FINISHED |

### `version status`

**Signature:** `datatagger version status <version_id>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |

### `version download`

**Signature:** `datatagger version download <version_id> <dest_path> <overwrite>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `dest_path` | argument **required** | Local destination path |
| `overwrite` | argument |  (default: False) |

### `version diff`

Diff between two versions (GET endpoint of the current API).

**Signature:** `datatagger version diff <version_id> <compare>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `compare` | argument **required** | Version to compare (uploads_version UUID) |

## `version-file`

### `version-file get`

**Signature:** `datatagger version-file get <file_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |

### `version-file parser-processing`

**Signature:** `datatagger version-file parser-processing <file_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |

### `version-file retrigger-parser`

**Signature:** `datatagger version-file retrigger-parser <file_id> <parser_type>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |
| `parser_type` | argument | e.g. CSV_VALUE |

### `version-file retry-processing`

**Signature:** `datatagger version-file retry-processing <file_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |

## `metadata`

### `metadata list`

**Signature:** `datatagger metadata list <search> <limit>`

| Parameter | Type | Description |
|---|---|---|
| `search` | argument |  |
| `limit` | argument |  (default: 100) |

### `metadata get`

**Signature:** `datatagger metadata get <metadata_id>`

| Parameter | Type | Description |
|---|---|---|
| `metadata_id` | argument **required** |  |

### `metadata tags`

**Signature:** `datatagger metadata tags <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

### `metadata tag`

**Signature:** `datatagger metadata tag <tag_id>`

| Parameter | Type | Description |
|---|---|---|
| `tag_id` | argument **required** |  |

### `metadata fields`

**Signature:** `datatagger metadata fields <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

### `metadata field`

**Signature:** `datatagger metadata field <field_id>`

| Parameter | Type | Description |
|---|---|---|
| `field_id` | argument **required** |  |

### `metadata bulk-add`

Apply metadata to multiple datasets at once.

**Signature:** `datatagger metadata bulk-add <dataset_ids> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_ids` | argument **required** | Dataset UUIDs |
| `metadata` | argument **required** | Metadata items as JSON or @file |

### `metadata template`

#### `metadata template list`

**Signature:** `datatagger metadata template list <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

#### `metadata template get`

**Signature:** `datatagger metadata template get <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

#### `metadata template update`

**Signature:** `datatagger metadata template update <template_id> <name>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |
| `name` | argument |  |

#### `metadata template diff`

**Signature:** `datatagger metadata template diff <template_id> <compare>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |
| `compare` | argument **required** | Template UUID to compare |

#### `metadata template lock`

**Signature:** `datatagger metadata template lock <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

#### `metadata template unlock`

**Signature:** `datatagger metadata template unlock <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

#### `metadata template status`

**Signature:** `datatagger metadata template status <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

### `metadata container`

#### `metadata container list`

**Signature:** `datatagger metadata container list <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

#### `metadata container get`

**Signature:** `datatagger metadata container get <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container create`

**Signature:** `datatagger metadata container create <name> <assigned_to_content_type> <assigned_to_object_id> <fields>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** |  |
| `assigned_to_content_type` | argument |  |
| `assigned_to_object_id` | argument |  |
| `fields` | argument | metadata_template_fields as JSON or @file |

#### `metadata container update`

**Signature:** `datatagger metadata container update <container_id> <name> <fields>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `name` | argument |  |
| `fields` | argument |  |

#### `metadata container clone`

**Signature:** `datatagger metadata container clone <container_id> <assigned_to_content_type> <assigned_to_object_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `assigned_to_content_type` | argument |  |
| `assigned_to_object_id` | argument |  |

#### `metadata container lock`

**Signature:** `datatagger metadata container lock <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container unlock`

**Signature:** `datatagger metadata container unlock <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container status`

**Signature:** `datatagger metadata container status <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container version`

**Signature:** `datatagger metadata container version <container_id> <name> <fields>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `name` | argument |  |
| `fields` | argument |  |

#### `metadata container restore`

**Signature:** `datatagger metadata container restore <container_id> <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `template_id` | argument **required** | metadata_template UUID (target version) |

#### `metadata container import`

Import a template container from a file (multipart).

**Signature:** `datatagger metadata container import <file_path> <assigned_to_content_type> <assigned_to_object_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_path` | argument **required** | Template file (.json) |
| `assigned_to_content_type` | argument |  |
| `assigned_to_object_id` | argument |  |

#### `metadata container pool`

Query the available template container pool of a resource.

**Signature:** `datatagger metadata container pool <resource_type> <resource_id>`

| Parameter | Type | Description |
|---|---|---|
| `resource_type` | argument **required** | project | folder | dataset |
| `resource_id` | argument **required** |  |

### `metadata export`

#### `metadata export list`

**Signature:** `datatagger metadata export list <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

#### `metadata export get`

**Signature:** `datatagger metadata export get <export_id>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |

#### `metadata export download`

**Signature:** `datatagger metadata export download <export_id> <dest_path> <overwrite>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |
| `dest_path` | argument **required** |  |
| `overwrite` | argument |  (default: False) |

#### `metadata export create`

**Signature:** `datatagger metadata export create <container_ids> <format>`

| Parameter | Type | Description |
|---|---|---|
| `container_ids` | argument **required** | Container UUIDs |
| `format` | argument | json | csv | xml (default: json) |

## `parser-config`

### `parser-config list`

**Signature:** `datatagger parser-config list <limit>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |

### `parser-config get`

**Signature:** `datatagger parser-config get <config_id>`

| Parameter | Type | Description |
|---|---|---|
| `config_id` | argument **required** |  |

### `parser-config available-types`


### `parser-config create`

**Signature:** `datatagger parser-config create <assigned_to_object_id> <assigned_to_content_type> <parser_type> <enabled> <config>`

| Parameter | Type | Description |
|---|---|---|
| `assigned_to_object_id` | argument **required** | Resource UUID |
| `assigned_to_content_type` | argument **required** | e.g. project, folder, uploadsdataset |
| `parser_type` | argument **required** | e.g. CSV_VALUE |
| `enabled` | argument |  (default: True) |
| `config` | argument | Parser config as JSON or @file |

### `parser-config update`

**Signature:** `datatagger parser-config update <config_id> <enabled> <config>`

| Parameter | Type | Description |
|---|---|---|
| `config_id` | argument **required** |  |
| `enabled` | argument |  |
| `config` | argument |  |

### `parser-config delete`

**Signature:** `datatagger parser-config delete <config_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `config_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

## `export`

### `export list`

**Signature:** `datatagger export list <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

### `export get`

**Signature:** `datatagger export get <export_id>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |

### `export download`

**Signature:** `datatagger export download <export_id> <dest_path> <overwrite>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |
| `dest_path` | argument **required** |  |
| `overwrite` | argument |  (default: False) |

### `export create`

**Signature:** `datatagger export create <export_type> <uuids> <format> <include_version_file> <include_version_file_metadata>`

| Parameter | Type | Description |
|---|---|---|
| `export_type` | argument **required** | projects.project | folders.folder | uploads.uploadsdataset | uploads.uploadsversion |
| `uuids` | argument **required** | UUIDs of the objects to export |
| `format` | argument | json | csv | xml (default: json) |
| `include_version_file` | argument |  (default: False) |
| `include_version_file_metadata` | argument |  (default: False) |

## `storage`

### `storage list`

**Signature:** `datatagger storage list <limit>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |

### `storage get`

**Signature:** `datatagger storage get <storage_id>`

| Parameter | Type | Description |
|---|---|---|
| `storage_id` | argument **required** |  |

### `storage create`

**Signature:** `datatagger storage create <name> <storage_type> <local_path> <description>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** |  |
| `storage_type` | argument **required** |  |
| `local_path` | argument **required** | local_private_dss_path |
| `description` | argument |  |

## `approval-queue`

### `approval-queue list`

**Signature:** `datatagger approval-queue list <limit>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |

### `approval-queue get`

**Signature:** `datatagger approval-queue get <approval_id>`

| Parameter | Type | Description |
|---|---|---|
| `approval_id` | argument **required** |  |

### `approval-queue approve`

Approve (warning: real approval action!).

**Signature:** `datatagger approval-queue approve <approval_id>`

| Parameter | Type | Description |
|---|---|---|
| `approval_id` | argument **required** |  |

## `user`

### `user list`

**Signature:** `datatagger user list <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

### `user get`

**Signature:** `datatagger user get <user_id>`

| Parameter | Type | Description |
|---|---|---|
| `user_id` | argument **required** |  |

### `user me`


### `user me-update`

**Signature:** `datatagger user me-update <settings>`

| Parameter | Type | Description |
|---|---|---|
| `settings` | argument | Settings as JSON or @file |

## `system`

### `system dashboard`


### `system settings`

**Signature:** `datatagger system settings <key>`

| Parameter | Type | Description |
|---|---|---|
| `key` | argument | Optional settings key |

### `system cms`

**Signature:** `datatagger system cms <slug>`

| Parameter | Type | Description |
|---|---|---|
| `slug` | argument | Optional slug |

### `system cms-slugs`


### `system faq`

**Signature:** `datatagger system faq <faq_id>`

| Parameter | Type | Description |
|---|---|---|
| `faq_id` | argument | Optional FAQ ID |

### `system search-schema`


### `system metadata-keys`

**Signature:** `datatagger system metadata-keys <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument | Required: template UUID |

### `system metadata-choice-options`

**Signature:** `datatagger system metadata-choice-options <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument | Required: template UUID |
