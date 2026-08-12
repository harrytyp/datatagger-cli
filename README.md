# datatagger-cli

Cross-platform CLI for the **TUM DataTagger API** — full API coverage with
high-level commands. Runs anywhere Python 3.11+ runs (Windows / macOS / Linux).
No runtime dependency on any MCP server: authentication and HTTP are
implemented directly (Bearer token from `FDM_TOKEN`), and the command structure
is inspired by the `datatagger-mcp` library's tool design for a simple user
experience.

## Features

- **Full API coverage** — every DataTagger endpoint is reachable: projects,
  folders, datasets, versions, version files, metadata (tags/fields/templates/
  containers/exports), parser configurations, data export jobs, storage,
  approval queue, users, auth, dashboard/settings/CMS/FAQ.
- **High-level UX** — commands are grouped and concise; the HTTP layer
  (`client.py`) centralizes auth, error formatting and file transfers (TUS
  uploads, streaming downloads).
- **`raw` escape hatch** — any API call, even for endpoints without a dedicated
  command: `datatagger raw GET /api/v1/settings/ --query limit=1`.
- **Machine-readable output** — every command prints valid JSON (or a clear
  error message), ready for scripting and CI.
- **JSON arguments** — inline JSON or `@path/to/file.json` for complex payloads
  (`--metadata`, `--users`, `--data`, …).
- **Safety guards** — destructive operations require `--confirm`.

## Installation

```bash
git clone https://github.com/harrytyp/datatagger-cli.git
cd datatagger-cli
uv sync            # creates .venv, installs dependencies
uv run datatagger --help
```

Or install into your environment:

```bash
uv tool install .  # or: pip install .
```

## Authentication

```bash
export FDM_TOKEN="your-token"        # DataTagger → Settings → API token
export FDM_BASE_URL="https://datatagger.ub.tum.de"   # optional, this is the default
```

The token is only read from the environment — never stored by the CLI.

## Quickstart

```bash
# Search
datatagger search "temperature" --limit 10

# Create project + folder + dataset
datatagger project create "My Project" --description '{"en": "Demo"}'
datatagger folder create <project-id> "measurements"
datatagger dataset create "measurement-1" --folder <folder-id>

# Upload (TUS) and finalize
datatagger dataset upload <dataset-id> ./measurement.csv
datatagger dataset publish <dataset-id>

# Versions: diff, restore
datatagger version diff <v2-id> <v1-id>
datatagger dataset restore <dataset-id> <v1-id>

# Folder permissions
datatagger folder set-permissions <folder-id> \
  '[{"email": "person@tum.de", "can_edit": true, "is_folder_admin": false, "is_metadata_template_admin": false}]'
```

> Note: `description` is a **JSON object** in the current API (e.g. `{"en": "…"}`).
> Plain text is wrapped automatically to `{"en": …}` by the CLI — a raw string
> causes a server-side 500 on create.

## Command overview

| Group | Commands |
|---|---|
| `search` | global search |
| `auth` | `login`, `verify`, `refresh`, `jwt-cookie` |
| `project` | `list get create update delete folders members members-set membership-list membership-create membership-update membership-delete lock unlock status metadata-templates template-container-pool` |
| `folder` | `list get create update delete lock unlock status permissions set-permissions metadata-templates template-container-pool` |
| `dataset` | `list get create update delete publish restore compare upload file-upload add-metadata new-version reference lock unlock status bulk-delete bulk-publish bulk-upgrade upgrade` |
| `version` | `list get update status download diff` |
| `version-file` | `get parser-processing retrigger-parser retry-processing` |
| `metadata` | `list get tags tag fields field bulk-add`; `template` (`list get update diff lock unlock status`); `container` (`list get create update clone lock unlock status version restore import pool`); `export` (`list get download create`) |
| `parser-config` | `list get create update delete available-types` |
| `export` | data export jobs: `list get download create` |
| `storage` | `list get create` |
| `approval-queue` | `list get approve` |
| `user` | `list get me me-update` |
| `system` | `dashboard settings cms cms-slugs faq search-schema metadata-keys metadata-choice-options` |
| `raw` | arbitrary API call (escape hatch) |

➡️ **Complete reference for all 118 commands** (arguments, options, defaults):
[docs/COMMANDS.md](docs/COMMANDS.md)

## Tests

The live test suite calls **every** CLI function against the real API:

```bash
export FDM_TOKEN="..."   # live token
uv run python tests/live_test.py
```

It creates its own resources with a `dtcli-test-<timestamp>` prefix and cleans up
afterwards. Expected API/role limitations (admin-only endpoints, missing
credentials, …) are reported as `DOC` instead of `FAIL`.

## Known issues

**CLI:** none currently known — the live test suite (tests/live_test.py) runs
every command against the real API with 0 failures (see [Tests](#tests)).

**Upstream API notes** (behavior of the DataTagger API itself; the CLI handles
or surfaces these cleanly):

- `description` (project/folder) is a **JSON object** in the current API
  (e.g. `{"en": "…"}`). The CLI wraps plain text into `{"en": …}` automatically;
  a raw string causes a server-side 500 on create.
- `folder set-permissions`: `folder_users` items expect **`email`** (not
  `member`).
- `publish`/`bulk-publish` require a publish role (403 for normal accounts);
  TUS uploads already finalize datasets.
- `dataset reference`, `storage create`, `approval-queue approve`,
  `auth login`/`refresh` need storage paths / admin rights / real credentials —
  marked `DOC` in the test suite.

## License

MIT — see [LICENSE](LICENSE).
