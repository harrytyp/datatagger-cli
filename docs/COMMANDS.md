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

## `api raw`

Arbitrary API call (escape hatch for anything without a dedicated command).

**Signature:** `datatagger api raw <method> <path> <data> <query>`

| Parameter | Type | Description |
|---|---|---|
| `method` | argument **required** | HTTP method: GET/POST/PUT/PATCH/DELETE |
| `path` | argument **required** | API path, e.g. /api/v1/settings/ |
| `data` | argument | JSON body or @file.json |
| `query` | argument | Query param k=v (repeatable) |

## `api auth`

### `api auth login`

Log in with username/password and print access & refresh tokens.

**Signature:** `datatagger api auth login <username> <password>`

| Parameter | Type | Description |
|---|---|---|
| `username` | argument **required** | TUM ID / email |
| `password` | argument | Password (prompted) |

### `api auth verify`

Verify the current token.

**Signature:** `datatagger api auth verify <token>`

| Parameter | Type | Description |
|---|---|---|
| `token` | argument | Token to verify (default: FDM_TOKEN) |

### `api auth refresh`

Exchange a refresh token for a new access token.

**Signature:** `datatagger api auth refresh <refresh>`

| Parameter | Type | Description |
|---|---|---|
| `refresh` | argument **required** | Refresh token |

### `api auth jwt-cookie`

Convert a JWT into an HTTP cookie (web UI auth).

**Signature:** `datatagger api auth jwt-cookie <token>`

| Parameter | Type | Description |
|---|---|---|
| `token` | argument | Token (default: FDM_TOKEN) |

## `api project`

### `api project list`

**Signature:** `datatagger api project list <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument | Max. entries (default: 100) |
| `offset` | argument | Offset (default: 0) |
| `search` | argument | Search filter |

### `api project get`

**Signature:** `datatagger api project get <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** | Project UUID |

### `api project create`

Create a project (MCP high-level for the name; extended fields optional).

**Signature:** `datatagger api project create <name> <description> <folder_name> <users> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** | Project name |
| `description` | argument |  |
| `folder_name` | argument | Create an initial folder |
| `users` | argument | project_users as JSON or @file |
| `metadata` | argument | Metadata as JSON or @file |

### `api project update`

**Signature:** `datatagger api project update <project_id> <name> <description> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `name` | argument |  |
| `description` | argument |  |
| `metadata` | argument |  |

### `api project delete`

**Signature:** `datatagger api project delete <project_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `confirm` | argument | Confirm deletion (default: False) |

### `api project folders`

List the folders of a project.

**Signature:** `datatagger api project folders <project_id> <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

### `api project members`

List the memberships of a project (client-side filtered).

**Signature:** `datatagger api project members <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `api project members-set`

Replace the member array of a project (warning: replaces everything!).

**Signature:** `datatagger api project members-set <project_id> <users>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `users` | argument **required** | project_users as JSON or @file |

### `api project lock`

**Signature:** `datatagger api project lock <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `api project unlock`

**Signature:** `datatagger api project unlock <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `api project status`

**Signature:** `datatagger api project status <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `api project metadata-templates`

**Signature:** `datatagger api project metadata-templates <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `api project template-container-pool`

**Signature:** `datatagger api project template-container-pool <project_id>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |

### `api project membership-list`

**Signature:** `datatagger api project membership-list <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

### `api project membership-create`

**Signature:** `datatagger api project membership-create <project_id> <member> <is_project_admin> <can_create_folders> <is_metadata_template_admin>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `member` | argument **required** | User ID or email |
| `is_project_admin` | argument |  (default: False) |
| `can_create_folders` | argument |  (default: True) |
| `is_metadata_template_admin` | argument |  (default: False) |

### `api project membership-update`

**Signature:** `datatagger api project membership-update <membership_id> <is_project_admin> <can_create_folders> <is_metadata_template_admin>`

| Parameter | Type | Description |
|---|---|---|
| `membership_id` | argument **required** |  |
| `is_project_admin` | argument |  |
| `can_create_folders` | argument |  |
| `is_metadata_template_admin` | argument |  |

### `api project membership-delete`

**Signature:** `datatagger api project membership-delete <membership_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `membership_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

## `api folder`

### `api folder list`

**Signature:** `datatagger api folder list <project> <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `project` | argument | Filter by project UUID |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |
| `search` | argument |  |

