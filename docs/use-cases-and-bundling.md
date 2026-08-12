# DataTagger CLI — Use Cases & Bundling Analysis

Status: **analysis only** — no code changes yet. All endpoints/methods verified against `src/datatagger_cli/cli.py` (2026-08-12).

## 1. Goal & Principles

The CLI currently exposes 124 commands, most of them 1:1 mirrors of single API calls ("API browser"). The goal is:

> **A CLI command is a task, not an API call.** A task often needs several API calls (e.g. "upload a file" = create dataset + TUS init + PATCH). The MCP defines the reference semantics for such operations; the CLI should bundle the same tasks into chains.

- **No removal**: single commands stay as building blocks. Bundling means adding task-level chains on top.
- **No all-in-one composite**: the `new-dataset` pattern (project → folder → dataset → file → metadata → publish in one shot) is rejected as too broad. Chains end at meaningful task boundaries.
- **MCP parity**: where the MCP already bundles (TUS upload = 2 calls + finalisation, README "Folder/Draft upload" workflows), the CLI should offer the same as one command.

## 2. Inventory (124 commands)

| Area | Commands | Count |
|---|---|---|
| Top-level | `search`, `raw` (escape hatch), `new-dataset` (rejected pattern) | 3 |
| `auth` | login, verify, refresh, jwt-cookie | 4 |
| `project` | list, get, create, update, delete, folders, members, members-set, lock, unlock, status, metadata-templates, template-container-pool, membership-list/create/update/delete | 17 |
| `folder` | list, get, create, update, delete, lock, unlock, status, permissions, set-permissions, metadata-templates, template-container-pool | 12 |
| `user` | list, get, me, me-update | 4 |
| `dataset` | list, get, create, update, delete, publish, restore, compare, upload, file-upload, add-metadata, new-version, reference, lock, unlock, status, bulk-delete, bulk-publish, bulk-upgrade, upgrade (4 modes) | 20 |
| `version` | list, get, update, status, download, diff | 6 |
| `version-file` | get, parser-processing, retrigger-parser, retry-processing | 4 |
| `metadata` | list, get, tags, tag, fields, field, bulk-add | 7 |
| `metadata template` | list, get, update, diff, lock, unlock, status | 7 |
| `metadata container` | list, get, create, update, clone, lock, unlock, status, version, restore, import, pool | 12 |
| `metadata export` | list, get, download, create | 4 |
| `parser-config` | list, get, available-types, create, update, delete | 6 |
| `export` | list, get, download, create | 4 |
| `storage` | list, get, create | 3 |
| `approval-queue` | list, get, approve | 3 |
| `system` | dashboard, settings, cms, cms-slugs, faq, search-schema, metadata-keys, metadata-choice-options | 8 |

## 3. MCP reference — existing building blocks (23 tools)

The MCP exposes each operation as one tool (internally bundling where needed):

`search_datatagger` · `list/get/create/update/delete_project` · `list/get/create/update/delete_folder` · `list/create/delete_dataset` · `publish_dataset` · `restore_dataset_version` · `compare_dataset_versions` · `download_version_file` · `upload_dataset_file` (TUS: init + PATCH + finalisation) · `set/get_folder_permissions` · `list_metadata` · `add_metadata_to_dataset`

The MCP README documents the **Folder/Draft upload** workflow (`create_dataset` → `upload_dataset_file`) — the canonical 2-tool chain the CLI should mirror as one command.

## 4. Bundling criteria

A chain is worth building if it satisfies at least one of:

- **(a) stateful** — poll / wait / verify / retry (upload → parser status → retry)
- **(b) safe** — dry-run, diff preview, explicit confirm, before/after verification (restore, permissions, approve)
- **(c) cross-resource** — one task spanning several resource types (project + folder + rights + schema)
- **(d) domain-real** — a task someone actually performs (new measurement data, campaign close-out, onboarding)

## 5. Proposed chains (consolidated)

### Wave 1 — highest value

#### 1. `dataset upload --wait-parser [--parser <type>]` — ingest with parser verification *(a, d)*
- Chain: *(optional)* `parser-config create` → TUS upload → resolve version-file id → **poll** `version-file parser-processing` (timeout) → on ERROR `retry-processing` (1×) → report FINISHED/ERROR
- Today: upload, then 3 manual status checks + retry by hand. Every upload ends in "waiting for the parser" — this is the single most common task.
- Building blocks: `upload_dataset_file` (MCP), `parser-processing`, `retry-processing`, `parser-config create` (CLI)

#### 2. `folder grant` / `folder revoke` — safe permission delta *(b, a)*
- Chain: `GET /folder-permission/?folder={id}` → diff (user present? role change?) → `PUT /folder/{id}/permissions/` → verify GET + before/after diff in output
- Today: `set-permissions` **replaces everything** — one wrong JSON wipes the access list. This is the most dangerous call in the workspace area.
- `--dry-run` supported. Idempotent (grant on existing user = role adjustment).

#### 3. `dataset restore-safe` — rollback with diff preview *(b, d)*
- Chain: `version list` → `version diff` (current vs target) → **show diff** → `--confirm` → `dataset restore` → `dataset status` verify
- Today: restore overwrites the current state blindly. The only destructive dataset op gets a preview + verification.

