# datatagger-cli

Cross-platform CLI for the **TUM DataTagger API** - full API coverage with
high-level commands. Runs anywhere Python 3.11+ runs (Windows / macOS / Linux).
No runtime dependency on any MCP server: authentication and HTTP are
implemented directly (Bearer token from `FDM_TOKEN`), and the command structure
is inspired by the `datatagger-mcp` library's tool design for a simple user
experience.

## Features

- **Full API coverage** - every DataTagger endpoint is reachable: projects,
  folders, datasets, versions, version files, metadata (tags/fields/templates/
  containers/exports), parser configurations, data export jobs, storage,
  approval queue, users, auth, dashboard/settings/CMS/FAQ.
- **High-level UX** - commands are grouped and concise; the HTTP layer
  (`client.py`) centralizes auth, error formatting and file transfers (TUS
  uploads, streaming downloads).
- **Clear split** - every raw API wrapper lives under `datatagger api …`
  (e.g. `datatagger api project create`, one command = one API call);
  high-level task commands sit on the top level
  (`datatagger search`, `datatagger new-dataset`, …).
- **`raw` escape hatch** - any API call, even for endpoints without a dedicated
  command: `datatagger api raw GET /api/v1/settings/ --query limit=1`.
- **Machine-readable output** - every command prints valid JSON (or a clear
  error message), ready for scripting and CI.
- **JSON arguments** - inline JSON or `@path/to/file.json` for complex payloads
  (`--metadata`, `--users`, `--data`, …).
- **Safety guards** - destructive operations require `--confirm`.

## Installation

### Option A: pip (recommended for most users)

Requires Python 3.11+:

```bash
pip install git+https://github.com/harrytyp/datatagger-cli.git
```

This installs the `datatagger` entry point into your Python environment
(venv, conda, or system). Afterwards:

```bash
datatagger --help
```

To upgrade later:

```bash
pip install --upgrade git+https://github.com/harrytyp/datatagger-cli.git
```

### Option B: uv (fast, isolated)

```bash
git clone https://github.com/harrytyp/datatagger-cli.git
cd datatagger-cli
uv sync            # creates .venv, installs dependencies
uv run datatagger --help
```

Or install globally with uv:

```bash
uv tool install .
```

### Option C: from a local checkout (pip editable)

```bash
git clone https://github.com/harrytyp/datatagger-cli.git
cd datatagger-cli
pip install -e .
```

## Authentication

The CLI authenticates with the raw token from the DataTagger web app (no extra
API token needed). Get it:

1. Open https://datatagger.ub.tum.de and log in
2. Open DevTools (**F12**) → **Storage → Cookies → https://datatagger.ub.tum.de**
3. Copy the value of the **`token`** cookie
4. Export it:

```bash
export FDM_TOKEN="<cookie-token-value>"
export FDM_BASE_URL="https://datatagger.ub.tum.de"   # optional, this is the default
```

The CLI sends it as `Authorization: Bearer <token>`. It is only read from the
environment - never stored by the CLI.

## Quickstart

```bash
# Search
datatagger search "temperature" --limit 10

# One-command workflow: creates project + folder + dataset (+ upload + metadata + publish)
datatagger new-dataset "measurement-1" \
  --project-name "My Project" --folder-name "measurements" \
  --file ./measurement.csv --publish

# ...or step by step (equivalent):
datatagger api project create "My Project" --description '{"en": "Demo"}'
datatagger api folder create <project-id> "measurements"
datatagger api dataset create "measurement-1" --folder <folder-id>
datatagger api dataset upload <dataset-id> ./measurement.csv
datatagger api dataset publish <dataset-id>

# Versions: diff, restore
datatagger api version diff <v2-id> <v1-id>
datatagger api dataset restore <dataset-id> <v1-id>

# Folder permissions
datatagger api folder set-permissions <folder-id> \
  '[{"email": "person@tum.de", "can_edit": true, "is_folder_admin": false, "is_metadata_template_admin": false}]'
```

> Raw API wrappers are grouped under `datatagger api …`; task-level commands
> (search, workflows) live directly under `datatagger`.

> Note: `description` is a **JSON object** in the current API (e.g. `{"en": "…"}`).
> Plain text is wrapped automatically to `{"en": …}` by the CLI - a raw string
> causes a server-side 500 on create.

## Command overview

| Group | Commands |
|---|---|
| `search` | global search |
| `new-dataset` | one-command workflow: project -> folder -> dataset -> file -> metadata -> publish |
| `api` | raw API wrappers - one command = one API call |
| `api auth` | `login`, `verify`, `refresh`, `jwt-cookie` |
| `api project` | `list get create update delete folders members members-set membership-list membership-create membership-update membership-delete lock unlock status metadata-templates template-container-pool` |
| `api folder` | `list get create update delete lock unlock status permissions set-permissions metadata-templates template-container-pool` |
| `api dataset` | `list get create update delete publish restore compare upload file-upload add-metadata new-version reference lock unlock status bulk-delete bulk-publish bulk-upgrade upgrade` |
| `api version` | `list get update status download diff` |
| `api version-file` | `get parser-processing retrigger-parser retry-processing` |
| `api metadata` | `list get tags tag fields field bulk-add`; `template` (`list get update diff lock unlock status`); `container` (`list get create update clone lock unlock status version restore import pool`); `export` (`list get download create`) |
| `api parser-config` | `list get create update delete available-types` |
| `api export` | data export jobs: `list get download create` |
| `api storage` | `list get create` |
| `api approval-queue` | `list get approve` |
| `api user` | `list get me me-update` |
| `api system` | `dashboard settings cms cms-slugs faq search-schema metadata-keys metadata-choice-options` |
| `api raw` | arbitrary API call (escape hatch) |

➡️ **Complete reference for all commands** (arguments, options, defaults):
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

**CLI:** none currently known - the live test suite (tests/live_test.py) runs
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
  `auth login`/`refresh` need storage paths / admin rights / real credentials -
  marked `DOC` in the test suite.

## License

MIT - see [LICENSE](LICENSE).