### `api folder get`

**Signature:** `datatagger api folder get <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `api folder create`

Create a folder (MCP high-level for name+project; extended fields optional).

**Signature:** `datatagger api folder create <project_id> <name> <description> <storage> <metadata> <users>`

| Parameter | Type | Description |
|---|---|---|
| `project_id` | argument **required** |  |
| `name` | argument **required** |  |
| `description` | argument |  |
| `storage` | argument |  |
| `metadata` | argument |  |
| `users` | argument |  |

### `api folder update`

**Signature:** `datatagger api folder update <folder_id> <name> <description> <storage> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |
| `name` | argument |  |
| `description` | argument |  |
| `storage` | argument |  |
| `metadata` | argument |  |

### `api folder delete`

**Signature:** `datatagger api folder delete <folder_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

### `api folder lock`

**Signature:** `datatagger api folder lock <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `api folder unlock`

**Signature:** `datatagger api folder unlock <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `api folder status`

**Signature:** `datatagger api folder status <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `api folder permissions`

List the active user permissions of a folder.

**Signature:** `datatagger api folder permissions <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `api folder set-permissions`

Set the permission array of a folder.

**Signature:** `datatagger api folder set-permissions <folder_id> <users>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |
| `users` | argument **required** | folder_users as JSON or @file |

### `api folder metadata-templates`

**Signature:** `datatagger api folder metadata-templates <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

### `api folder template-container-pool`

**Signature:** `datatagger api folder template-container-pool <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `folder_id` | argument **required** |  |

## `api dataset`

### `api dataset list`

**Signature:** `datatagger api dataset list <folder> <name> <status> <locked> <created_by> <ordering> <limit> <offset> <search>`

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

### `api dataset get`

**Signature:** `datatagger api dataset get <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `api dataset create`

**Signature:** `datatagger api dataset create <name> <folder_id>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** |  |
| `folder_id` | argument | Folder UUID (otherwise draft) |

### `api dataset update`

**Signature:** `datatagger api dataset update <dataset_id> <name> <metadata_template>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `name` | argument |  |
| `metadata_template` | argument |  |

### `api dataset delete`

**Signature:** `datatagger api dataset delete <dataset_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

### `api dataset publish`

Finalize/publish a dataset.

**Signature:** `datatagger api dataset publish <dataset_id> <folder>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `folder` | argument | Optional target folder |

### `api dataset restore`

Restore a dataset to a historical version.

**Signature:** `datatagger api dataset restore <dataset_id> <version_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `version_id` | argument **required** | uploads_version UUID |

### `api dataset compare`

Diff between two dataset versions (GET endpoint of the current API).

**Signature:** `datatagger api dataset compare <version_id> <compare_to_id>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `compare_to_id` | argument **required** | other uploads_version UUID |

### `api dataset upload`

Upload a file into a dataset (TUS protocol, like the web UI).

**Signature:** `datatagger api dataset upload <dataset_id> <source_path>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `source_path` | argument **required** | Local file (TUS resumable) |

### `api dataset file-upload`

Upload a file via legacy multipart (POST /file/).

**Signature:** `datatagger api dataset file-upload <dataset_id> <source_path>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `source_path` | argument **required** |  |

### `api dataset add-metadata`

Append metadata tags to a dataset (creates a new version).

**Signature:** `datatagger api dataset add-metadata <dataset_id> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `metadata` | argument **required** | Metadata items as JSON or @file |

### `api dataset new-version`

Create a new version of a dataset.

**Signature:** `datatagger api dataset new-version <dataset_id> <name> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `name` | argument |  |
| `metadata` | argument |  |

### `api dataset reference`

Reference an existing storage file.

**Signature:** `datatagger api dataset reference <dataset_id> <filepath>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `filepath` | argument **required** | Path to an existing file on the storage |

### `api dataset lock`

**Signature:** `datatagger api dataset lock <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `api dataset unlock`

**Signature:** `datatagger api dataset unlock <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `api dataset status`

