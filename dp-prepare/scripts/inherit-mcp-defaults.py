#!/usr/bin/env python3
"""Pre-register a new worktree in ~/.claude.json so it inherits the source
repo's per-project MCP on/off state (disabledMcpServers).

Why: Claude Code only creates a `projects[<dir>]` entry on the first session
in that directory, and the default for every MCP server is ON. A fresh
worktree therefore boots every globally-configured MCP server (figma, safari,
chrome-devtools, ...) even if the source repo had them switched off via /mcp.

Usage:
    python3 inherit-mcp-defaults.py <source-repo-path> <new-worktree-path>

Behaviour:
  - copies `disabledMcpServers` from the source repo's project entry
  - falls back to DEFAULT_DISABLED when the source has none
  - never removes anything already present on the worktree entry
  - backs up ~/.claude.json before writing, validates JSON after
Exit code is always 0 unless the config file itself is unreadable; failures
are printed so the caller can report them (non-blocking stage policy).
"""
import json
import os
import shutil
import sys
import time

DEFAULT_DISABLED = ["safari-devtools", "figma"]
CONFIG = os.path.expanduser("~/.claude.json")


def as_list(v):
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except json.JSONDecodeError:
            return []
    return list(v) if isinstance(v, list) else []


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src = os.path.abspath(os.path.expanduser(sys.argv[1]))
    dst = os.path.abspath(os.path.expanduser(sys.argv[2]))

    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    projects = cfg.setdefault("projects", {})

    inherited = as_list(projects.get(src, {}).get("disabledMcpServers"))
    origin = f"source {src}" if inherited else "DEFAULT_DISABLED (source has none)"
    if not inherited:
        inherited = DEFAULT_DISABLED

    entry = projects.setdefault(dst, {})
    current = as_list(entry.get("disabledMcpServers"))
    merged = current + [s for s in inherited if s not in current]
    if merged == current and dst in projects:
        print(f"[inherit-mcp-defaults] no change: {dst} already has {current}")
        return 0
    entry["disabledMcpServers"] = merged

    backup = f"{CONFIG}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(CONFIG, backup)
    tmp = CONFIG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    with open(tmp, encoding="utf-8") as f:
        json.load(f)  # validate before replacing
    os.replace(tmp, CONFIG)
    print(f"[inherit-mcp-defaults] {dst}: disabledMcpServers={merged} (from {origin}; backup {backup})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # non-blocking stage: report, don't crash the pipeline
        print(f"[inherit-mcp-defaults] FAILED: {e}")
        sys.exit(0)