#### 4. `project member add` / `project member remove` — delta membership *(b, a, d)*
- Chain: `user list --search <kennung>` → `project-membership` list (already member? creator quirk → avoid "must make a unique set" 400) → `membership-create` (with roles) → verify; remove = DELETE + confirm
- Today: `members-set` replaces the whole team; onboarding/offboarding is a real weekly task.

#### 5. `metadata apply-template <dataset> <template>` — template onto dataset *(c)*
- Chain: `container pool <dataset>` → `template get` → `dataset add-metadata` (MCP `add_metadata_to_dataset`) → `metadata list/get` verify → optional `dataset publish`
- Today: copy-paste field values out of the pool output into JSON by hand.

#### 6. `approval-queue process` — safe approval workflow *(b)*
- Chain: `approval-queue list` (pending only) → `get <id>` (show details) → `--dry-run` → `--confirm` → `approve` → `get` (status after)
- Today: `approve` is a **GET** on `.../approve/` that performs a real action — one typo approves the wrong dataset.

#### 7. `dataset create-upload <folder> <name> <file>` — new dataset with file (ingest) *(a, c)*
- Chain: `dataset create` (with `--folder`) → TUS upload → resolve version-file id → **poll** `version-file parser-processing` (timeout) → report FINISHED/ERROR
- Use case: "I have measurement data for a new dataset" — the MCP README "Folder upload" workflow as one command. Ends **before** `publish` (deliberate post-QA decision, `dataset publish` stays separate) and **before** metadata (`apply-template` / `add-metadata` is its own task).
- Building blocks: `create_dataset` + `upload_dataset_file` (MCP), `parser-processing` (CLI)

### Wave 2 — solid follow-ups

#### 9. `export run` — export job to file *(a)*
- Chain: `export create <type> <uuids>` → poll `export get` → `export download <dest> --overwrite` → local file check. Same semantics for `metadata export` (template schemas).

#### 10. `metadata template release` — template freeze with before/after *(b)*
- Chain: `template diff` (show) → `--confirm` → `template lock` → `template status` verify → optional `metadata export create`+`download` as release evidence.

#### 11. `dataset upgrade-run` — metadata upgrade with conflict handling *(a, d)*
- Chain: `upgrade --submit` → poll `--status` → on conflict: `--payload` + `--resolve-conflict --json` → resubmit → final status. Bundles the 4 existing modes of `dataset upgrade` into one guided flow.

#### 12. `dataset bulk-publish --wait` — campaign close-out with report *(a, c)*
- Chain: `bulk-publish <folder> <ids>` → per-dataset `status` poll → report: X PUBLISHED, Y ERROR (with IDs). Same pattern for `bulk-upgrade --wait` and `bulk-delete` (with `dataset list` preview).

#### 13. `project overview <id>` — one-shot project view *(c, d)*
- Chain: `project get` → `project folders` → `project-membership` (server-side filter) → `project status` → optional `metadata-templates`. Replaces the client-side filtering of `project members`.

#### 14. `project finalize` / `folder freeze` — close-out with verification *(a, b)*
- Chain: `status` → `lock` → `status` (verify `locked=true`); `project finalize` cascades to all folders; optional `dataset list --folder` warns about unfinished drafts.

#### 15. Smaller chains
- `dataset edit-safe` — lock → change → status → unlock (try/finally) *(b)*
- `version fetch <dataset> --dest` — resolve latest/published version → download → verify size *(c, d)*
- `metadata container provision` — clone schema for new project + pool verify *(c, b)*
- `metadata container migrate` — export → poll → download → import on target instance → pool verify *(a, c)*
- `system template-search-preview` — metadata-keys + choice-options + search-schema for one template *(d)*
- `storage register` — list → create → get verify *(b, admin)*
- Safe delete wizard for project/folder — content preview → confirm → delete → verify *(b, low prio)*

## 6. Building blocks without a standalone use case

These are primitives, not tasks — they stay as commands but are not bundling targets:

| Command | Reason |
|---|---|
| `dataset create` | an empty draft is worthless — building block |
| `dataset status`, `version status`, `version-file parser-processing`, `version-file retry-processing` | poll primitives |
| `project/folder metadata-templates`, `template-container-pool` | info snippets |
| `version update` | emergency status surgery — candidate to hide behind `--force` |
| `dataset file-upload` | legacy multipart; TUS is the web-UI standard — deprecation candidate |
| `storage *`, `system *` | admin diagnostics |

## 7. Explicitly out of scope

- `new-dataset` all-in-one composite — rejected (too broad; nobody runs the full 6-step chain in one go)
- `workspace init` (project + folder + rights + team + schema in one call) — rejected; these are separate tasks, each with its own chain (`folder grant/revoke`, `project member add/remove`, `metadata container provision`)
- `dataset publish-new` (create → upload → metadata → publish in one go) — rejected; publishing is a deliberate post-QA decision, the ingest chain (`create-upload`) ends before `publish`
- `raw` — stays as the escape hatch for anything without a dedicated command
- `auth` — client-side token mechanics, no bundling value