**Signature:** `datatagger api dataset status <dataset_id>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |

### `api dataset bulk-delete`

**Signature:** `datatagger api dataset bulk-delete <dataset_ids> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_ids` | argument **required** | Dataset UUIDs |
| `confirm` | argument |  (default: False) |

### `api dataset bulk-publish`

**Signature:** `datatagger api dataset bulk-publish <folder> <dataset_ids>`

| Parameter | Type | Description |
|---|---|---|
| `folder` | argument **required** | Target folder UUID |
| `dataset_ids` | argument **required** | Dataset UUIDs |

### `api dataset bulk-upgrade`

Bulk: trigger a metadata template upgrade.

**Signature:** `datatagger api dataset bulk-upgrade <dataset_ids>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_ids` | argument **required** | Dataset UUIDs |

### `api dataset upgrade`

Metadata template upgrade of a dataset (one mode required).

**Signature:** `datatagger api dataset upgrade <dataset_id> <status> <payload> <submit> <resolve_conflict> <json_data>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | argument **required** |  |
| `status` | argument | Query upgrade status (default: False) |
| `payload` | argument | Query upgrade payload (default: False) |
| `submit` | argument | Run upgrade (default: False) |
| `resolve_conflict` | argument | Resolve conflict (default: False) |
| `json_data` | argument | JSON for --resolve-conflict (base_version_pk, resolutions) |

## `api version`

### `api version list`

**Signature:** `datatagger api version list <dataset> <dataset_folder> <limit> <offset> <search>`

| Parameter | Type | Description |
|---|---|---|
| `dataset` | argument | Filter by dataset UUID |
| `dataset_folder` | argument | Filter by dataset__folder |
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |
| `search` | argument |  |

### `api version get`

**Signature:** `datatagger api version get <version_id>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |

### `api version update`

**Signature:** `datatagger api version update <version_id> <name> <status>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `name` | argument |  |
| `status` | argument | SCHEDULED/IN_PROGRESS/ERROR/FINISHED |

### `api version status`

**Signature:** `datatagger api version status <version_id>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |

### `api version download`

**Signature:** `datatagger api version download <version_id> <dest_path> <overwrite>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `dest_path` | argument **required** | Local destination path |
| `overwrite` | argument |  (default: False) |

### `api version diff`

Diff between two versions (GET endpoint of the current API).

**Signature:** `datatagger api version diff <version_id> <compare>`

| Parameter | Type | Description |
|---|---|---|
| `version_id` | argument **required** |  |
| `compare` | argument **required** | Version to compare (uploads_version UUID) |

## `api version-file`

### `api version-file get`

**Signature:** `datatagger api version-file get <file_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |

### `api version-file parser-processing`

**Signature:** `datatagger api version-file parser-processing <file_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |

### `api version-file retrigger-parser`

**Signature:** `datatagger api version-file retrigger-parser <file_id> <parser_type>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |
| `parser_type` | argument | e.g. CSV_VALUE |

### `api version-file retry-processing`

**Signature:** `datatagger api version-file retry-processing <file_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_id` | argument **required** |  |

## `api metadata`

### `api metadata list`

**Signature:** `datatagger api metadata list <search> <limit>`

| Parameter | Type | Description |
|---|---|---|
| `search` | argument |  |
| `limit` | argument |  (default: 100) |

### `api metadata get`

**Signature:** `datatagger api metadata get <metadata_id>`

| Parameter | Type | Description |
|---|---|---|
| `metadata_id` | argument **required** |  |

### `api metadata tags`

**Signature:** `datatagger api metadata tags <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

### `api metadata tag`

**Signature:** `datatagger api metadata tag <tag_id>`

| Parameter | Type | Description |
|---|---|---|
| `tag_id` | argument **required** |  |

### `api metadata fields`

**Signature:** `datatagger api metadata fields <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

### `api metadata field`

**Signature:** `datatagger api metadata field <field_id>`

| Parameter | Type | Description |
|---|---|---|
| `field_id` | argument **required** |  |

### `api metadata bulk-add`

Apply metadata to multiple datasets at once.

**Signature:** `datatagger api metadata bulk-add <dataset_ids> <metadata>`

| Parameter | Type | Description |
|---|---|---|
| `dataset_ids` | argument **required** | Dataset UUIDs |
| `metadata` | argument **required** | Metadata items as JSON or @file |

### `api metadata template`

#### `metadata template list`

**Signature:** `datatagger api metadata template list <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

