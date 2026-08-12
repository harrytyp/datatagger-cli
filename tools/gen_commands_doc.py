#!/usr/bin/env python
"""Generiert docs/COMMANDS.md — vollständige Befehlsreferenz aus den Typer-Signaturen."""
import os, sys, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from typer.main import get_command
import datatagger_cli.cli as cli

root = get_command(cli.app)
lines = []
lines.append("# Command Reference\n")
lines.append("Complete reference for every `datatagger` command. All commands require ")
lines.append("`FDM_TOKEN` (the `token` cookie from datatagger.ub.tum.de, sent as Bearer) ")
lines.append("and optionally `FDM_BASE_URL` as environment variables.\n")
lines.append("JSON arguments accept inline JSON or `@path/to/file.json`.\n")
lines.append("Destructive operations require `--confirm`.\n")

def fmt_default(param):
    d = param.default
    if d in (None, "", False):
        return ""
    if d is True:
        return " (default)"
    return f" (default: {d})"

def param_line(p, indent="  "):
    if p.is_flag:
        names = " / ".join(p.opts)
        return f"{indent}- `{names}` — flag{fmt_default(p)} {p.help or ''}".rstrip()
    names = " / ".join(p.opts) if p.opts else p.name
    req = "**required**" if p.required else ""
    return f"{indent}- `{names}` {req}{fmt_default(p)} — {p.help or ''}".rstrip()

def emit_command(cmd, level=2, prefix=""):
    full = f"{prefix} {cmd.name}".strip()
    doc = inspect.getdoc(cmd.callback) or ""
    lines.append(f"{'#'*level} `{full}`")
    if doc:
        lines.append("")
        lines.append(doc)
    lines.append("")
    if cmd.params:
        import click
        sig_parts = []
        for p in cmd.params:
            if isinstance(p, click.Option):
                sig_parts.append(p.opts[0])
            else:
                sig_parts.append(f"<{p.name}>")
        lines.append(f"**Signature:** `datatagger {full} " + " ".join(sig_parts) + "`")
        lines.append("")
        lines.append("| Parameter | Type | Description |")
        lines.append("|---|---|---|")
        for p in cmd.params:
            if isinstance(p, click.Option) and p.is_flag:
                typ = "flag"
            elif isinstance(p, click.Option):
                typ = "option"
            else:
                typ = "argument"
            names = " / ".join(p.opts) if isinstance(p, click.Option) else f"`{p.name}`"
            req = " **required**" if p.required else ""
            default = f" (default: {p.default})" if p.default not in (None, "") else ""
            lines.append(f"| {names} | {typ}{req} | {p.help or ''}{default} |")
    lines.append("")

# --- App-Ebene (search, raw) ---
for name, cmd in root.commands.items():
    if hasattr(cmd, "commands"):
        continue
    emit_command(cmd)

# --- Gruppen ---
groups = {g.name: g for g in root.commands.values() if hasattr(g, "commands")}
group_order = ["auth", "project", "folder", "dataset", "version", "version-file",
               "metadata", "parser-config", "export", "storage", "approval-queue",
               "user", "system"]
for gname in group_order:
    g = groups.get(gname)
    if not g:
        continue
    lines.append(f"## `{gname}`\n")
    for cname, cmd in g.commands.items():
        if hasattr(cmd, "commands"):  # Sub-Gruppen (metadata template/container/export)
            lines.append(f"### `{gname} {cname}`\n")
            for subname, sub in cmd.commands.items():
                emit_command(sub, 4, f"{gname} {cname}")
        else:
            emit_command(cmd, 3, gname)

out = "\n".join(lines).rstrip() + "\n"
dst = os.path.join(os.path.dirname(__file__), "..", "docs", "COMMANDS.md")
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst, "w", encoding="utf-8") as f:
    f.write(out)
print(f"OK: {dst} ({len(out.splitlines())} Zeilen)")
