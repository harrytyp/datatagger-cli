#!/usr/bin/env python
"""Live-Tests: führt JEDE datatagger-CLI-Funktion gegen die echte API aus.

Voraussetzungen:
  - FDM_TOKEN (Bearer-Token) als Umgebungsvariable
  - CLI installiert: .venv/Scripts/datatagger.exe (oder DT_CLI=<pfad>)

Ablauf: legt Ressourcen mit Präfix 'dtcli-test-<ts>' an, testet alle
Kommandos darauf, räumt am Ende bestmöglich auf (nur eigene Ressourcen).
Erwartete API-Fehler (z. B. 405 beim MCP-compare-Bug, 403 für Admin-Only)
werden als 'DOC' (dokumentiert) gewertet, nicht als Fehlschlag.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import uuid

BIN = os.environ.get("DT_CLI", os.path.join(os.path.dirname(__file__), "..", ".venv", "Scripts", "datatagger.exe"))
if not os.environ.get("FDM_TOKEN"):
    print("FEHLER: FDM_TOKEN Umgebungsvariable fehlt.", file=sys.stderr)
    sys.exit(3)

API_GROUPS = {"auth", "project", "folder", "dataset", "version", "version-file",
              "metadata", "parser-config", "export", "storage", "approval-queue",
              "user", "system", "raw"}

TS = time.strftime("%Y%m%d-%H%M%S")
PREFIX = f"dtcli-test-{TS}"
results: list[dict] = []


def run(args, timeout=150):
    """CLI-Aufruf; liefert (returncode, stdout, stderr). None-Argumente werden zu '' (kein Crash)."""
    time.sleep(0.1)  # dezente Drossel gegen API-Rate-Limits
    args = ["" if a is None else str(a) for a in args]
    if args and args[0] in API_GROUPS:
        args = ["api"] + args
    try:
        p = subprocess.run([BIN, *args], capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -99, "", f"TIMEOUT nach {timeout}s"


def parse_json(text: str):
    try:
        return json.loads(text.strip())
    except Exception:
        return None


def first_id(data, keys=("id", "pk")):
    """Erste ID aus dict oder Ergebnisliste."""
    if isinstance(data, dict):
        for k in keys:
            if data.get(k):
                return data[k]
        for v in data.values():
            if isinstance(v, dict):
                r = first_id(v, keys)
                if r:
                    return r
        return None
    if isinstance(data, list):
        for item in data:
            r = first_id(item, keys)
            if r:
                return r
    return None


def T(name, args, mode="json", expect_in=None, expect_exit=0, timeout=150):
    """Testfall ausführen und registrieren.

    mode: 'json' (exit 0 + parsebares JSON), 'any' (exit 0, irgendeine Ausgabe),
          'doc' (dokumentierter API-Fehler: exit 0, 'API Error' in Ausgabe),
          'exit2' (CLI bricht ab, exit 2).
    """
    rc, out, err = run(args, timeout)
    status = "PASS"
    note = ""
    if mode == "json":
        data = parse_json(out)
        if rc != 0 or data is None:
            status = "FAIL"
            note = f"rc={rc}, kein JSON: {repr(out[:140])}"
    elif mode == "any":
        if rc != 0 or not (out.strip() or err.strip()):
            status = "FAIL"
            note = f"rc={rc}, keine Ausgabe"
    elif mode == "doc":
        if rc != 0 or ("API Error" not in out and "Error" not in out):
            status = "FAIL"
            note = f"rc={rc}, erwarteter API-Fehler fehlt"
        else:
            status = "DOC"
    elif mode == "exit2":
        if rc != 2:
            status = "FAIL"
            note = f"rc={rc} (erwartet 2)"
    if expect_in and expect_in not in out:
        status = "FAIL"
        note = f"fehlt in Ausgabe: {expect_in}"
    evidence = (out or err).strip().splitlines()
    ev = evidence[-1][:160] if evidence else ""
    results.append({"name": name, "status": status, "note": note,
                    "ev": ev, "rc": rc, "args": " ".join(args)})
    return rc, out, err


def summary():
    passed = sum(1 for r in results if r["status"] == "PASS")
    doc = sum(1 for r in results if r["status"] == "DOC")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    print("\n" + "=" * 100)
    print(f"ERGEBNIS: {passed} PASS | {doc} DOC (erwartete API-Einschränkungen) | {failed} FAIL | {skipped} SKIP | gesamt {len(results)}")
    print("=" * 100)
    for r in results:
        mark = {"PASS": "  ✅", "DOC": "  🟡", "FAIL": "  ❌", "SKIP": "  ⏭️ "}[r["status"]]
        print(f"{mark} {r['name']:<52} {r['note']:<42} {r['ev']}")
    print("=" * 100)


def main():
    print(f"### Live-Test-Suite  ({BIN})  Präfix: {PREFIX}\n")

    # ---------- 0) Smoke-Tests: --help für App + ALLE Gruppen/Kommandos ----------
    rc, out, err = run(["--help"])
    T("help (App)", ["--help"], mode="any")
    groups = ["auth", "project", "folder", "dataset", "version", "version-file",
              "metadata", "parser-config", "export", "storage", "approval-queue",
              "user", "system"]
    for g in groups:
        T(f"help {g}", [g, "--help"], mode="any")
        rc, out, err = run([g, "--help"])
        cmds = []
        in_cmds = False
        for line in (out + err).splitlines():
            if "Commands" in line:
                in_cmds = True
                continue
            if not in_cmds:
                continue
            # Panel-Ränder beidseitig entfernen, Name/Description an 2+ Spaces trennen
            s = line.strip().strip("│┃|")
            if not s or s.startswith(("Usage", "Options", "┌", "└", "╭", "╰", "─")):
                continue
            parts = [p for p in __import__("re").split(r"\s{2,}", s) if p]
            if len(parts) < 2:
                continue
            c = parts[0].strip()
            if c and not c.startswith("--") and c not in cmds:
                cmds.append(c)
        for c in cmds:
            T(f"help {g} {c}", [g, c, "--help"], mode="any")

    # ---------- 1) Auth / User ----------
    T("auth verify (Token)", ["auth", "verify"], mode="any")
    rc, out, _ = T("user me", ["user", "me"])
    me = parse_json(out) or {}
    uid = me.get("pk") or me.get("id")
    print(f"   -> User-ID: {uid}")

    # ---------- 2) Projekt ----------
    proj_name = f"{PREFIX}-proj"
    rc, out, _ = T("project create", ["project", "create", proj_name, "--description", "CLI-Testprojekt"])
    proj_id = first_id(parse_json(out))
    print(f"   -> Projekt: {proj_id}")
    T("project get", ["project", "get", proj_id])
    T("project list", ["project", "list", "--search", PREFIX])
    T("project update", ["project", "update", proj_id, "--name", f"{proj_name}-renamed"])
    T("project lock", ["project", "lock", proj_id])
    T("project status", ["project", "status", proj_id])
    T("project unlock", ["project", "unlock", proj_id])
    T("project folders", ["project", "folders", proj_id])
    T("project metadata-templates", ["project", "metadata-templates", proj_id])
    T("project template-container-pool", ["project", "template-container-pool", proj_id])
    T("project members", ["project", "members", proj_id])
    T("project membership-list", ["project", "membership-list", "--limit", "5"])
    # membership-create auf frischem Projekt mit einem anderen User (Ersteller ist automatisch Mitglied)
    rc, out, _ = T("project create (f. Membership)", ["project", "create", f"{PREFIX}-memproj"])
    memproj_id = first_id(parse_json(out))
    other_user = None
    rc2, out2, _ = run(["user", "list", "--limit", "50"])
    udata = parse_json(out2) or {}
    for u in udata.get("results", []) if isinstance(udata, dict) else []:
        if u.get("pk") != uid:
            other_user = u.get("pk")
            break
    if memproj_id and other_user:
        rc, out, _ = T("project membership-create", ["project", "membership-create", memproj_id, str(other_user)])
        mship_id = first_id(parse_json(out))
        if mship_id:
            T("project membership-update", ["project", "membership-update", mship_id, "--can-create-folders", "true"])
            T("project membership-delete", ["project", "membership-delete", mship_id, "--confirm"], mode="any")
    else:
        results.append({"name": "project membership-create", "status": "DOC",
                        "note": "kein zweiter User im Test-Account sichtbar",
                        "ev": "", "rc": 0, "args": ""})
        results.append({"name": "project membership-update", "status": "SKIP", "note": "kein Membership erstellt",
                        "ev": "", "rc": 0, "args": ""})
    T("project delete ohne --confirm (Guard)", ["project", "delete", proj_id], mode="exit2")

    # ---------- 3) Ordner ----------
    rc, out, _ = T("folder create", ["folder", "create", proj_id, f"{PREFIX}-folder", "--description", "CLI-Testordner"])
    folder_id = first_id(parse_json(out))
    print(f"   -> Ordner: {folder_id}")
    T("folder get", ["folder", "get", folder_id])
    T("folder list", ["folder", "list", "--project", proj_id])
    T("folder update", ["folder", "update", folder_id, "--description", "CLI-Testordner v2"])
    T("folder lock", ["folder", "lock", folder_id])
    T("folder status", ["folder", "status", folder_id])
    T("folder unlock", ["folder", "unlock", folder_id])
    T("folder permissions", ["folder", "permissions", folder_id])
    my_email = (me or {}).get("email")
    if my_email:
        T("folder set-permissions (email-Format)", ["folder", "set-permissions", folder_id,
                                                     json.dumps([{"email": my_email, "is_folder_admin": False,
                                                                  "is_metadata_template_admin": False, "can_edit": True}])])
        T("folder set-permissions (Reset)", ["folder", "set-permissions", folder_id, "[]"], mode="any")
    T("folder metadata-templates", ["folder", "metadata-templates", folder_id])
    T("folder template-container-pool", ["folder", "template-container-pool", folder_id])

    # ---------- 4) Dataset / Versionen / Upload / Download ----------
    tmp = tempfile.mkdtemp(prefix="dtcli-")
    sample = os.path.join(tmp, "sample.csv")
    with open(sample, "w", encoding="utf-8") as f:
        f.write("col1,col2\n1,a\n2,b\n")
    sample2 = os.path.join(tmp, "sample2.txt")
    with open(sample2, "w", encoding="utf-8") as f:
        f.write("second file\n")

    rc, out, _ = T("dataset create (im Ordner)", ["dataset", "create", f"{PREFIX}-ds", "--folder", folder_id])
    ds_id = first_id(parse_json(out))
    print(f"   -> Dataset: {ds_id}")
    rc, out, _ = T("dataset create (Draft)", ["dataset", "create", f"{PREFIX}-draft"])
    draft_id = first_id(parse_json(out))
    rc, out, _ = T("dataset create (Draft2)", ["dataset", "create", f"{PREFIX}-draft2"])
    draft2_id = first_id(parse_json(out))
    T("dataset get", ["dataset", "get", ds_id])
    T("dataset list", ["dataset", "list", "--folder", folder_id])
    T("dataset update", ["dataset", "update", ds_id, "--name", f"{PREFIX}-ds-renamed"])
    T("dataset upload (TUS)", ["dataset", "upload", ds_id, sample], mode="any")
    # add-metadata braucht eine existierende Version → NACH dem Upload
    T("dataset add-metadata", ["dataset", "add-metadata", ds_id,
                               json.dumps([{"field": {"key": "cli-test-key", "field_type": "TEXT"}, "value": "cli-test-value"}])])
    T("dataset file-upload (legacy)", ["dataset", "file-upload", ds_id, sample2], mode="any")

    rc, out, _ = T("version list", ["version", "list", "--dataset", ds_id])
    vdata = parse_json(out) or {}
    versions = vdata.get("results", []) if isinstance(vdata, dict) else vdata
    # v1 = Version MIT Datei, v2 = beliebige andere
    v1 = vfile = None
    for v in versions:
        vf = v.get("version_file")
        fid = vf.get("pk") if isinstance(vf, dict) else vf
        if fid and not v1:
            v1 = v.get("pk")
            vfile = fid
    v2 = None
    for v in versions:
        if v.get("pk") != v1:
            v2 = v.get("pk")
            break
    print(f"   -> Version 1: {v1}, File: {vfile}, Version 2: {v2}")
    if v1:
        T("version get", ["version", "get", v1])
        T("version update", ["version", "update", v1, "--name", f"{PREFIX}-v1"])
        T("version status", ["version", "status", v1])
        dest1 = os.path.join(tmp, "downloaded.csv")
        T("version download", ["version", "download", v1, dest1, "--overwrite"], mode="any")
        if os.path.exists(dest1):
            print(f"   -> Download verifiziert: {os.path.getsize(dest1)} Bytes")
        else:
            results.append({"name": "version download (Datei)", "status": "FAIL", "note": "Datei fehlt",
                            "ev": dest1, "rc": 0, "args": ""})
    rc, out, _ = T("dataset new-version", ["dataset", "new-version", ds_id, "--name", f"{PREFIX}-v2"])
    rc, out, _ = T("version list (2. Version)", ["version", "list", "--dataset", ds_id])
    vdata = parse_json(out) or {}
    versions = vdata.get("results", []) if isinstance(vdata, dict) else vdata
    if not v1:
        v1 = first_id(versions)
    for v in versions:
        if v.get("pk") != v1:
            v2 = v.get("pk")
            break
    print(f"   -> Version 2: {v2}")
    if v1 and v2:
        T("version diff (GET, aktueller Endpunkt)", ["version", "diff", v2, v1])
        T("dataset compare (GET-Endpunkt)", ["dataset", "compare", v2, v1])
        T("dataset restore", ["dataset", "restore", ds_id, v1])
    T("dataset publish (403 ohne Publish-Rolle erwartet)", ["dataset", "publish", ds_id], mode="any")
    T("dataset status", ["dataset", "status", ds_id])
    T("dataset lock", ["dataset", "lock", ds_id])
    T("dataset unlock", ["dataset", "unlock", ds_id])
    T("dataset reference (kein Storage-Pfad)", ["dataset", "reference", ds_id, "/nonexistent/does-not-exist.csv"], mode="doc")
    T("dataset upgrade --status", ["dataset", "upgrade", ds_id, "--status"], mode="any")
    T("dataset upgrade --payload", ["dataset", "upgrade", ds_id, "--payload"], mode="any")
    T("dataset upgrade --submit", ["dataset", "upgrade", ds_id, "--submit"], mode="any")
    T("dataset bulk-upgrade", ["dataset", "bulk-upgrade", ds_id], mode="any")

    if vfile:
        T("version-file get", ["version-file", "get", vfile])
        T("version-file parser-processing", ["version-file", "parser-processing", vfile], mode="any")
        T("version-file retrigger-parser", ["version-file", "retrigger-parser", vfile], mode="any")
        T("version-file retry-processing", ["version-file", "retry-processing", vfile], mode="any")

    # ---------- 5) Bulk-Operationen ----------
    T("dataset delete (Draft, --confirm)", ["dataset", "delete", draft_id, "--confirm"], mode="any")
    T("dataset bulk-publish (403 ohne Rolle erwartet)", ["dataset", "bulk-publish", folder_id, draft2_id], mode="any")
    T("dataset bulk-delete (Draft2)", ["dataset", "bulk-delete", draft2_id, "--confirm"], mode="any")
    T("dataset delete ohne --confirm (Guard)", ["dataset", "delete", ds_id], mode="exit2")

    # ---------- 6) Metadata ----------
    T("metadata list", ["metadata", "list", "--limit", "5"])
    rc, out, _ = T("metadata tags", ["metadata", "tags", "--limit", "5"])
    tag_id = first_id(parse_json(out))
    if tag_id:
        T("metadata tag", ["metadata", "tag", tag_id])
    rc, out, _ = T("metadata fields", ["metadata", "fields", "--limit", "5"])
    field_id = first_id(parse_json(out))
    if field_id:
        T("metadata field", ["metadata", "field", field_id])
    rc, out, _ = T("metadata list (id aus Liste)", ["metadata", "list", "--limit", "5"])
    mid = first_id(parse_json(out))
    if mid:
        T("metadata get", ["metadata", "get", mid])
    rc, out, _ = T("dataset create (Draft3)", ["dataset", "create", f"{PREFIX}-draft3"])
    draft3_id = first_id(parse_json(out))
    T("metadata bulk-add", ["metadata", "bulk-add", draft3_id,
                            json.dumps([{"field": {"key": "cli-bulk-key", "field_type": "TEXT"}, "value": "bulk"}])], mode="any")

    # ---------- 7) Metadata-Template-Container / Templates ----------
    rc, out, _ = T("metadata container create", ["metadata", "container", "create", f"{PREFIX}-container",
                                                 "--content-type", "projects.project", "--object-id", proj_id])
    cont_id = first_id(parse_json(out))
    t1 = None
    if cont_id:
        print(f"   -> Container: {cont_id}")
        T("metadata container get", ["metadata", "container", "get", cont_id])
        rc2, out2, _ = run(["metadata", "container", "get", cont_id])
        cdata = parse_json(out2) or {}
        t1 = cdata.get("metadata_template") or (cdata.get("current_template") if isinstance(cdata.get("current_template"), str) else None)
        if not t1 and isinstance(cdata.get("metadata_templates"), list) and cdata["metadata_templates"]:
            t1 = cdata["metadata_templates"][0] if isinstance(cdata["metadata_templates"][0], str) else cdata["metadata_templates"][0].get("pk")
        T("metadata container update", ["metadata", "container", "update", cont_id, "--name", f"{PREFIX}-container-v2"])
        T("metadata container lock", ["metadata", "container", "lock", cont_id])
        T("metadata container status", ["metadata", "container", "status", cont_id])
        T("metadata container unlock", ["metadata", "container", "unlock", cont_id])
        rc, out, _ = T("metadata container clone", ["metadata", "container", "clone", cont_id])
        cont2_id = first_id(parse_json(out))
        T("metadata container version (neue Template-Version)", ["metadata", "container", "version", cont_id, "--name", "v2"], mode="any")
        rc2, out2, _ = run(["metadata", "container", "get", cont_id])
        cdata = parse_json(out2) or {}
        t2 = cdata.get("metadata_template") or (cdata.get("current_template") if isinstance(cdata.get("current_template"), str) else None)
        print(f"   -> Template v1: {t1}, nach Version: {t2}")
        if t1 and t2 and t1 != t2:
            T("metadata template diff", ["metadata", "template", "diff", t1, "--compare", t2])
        T("metadata container pool (project)", ["metadata", "container", "pool", "project", proj_id])
        if t1:
            T("metadata template get", ["metadata", "template", "get", t1])
            T("metadata template lock", ["metadata", "template", "lock", t1], mode="any")
            T("metadata template status", ["metadata", "template", "status", t1], mode="any")
            T("metadata template unlock", ["metadata", "template", "unlock", t1], mode="any")
            T("metadata template update", ["metadata", "template", "update", t1, "--name", f"{PREFIX}-tpl"], mode="any")
        T("metadata container restore", ["metadata", "container", "restore", cont_id, t1 or "00000000-0000-0000-0000-000000000000"], mode="any")
        rc, out, _ = T("metadata export create", ["metadata", "export", "create", cont_id], mode="any")
        texp_id = first_id(parse_json(out))
        if texp_id:
            T("metadata export get", ["metadata", "export", "get", texp_id])
            texp_dest = os.path.join(tmp, "template-export.json")
            T("metadata export download", ["metadata", "export", "download", texp_id, texp_dest, "--overwrite"], mode="any")
            if os.path.exists(texp_dest) and os.path.getsize(texp_dest) > 0:
                T("metadata container import (Export-Datei)", ["metadata", "container", "import", texp_dest], mode="any")
    T("metadata template list", ["metadata", "template", "list", "--limit", "5"])
    T("metadata container list", ["metadata", "container", "list", "--limit", "5"])
    T("metadata export list", ["metadata", "export", "list"])

    # ---------- 8) Parser-Config ----------
    T("parser-config list", ["parser-config", "list", "--limit", "5"])
    T("parser-config available-types", ["parser-config", "available-types"])
    rc, out, _ = T("parser-config create", ["parser-config", "create", proj_id, "projects.project", "CSV_VALUE",
                                            "--config", json.dumps([{"row": 0, "column": 0, "key": "cli-parser-key", "field_type": "TEXT"}])])
    pcfg_id = first_id(parse_json(out))
    if pcfg_id:
        T("parser-config get", ["parser-config", "get", pcfg_id])
        T("parser-config update", ["parser-config", "update", pcfg_id, "--disabled"])
        T("parser-config delete", ["parser-config", "delete", pcfg_id, "--confirm"], mode="any")
    else:
        T("parser-config get (keine ID)", ["parser-config", "get", "00000000-0000-0000-0000-000000000000"], mode="doc")

    # ---------- 9) Export-Jobs / Storage / Approval / User ----------
    rc, out, _ = T("export create (mit Datei-Export)", ["export", "create", "uploads.uploadsdataset", ds_id, "--include-file"])
    exp_id = first_id(parse_json(out))
    if exp_id:
        T("export get", ["export", "get", exp_id])
        exp_dest = os.path.join(tmp, "export.json")
        T("export download", ["export", "download", exp_id, exp_dest, "--overwrite"], mode="any")
    T("export list", ["export", "list"])
    T("storage list", ["storage", "list", "--limit", "5"])
    rc, out, _ = run(["storage", "list", "--limit", "5"])
    sdata = parse_json(out)
    st_id = first_id(sdata)
    if st_id:
        T("storage get", ["storage", "get", st_id])
    T("storage create (Admin-Only)", ["storage", "create", f"{PREFIX}-storage", "LOCAL", "/tmp/xxx"], mode="doc")
    T("approval-queue list", ["approval-queue", "list", "--limit", "5"])
    rc, out, _ = run(["approval-queue", "list", "--limit", "5"])
    adata = parse_json(out)
    ap_id = first_id(adata)
    if ap_id:
        T("approval-queue get", ["approval-queue", "get", ap_id])
    T("approval-queue approve (nur Pfad-Test)", ["approval-queue", "approve", "00000000-0000-0000-0000-000000000000"], mode="doc")
    T("user list", ["user", "list", "--limit", "5"])
    rc, out, _ = run(["user", "list", "--limit", "5"])
    udata = parse_json(out)
    first_user = first_id(udata)
    if first_user:
        T("user get", ["user", "get", first_user])
    T("user me-update (No-Op)", ["user", "me-update", "--settings", "{}"], mode="any")

    # ---------- 10) System / Raw / Auth-Rest ----------
    T("system dashboard", ["system", "dashboard"])
    T("system settings", ["system", "settings"])
    rc, out, _ = run(["system", "settings"])
    sdata = parse_json(out)
    keys = None
    if isinstance(sdata, dict):
        keys = list(sdata.keys()) or (list(sdata.get("results", {}).keys()) if isinstance(sdata.get("results"), dict) else None)
    elif isinstance(sdata, list) and sdata:
        keys = [sdata[0]]
    if keys:
        T("system settings <key>", ["system", "settings", str(keys[0])], mode="any")
    T("system cms", ["system", "cms"], mode="any")
    T("system cms-slugs", ["system", "cms-slugs"], mode="any")
    T("system faq", ["system", "faq"], mode="any")
    T("system search-schema", ["system", "search-schema"])
    if t1:
        T("system metadata-keys", ["system", "metadata-keys", "--template-id", t1], mode="any")
        T("system metadata-choice-options", ["system", "metadata-choice-options", "--template-id", t1], mode="any")
    else:
        T("system metadata-keys (ohne template)", ["system", "metadata-keys"], mode="doc")
        T("system metadata-choice-options (ohne template)", ["system", "metadata-choice-options"], mode="doc")
    T("raw GET", ["raw", "GET", "/api/v1/dashboard/"])
    T("raw GET mit Query", ["raw", "GET", "/api/v1/settings/", "--query", "limit=1"], mode="any")
    T("raw POST mit Body", ["raw", "POST", "/api/v1/search/global/", "--data",
                            json.dumps({"search_text": PREFIX, "limit": 5})])
    T("search", ["search", PREFIX, "--limit", "5"])
    T("auth login (keine Creds)", ["auth", "login", "nobody", "--password", "wrong"], mode="doc")
    T("auth refresh (ungültig)", ["auth", "refresh", "invalid-refresh-token"], mode="doc")
    T("auth jwt-cookie", ["auth", "jwt-cookie"], mode="any")

    # ---------- 11) Cleanup (best effort, nur eigene Ressourcen) ----------
    print("\n### Cleanup (best effort) …")
    targets = [
        ("dataset delete (Draft3)", ["dataset", "delete", draft3_id, "--confirm"], draft3_id),
        ("dataset delete (Haupt)", ["dataset", "delete", ds_id, "--confirm"], ds_id),
        ("folder delete", ["folder", "delete", folder_id, "--confirm"], folder_id),
        ("project delete (Membership)", ["project", "delete", memproj_id, "--confirm"], memproj_id),
        ("project delete", ["project", "delete", proj_id, "--confirm"], proj_id),
    ]
    for label, args, ident in targets:
        if ident:
            rc, out, err = run(args)
            print(f"   {label}: rc={rc} {err.strip()[:100] if rc else ''}")

    summary()


if __name__ == "__main__":
    main()