#### `metadata template get`

**Signature:** `datatagger api metadata template get <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

#### `metadata template update`

**Signature:** `datatagger api metadata template update <template_id> <name>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |
| `name` | argument |  |

#### `metadata template diff`

**Signature:** `datatagger api metadata template diff <template_id> <compare>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |
| `compare` | argument **required** | Template UUID to compare |

#### `metadata template lock`

**Signature:** `datatagger api metadata template lock <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

#### `metadata template unlock`

**Signature:** `datatagger api metadata template unlock <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

#### `metadata template status`

**Signature:** `datatagger api metadata template status <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument **required** |  |

### `api metadata container`

#### `metadata container list`

**Signature:** `datatagger api metadata container list <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

#### `metadata container get`

**Signature:** `datatagger api metadata container get <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container create`

**Signature:** `datatagger api metadata container create <name> <assigned_to_content_type> <assigned_to_object_id> <fields>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** |  |
| `assigned_to_content_type` | argument |  |
| `assigned_to_object_id` | argument |  |
| `fields` | argument | metadata_template_fields as JSON or @file |

#### `metadata container update`

**Signature:** `datatagger api metadata container update <container_id> <name> <fields>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `name` | argument |  |
| `fields` | argument |  |

#### `metadata container clone`

**Signature:** `datatagger api metadata container clone <container_id> <assigned_to_content_type> <assigned_to_object_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `assigned_to_content_type` | argument |  |
| `assigned_to_object_id` | argument |  |

#### `metadata container lock`

**Signature:** `datatagger api metadata container lock <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container unlock`

**Signature:** `datatagger api metadata container unlock <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container status`

**Signature:** `datatagger api metadata container status <container_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |

#### `metadata container version`

**Signature:** `datatagger api metadata container version <container_id> <name> <fields>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `name` | argument |  |
| `fields` | argument |  |

#### `metadata container restore`

**Signature:** `datatagger api metadata container restore <container_id> <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `container_id` | argument **required** |  |
| `template_id` | argument **required** | metadata_template UUID (target version) |

#### `metadata container import`

Import a template container from a file (multipart).

**Signature:** `datatagger api metadata container import <file_path> <assigned_to_content_type> <assigned_to_object_id>`

| Parameter | Type | Description |
|---|---|---|
| `file_path` | argument **required** | Template file (.json) |
| `assigned_to_content_type` | argument |  |
| `assigned_to_object_id` | argument |  |

#### `metadata container pool`

Query the available template container pool of a resource.

**Signature:** `datatagger api metadata container pool <resource_type> <resource_id>`

| Parameter | Type | Description |
|---|---|---|
| `resource_type` | argument **required** | project | folder | dataset |
| `resource_id` | argument **required** |  |

### `api metadata export`

#### `metadata export list`

**Signature:** `datatagger api metadata export list <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

#### `metadata export get`

**Signature:** `datatagger api metadata export get <export_id>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |

#### `metadata export download`

**Signature:** `datatagger api metadata export download <export_id> <dest_path> <overwrite>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |
| `dest_path` | argument **required** |  |
| `overwrite` | argument |  (default: False) |

#### `metadata export create`

**Signature:** `datatagger api metadata export create <container_ids> <format>`

| Parameter | Type | Description |
|---|---|---|
| `container_ids` | argument **required** | Container UUIDs |
| `format` | argument | json | csv | xml (default: json) |

## `api parser-config`

### `api parser-config list`

**Signature:** `datatagger api parser-config list <limit>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |

### `api parser-config get`

**Signature:** `datatagger api parser-config get <config_id>`

| Parameter | Type | Description |
|---|---|---|
| `config_id` | argument **required** |  |

### `api parser-config available-types`


### `api parser-config create`

**Signature:** `datatagger api parser-config create <assigned_to_object_id> <assigned_to_content_type> <parser_type> <enabled> <config>`

| Parameter | Type | Description |
|---|---|---|
| `assigned_to_object_id` | argument **required** | Resource UUID |
| `assigned_to_content_type` | argument **required** | e.g. project, folder, uploadsdataset |
| `parser_type` | argument **required** | e.g. CSV_VALUE |
| `enabled` | argument |  (default: True) |
| `config` | argument | Parser config as JSON or @file |

### `api parser-config update`

**Signature:** `datatagger api parser-config update <config_id> <enabled> <config>`

| Parameter | Type | Description |
|---|---|---|
| `config_id` | argument **required** |  |
| `enabled` | argument |  |
| `config` | argument |  |

### `api parser-config delete`

**Signature:** `datatagger api parser-config delete <config_id> <confirm>`

| Parameter | Type | Description |
|---|---|---|
| `config_id` | argument **required** |  |
| `confirm` | argument |  (default: False) |

## `api export`

### `api export list`

**Signature:** `datatagger api export list <limit> <offset>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `offset` | argument |  (default: 0) |

