"""
DevSquad Spec-Driven Development Toolkit
https://devsquad.com

Built and maintained by DevSquad.
Licensed under MIT. See LICENSE for details.

Minimal CLI — just `ds init` to bootstrap any project.
Usage: uvx --from git+https://github.com/<org>/spec-kit.git ds init
"""

import json
import re
import shutil
import sys
from pathlib import Path


def get_pack_dir() -> Path:
    """Return the path to the bundled templates and scripts."""
    return Path(__file__).parent / "pack"


def detect_laravel(target_dir: Path) -> bool:
    """Check if the target directory is a Laravel project."""
    composer_json = target_dir / "composer.json"
    if not composer_json.exists():
        return False
    try:
        data = json.loads(composer_json.read_text())
        deps = {**data.get("require", {}), **data.get("require-dev", {})}
        return "laravel/framework" in deps
    except (json.JSONDecodeError, KeyError):
        return False


def check_laravel_boost(target_dir: Path) -> bool:
    """Check if laravel/boost is installed in a Laravel project."""
    composer_json = target_dir / "composer.json"
    try:
        data = json.loads(composer_json.read_text())
        deps = {**data.get("require", {}), **data.get("require-dev", {})}
        return "laravel/boost" in deps
    except (json.JSONDecodeError, KeyError):
        return False


def get_composer_deps(target_dir: Path) -> set[str]:
    """Return a set of all composer dependency names."""
    composer_json = target_dir / "composer.json"
    try:
        data = json.loads(composer_json.read_text())
        deps = {**data.get("require", {}), **data.get("require-dev", {})}
        return set(deps.keys())
    except (json.JSONDecodeError, KeyError):
        return set()


def process_conditional_template(content: str, flags: dict[str, bool]) -> str:
    """Process conditional sections in a template.

    Removes or keeps blocks wrapped in <!-- [CONDITIONAL:key] --> markers
    based on the flags dict. Removes the marker comments themselves.
    """
    for key, enabled in flags.items():
        pattern = re.compile(
            rf"<!-- \[CONDITIONAL:{key}\] -->[ \t]*\n"
            rf"(.*?)"
            rf"<!-- \[/CONDITIONAL:{key}\] -->[ \t]*\n",
            re.DOTALL,
        )
        if enabled:
            content = pattern.sub(r"\1", content)
        else:
            content = pattern.sub("", content)

    return content


def command_to_skill(command_file: Path, skill_name: str) -> str:
    """Convert a command template to a Boost SKILL.md format.

    Reads the command template, extracts the description from its
    frontmatter, and rewrites the frontmatter in Boost's skill format
    (name + description). The rest of the content is kept as-is.
    """
    content = command_file.read_text()

    # Extract description from existing frontmatter
    description = ""
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        for line in frontmatter.splitlines():
            if line.startswith("description:"):
                description = line.split(":", 1)[1].strip()
                break
        body = content[match.end():]
    else:
        body = content

    # Build Boost SKILL.md with name + description frontmatter
    skill_content = f"""---
name: {skill_name}
description: {description}
---
{body}"""

    return skill_content


