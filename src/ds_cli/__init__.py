"""
DevSquad Spec-Driven Development Toolkit
https://devsquad.com

Built and maintained by DevSquad.
Licensed under MIT. See LICENSE for details.

Minimal CLI — just `ds init` to bootstrap any project.
Usage: uvx --from git+https://github.com/<org>/spec-kit.git ds init
"""

import os
import shutil
import sys
from pathlib import Path


def get_pack_dir() -> Path:
    """Return the path to the bundled templates and scripts."""
    return Path(__file__).parent / "pack"


def cmd_init(target: str | None = None) -> None:
    """Initialize the .ds/ structure in a project."""
    target_dir = Path(target) if target else Path.cwd()
    ds_dir = target_dir / ".ds"

    if ds_dir.exists():
        print(f"[ds] .ds/ already exists at {target_dir}", file=sys.stderr)
        print("[ds] Use this command only for fresh initialization.", file=sys.stderr)
        sys.exit(1)

    pack = get_pack_dir()
    if not pack.exists():
        print("[ds] Error: bundled pack not found. Reinstall the package.", file=sys.stderr)
        sys.exit(1)

    # Create structure
    (ds_dir / "templates" / "commands").mkdir(parents=True)
    (ds_dir / "scripts" / "bash").mkdir(parents=True)
    (ds_dir / "memory").mkdir(parents=True)
    (target_dir / "specs").mkdir(exist_ok=True)

    # Copy templates
    templates_src = pack / "templates"
    for f in templates_src.glob("*.md"):
        shutil.copy2(f, ds_dir / "templates" / f.name)

    # Copy command templates
    commands_src = pack / "commands"
    for f in commands_src.glob("*.md"):
        shutil.copy2(f, ds_dir / "templates" / "commands" / f.name)

    # Copy scripts
    scripts_src = pack / "scripts" / "bash"
    for f in scripts_src.glob("*.sh"):
        dest = ds_dir / "scripts" / "bash" / f.name
        shutil.copy2(f, dest)
        dest.chmod(0o755)

    # Copy constitution template to memory as starting point
    constitution_tmpl = ds_dir / "templates" / "constitution-template.md"
    if constitution_tmpl.exists():
        shutil.copy2(constitution_tmpl, ds_dir / "memory" / "constitution.md")

    # Count what was installed
    templates = list((ds_dir / "templates").glob("*.md"))
    commands = list((ds_dir / "templates" / "commands").glob("*.md"))
    scripts = list((ds_dir / "scripts" / "bash").glob("*.sh"))

    print()
    print(f"[ds] Initialized DevSquad SDD in {target_dir}")
    print()
    print(f"  .ds/templates/          {len(templates)} document templates")
    print(f"  .ds/templates/commands/ {len(commands)} command templates")
    print(f"  .ds/scripts/bash/       {len(scripts)} scripts")
    print(f"  .ds/memory/             constitution.md (ready to configure)")
    print(f"  specs/                  feature specs directory")
    print()
    print("Next steps:")
    print("  1. Run /ds.constitution to set up your project principles")
    print("  2. Run /ds.specify <JIRA-CODE> to create your first feature spec")


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: ds <command>")
        print()
        print("Commands:")
        print("  init [--target <path>]   Initialize .ds/ structure in a project")
        print()
        print("Run without installing:")
        print("  uvx --from git+https://github.com/<org>/spec-kit.git ds init")
        sys.exit(0)

    if args[0] == "init":
        target = None
        if len(args) >= 3 and args[1] == "--target":
            target = args[2]
        cmd_init(target)
    else:
        print(f"Unknown command: {args[0]}", file=sys.stderr)
        print("Run 'ds --help' for usage.", file=sys.stderr)
        sys.exit(1)
