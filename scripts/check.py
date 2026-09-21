#!/usr/bin/env python3
"""Repo consistency checks. No network, no dependencies.

- the Grok and Claude manifests are byte-identical
- the Cursor manifest carries the same identity fields
- .mcp.json and mcp.json declare the same server URL(s)
- every skills/*/SKILL.md has frontmatter with a matching name and a description
- the logo referenced by the manifests exists
- no em-dashes in prose or manifests (house style)
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []


def load(path: str):
    try:
        return json.loads((ROOT / path).read_text())
    except Exception as e:  # noqa: BLE001
        errors.append(f"{path}: {e}")
        return None


grok = load(".grok-plugin/plugin.json")
claude = load(".claude-plugin/plugin.json")
cursor = load(".cursor-plugin/plugin.json")
dot_mcp = load(".mcp.json")
mcp = load("mcp.json")

if grok and claude and (ROOT / ".grok-plugin/plugin.json").read_bytes() != (ROOT / ".claude-plugin/plugin.json").read_bytes():
    errors.append(".grok-plugin/plugin.json and .claude-plugin/plugin.json differ")

if grok and cursor:
    for key in ("name", "version", "description", "author", "homepage", "repository", "license", "keywords", "logo"):
        if grok.get(key) != cursor.get(key):
            errors.append(f".cursor-plugin/plugin.json `{key}` differs from .grok-plugin/plugin.json")
    if cursor.get("mcpServers") != "mcp.json":
        errors.append(".cursor-plugin/plugin.json must point `mcpServers` at mcp.json")
    if cursor.get("skills") != "skills/":
        errors.append(".cursor-plugin/plugin.json must point `skills` at skills/")

if grok and not (ROOT / grok.get("logo", "")).is_file():
    errors.append("logo referenced by the manifests is missing")

if dot_mcp and mcp:
    a = {k: v.get("url") for k, v in dot_mcp.get("mcpServers", {}).items()}
    b = {k: v.get("url") for k, v in mcp.get("mcpServers", {}).items()}
    if a != b:
        errors.append(f".mcp.json servers {a} differ from mcp.json servers {b}")
    for name, url in a.items():
        if not str(url).startswith("https://mcp.vertebrae.ai/"):
            errors.append(f"server `{name}` url {url!r} is not on mcp.vertebrae.ai")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
for skill_dir in sorted((ROOT / "skills").iterdir()):
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        errors.append(f"{skill_dir.name}: missing SKILL.md")
        continue
    m = FRONTMATTER.match(md.read_text())
    if not m:
        errors.append(f"{md.relative_to(ROOT)}: missing YAML frontmatter")
        continue
    fields = dict(
        line.split(":", 1) for line in m.group(1).splitlines() if ":" in line
    )
    fields = {k.strip(): v.strip() for k, v in fields.items()}
    if fields.get("name") != skill_dir.name:
        errors.append(f"{md.relative_to(ROOT)}: frontmatter name {fields.get('name')!r} != directory {skill_dir.name!r}")
    if len(fields.get("description", "")) < 40:
        errors.append(f"{md.relative_to(ROOT)}: description is missing or too short")

for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.json")):
    if ".git" in path.parts:
        continue
    if "—" in path.read_text():
        errors.append(f"{path.relative_to(ROOT)}: contains an em-dash")

if errors:
    print("check failed:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print("ok")