def install_boost_skills(target_dir: Path, pack: Path) -> int:
    """Install command templates as Laravel Boost skills in .ai/skills/."""
    skills_dir = target_dir / ".ai" / "skills"
    commands_src = pack / "commands"
    count = 0

    for f in sorted(commands_src.glob("*.md")):
        # command file name -> skill name: specify.md -> ds-specify
        cmd_name = f.stem
        skill_name = f"ds-{cmd_name}"
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_content = command_to_skill(f, skill_name)
        (skill_dir / "SKILL.md").write_text(skill_content)
        count += 1

    return count


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

    # Detect Laravel project
    is_laravel = detect_laravel(target_dir)

    if is_laravel and not check_laravel_boost(target_dir):
        print("[ds] Laravel project detected but laravel/boost is not installed.", file=sys.stderr)
        print("", file=sys.stderr)
        print("[ds] Laravel Boost is required for DevSquad SDD in Laravel projects.", file=sys.stderr)
        print("[ds] Install it first:", file=sys.stderr)
        print("", file=sys.stderr)
        print("  composer require laravel/boost --dev", file=sys.stderr)
        print("  php artisan boost:install", file=sys.stderr)
        print("", file=sys.stderr)
        print("[ds] Then run 'ds init' again.", file=sys.stderr)
        sys.exit(1)

    # Print branded header
    print()
    print("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510")
    print("  \u2502                                                  \u2502")
    print("  \u2502   \u00b7  DevSquad \u00b7 Spec-Driven Development  \u00b7       \u2502")
    print("  \u2502                                                  \u2502")
    print("  \u2502   https://devsquad.com                           \u2502")
    print("  \u2502                                                  \u2502")
    print("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518")
    print()

    # Prompt for Jira project key
    jira_key = ""
    try:
        print("  Configuration:")
        print("  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
        print("  Link a Jira project so you can run")
        print("  /ds.specify 23 instead of /ds.specify SPR-23")
        print()
        raw = input("  Project key (e.g., SPR, PROJ) \u2014 leave blank to skip: ").strip()
        if raw:
            jira_key = raw.upper()
        print()
    except (EOFError, KeyboardInterrupt):
        pass

    # Create .ds/ structure (templates, scripts, memory)
    (ds_dir / "templates").mkdir(parents=True)
    (ds_dir / "scripts" / "bash").mkdir(parents=True)
    (ds_dir / "memory").mkdir(parents=True)
    (target_dir / "specs").mkdir(exist_ok=True)

    # Write Jira config if project key was provided
    if jira_key:
        config = {"jira": {"project_key": jira_key}}
        (ds_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    # Copy document templates
    templates_src = pack / "templates"
    for f in templates_src.glob("*.md"):
        shutil.copy2(f, ds_dir / "templates" / f.name)

    # Copy scripts
    scripts_src = pack / "scripts" / "bash"
    for f in scripts_src.glob("*.sh"):
        dest = ds_dir / "scripts" / "bash" / f.name
        shutil.copy2(f, dest)
        dest.chmod(0o755)

    # Copy constitution template to memory as starting point
    if is_laravel:
        laravel_tmpl = ds_dir / "templates" / "constitution-laravel.md"
        if laravel_tmpl.exists():
            deps = get_composer_deps(target_dir)
            flags = {
                "brain": "r2luna/brain" in deps,
                "flux": "livewire/flux" in deps,
            }
            content = process_conditional_template(laravel_tmpl.read_text(), flags)
            (ds_dir / "memory" / "constitution.md").write_text(content)
        else:
            shutil.copy2(
                ds_dir / "templates" / "constitution-template.md",
                ds_dir / "memory" / "constitution.md",
            )
    else:
        constitution_tmpl = ds_dir / "templates" / "constitution-template.md"
        if constitution_tmpl.exists():
            shutil.copy2(constitution_tmpl, ds_dir / "memory" / "constitution.md")

    # Count what was installed
    templates = list((ds_dir / "templates").glob("*.md"))
    scripts = list((ds_dir / "scripts" / "bash").glob("*.sh"))

    # Handle command templates based on project type
    if is_laravel:
        # Install as Laravel Boost skills in .ai/skills/
        skills_count = install_boost_skills(target_dir, pack)
    else:
        # Non-Laravel: install commands in .ds/templates/commands/
        (ds_dir / "templates" / "commands").mkdir(parents=True, exist_ok=True)
        commands_src = pack / "commands"
        commands_count = 0
        for f in commands_src.glob("*.md"):
            shutil.copy2(f, ds_dir / "templates" / "commands" / f.name)
            commands_count += 1

    if is_laravel:
        print(f"  Initialized in {target_dir}")
        print("  Mode: Laravel + Boost")
        print()
        print("  Created:")
        print("  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
        print(f"  .ai/skills/ds-*/        {skills_count} skills (Boost format)")
        print(f"  .ds/templates/          {len(templates)} document templates")
        print(f"  .ds/scripts/bash/       {len(scripts)} scripts")
        print(f"  .ds/memory/             constitution.md")
        if jira_key:
            print(f"  .ds/config.json         Jira project: {jira_key}")
        print(f"  specs/                  feature specs")
        print()
        print("  Next steps:")
        print("  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
        print("  1. \033[32mphp artisan boost:update\033[0m")
        print("  2. /ds.constitution \u2014 define project constraints and principles")
        print("  3. /ds.specify <JIRA-CODE> \u2014 create first feature spec")
    else:
        print(f"  Initialized in {target_dir}")
        print()
        print("  Created:")
        print("  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
        print(f"  .ds/templates/          {len(templates)} document templates")
        print(f"  .ds/templates/commands/ {commands_count} command templates")
        print(f"  .ds/scripts/bash/       {len(scripts)} scripts")
        print(f"  .ds/memory/             constitution.md")
        if jira_key:
            print(f"  .ds/config.json         Jira project: {jira_key}")
        print(f"  specs/                  feature specs")
        print()
        print("  Next steps:")
        print("  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
        print("  1. /ds.constitution \u2014 define project constraints and principles")
        print("  2. /ds.specify <JIRA-CODE> \u2014 create first feature spec")

    print()


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
