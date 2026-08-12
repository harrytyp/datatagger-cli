"""Offline test for the new-dataset workflow via typer.testing.CliRunner.

Verifies the chain project -> folder -> dataset -> file -> metadata -> publish
with mocked API functions (no network).
"""
import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
import datatagger_cli.cli as cli

calls = []


async def fake_create_project(name):
    calls.append(f'create_project({name})')
    return {'id': 'PROJ-1', 'name': name}


async def fake_create_folder(project_id, name):
    calls.append(f'create_folder({project_id}, {name})')
    return {'id': 'FOLD-1'}


async def fake_create_dataset(name, folder_id=None):
    calls.append(f'create_dataset({name}, folder={folder_id})')
    return {'id': 'DATA-1'}


async def fake_upload(dataset_id, path):
    calls.append(f'upload({dataset_id}, {path})')
    return {'status': 'ok'}


async def fake_metadata(dataset_id, items):
    calls.append(f'metadata({dataset_id}, {len(items)} items)')
    return {'status': 'ok'}


async def fake_publish(dataset_id):
    calls.append(f'publish({dataset_id})')
    return {'status': 'published'}


def run_cmd(args):
    calls.clear()
    with patch.object(cli, 'create_project', fake_create_project), \
         patch.object(cli, 'create_folder', fake_create_folder), \
         patch.object(cli, 'create_dataset', fake_create_dataset), \
         patch.object(cli, 'upload_dataset_file', fake_upload), \
         patch.object(cli, 'add_metadata_to_dataset', fake_metadata), \
         patch.object(cli, 'publish_dataset', fake_publish), \
         patch.object(cli, 'parse_json_arg', lambda s: [s]):
        return CliRunner().invoke(cli.app, args)


def check(name, ok, detail=''):
    print(f'{"✅" if ok else "❌"} {name} {detail}')
    return ok


ok_all = True

# 1. Full chain
r = run_cmd(['new-dataset', 'exp1', '--project-name', 'P', '--folder-name', 'F',
             '--file', 'x.csv', '--metadata', '[...]', '--publish'])
ok_all &= check('1. Kompletter Workflow', r.exit_code == 0 and calls == [
    'create_project(P)', 'create_folder(PROJ-1, F)', 'create_dataset(exp1, folder=FOLD-1)',
    'upload(DATA-1, x.csv)', 'metadata(DATA-1, 1 items)', 'publish(DATA-1)'],
    f'exit={r.exit_code} calls={calls}')

# 2. Existing resources, minimal
r = run_cmd(['new-dataset', 'exp2', '--project', 'PROJ-X', '--folder', 'FOLD-X'])
ok_all &= check('2. Bestehende Ressourcen, minimal',
                r.exit_code == 0 and calls == ['create_dataset(exp2, folder=FOLD-X)'],
                f'calls={calls}')

# 3. Project exists, folder created
r = run_cmd(['new-dataset', 'exp3', '--project', 'PROJ-X', '--folder-name', 'F2'])
ok_all &= check('3. Projekt existiert, Folder neu',
                r.exit_code == 0 and calls == ['create_folder(PROJ-X, F2)',
                                                'create_dataset(exp3, folder=FOLD-1)'],
                f'calls={calls}')

# 4. Missing project -> exit code 2 with error message
r = run_cmd(['new-dataset', 'exp4'])
ok_all &= check('4. Fehlender Projekt-Parameter -> Exit 2',
                r.exit_code == 2 and '--project' in r.stdout,
                f'exit={r.exit_code}')

# 5. String response from API (robustness: create returns bare str)
async def fake_create_project_str(name):
    calls.append(f'create_project({name})')
    return 'PROJ-STR-1'
with patch.object(cli, 'create_project', fake_create_project_str), \
     patch.object(cli, 'create_folder', fake_create_folder), \
     patch.object(cli, 'create_dataset', fake_create_dataset), \
     patch.object(cli, 'upload_dataset_file', fake_upload), \
     patch.object(cli, 'out', lambda r: None):
    calls.clear()
    r = CliRunner().invoke(cli.app, ['new-dataset', 'exp5', '--project-name', 'P'])
    ok_all &= check('5. String-Antwort (dict ODER str)',
                    r.exit_code == 0 and calls == ['create_project(P)',
                                                    'create_dataset(exp5, folder=None)'],
                    f'exit={r.exit_code} calls={calls}')

print('\n' + ('ALLE WORKFLOW-TESTS BESTANDEN' if ok_all else 'FEHLER GEFUNDEN'))
sys.exit(0 if ok_all else 1)