### `api export get`

**Signature:** `datatagger api export get <export_id>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |

### `api export download`

**Signature:** `datatagger api export download <export_id> <dest_path> <overwrite>`

| Parameter | Type | Description |
|---|---|---|
| `export_id` | argument **required** |  |
| `dest_path` | argument **required** |  |
| `overwrite` | argument |  (default: False) |

### `api export create`

**Signature:** `datatagger api export create <export_type> <uuids> <format> <include_version_file> <include_version_file_metadata>`

| Parameter | Type | Description |
|---|---|---|
| `export_type` | argument **required** | projects.project | folders.folder | uploads.uploadsdataset | uploads.uploadsversion |
| `uuids` | argument **required** | UUIDs of the objects to export |
| `format` | argument | json | csv | xml (default: json) |
| `include_version_file` | argument |  (default: False) |
| `include_version_file_metadata` | argument |  (default: False) |

## `api storage`

### `api storage list`

**Signature:** `datatagger api storage list <limit>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |

### `api storage get`

**Signature:** `datatagger api storage get <storage_id>`

| Parameter | Type | Description |
|---|---|---|
| `storage_id` | argument **required** |  |

### `api storage create`

**Signature:** `datatagger api storage create <name> <storage_type> <local_path> <description>`

| Parameter | Type | Description |
|---|---|---|
| `name` | argument **required** |  |
| `storage_type` | argument **required** |  |
| `local_path` | argument **required** | local_private_dss_path |
| `description` | argument |  |

## `api approval-queue`

### `api approval-queue list`

**Signature:** `datatagger api approval-queue list <limit>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |

### `api approval-queue get`

**Signature:** `datatagger api approval-queue get <approval_id>`

| Parameter | Type | Description |
|---|---|---|
| `approval_id` | argument **required** |  |

### `api approval-queue approve`

Approve (warning: real approval action!).

**Signature:** `datatagger api approval-queue approve <approval_id>`

| Parameter | Type | Description |
|---|---|---|
| `approval_id` | argument **required** |  |

## `api user`

### `api user list`

**Signature:** `datatagger api user list <limit> <search>`

| Parameter | Type | Description |
|---|---|---|
| `limit` | argument |  (default: 100) |
| `search` | argument |  |

### `api user get`

**Signature:** `datatagger api user get <user_id>`

| Parameter | Type | Description |
|---|---|---|
| `user_id` | argument **required** |  |

### `api user me`


### `api user me-update`

**Signature:** `datatagger api user me-update <settings>`

| Parameter | Type | Description |
|---|---|---|
| `settings` | argument | Settings as JSON or @file |

## `api system`

### `api system dashboard`


### `api system settings`

**Signature:** `datatagger api system settings <key>`

| Parameter | Type | Description |
|---|---|---|
| `key` | argument | Optional settings key |

### `api system cms`

**Signature:** `datatagger api system cms <slug>`

| Parameter | Type | Description |
|---|---|---|
| `slug` | argument | Optional slug |

### `api system cms-slugs`


### `api system faq`

**Signature:** `datatagger api system faq <faq_id>`

| Parameter | Type | Description |
|---|---|---|
| `faq_id` | argument | Optional FAQ ID |

### `api system search-schema`


### `api system metadata-keys`

**Signature:** `datatagger api system metadata-keys <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument | Required: template UUID |

### `api system metadata-choice-options`

**Signature:** `datatagger api system metadata-choice-options <template_id>`

| Parameter | Type | Description |
|---|---|---|
| `template_id` | argument | Required: template UUID |
