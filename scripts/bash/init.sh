#!/usr/bin/env bash
# =============================================================================
# DevSquad Spec-Driven Development Toolkit
# https://devsquad.com
#
# Built and maintained by DevSquad.
# Licensed under MIT. See LICENSE for details.
# =============================================================================

# Initialize the DevSquad SDD structure in a project.
# Creates the .ds/ directory with templates, scripts, and memory.
# For Laravel projects: requires laravel/boost and installs skills in .ai/skills/.

set -e

JSON_MODE=false
TARGET_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        --json)
            JSON_MODE=true
            ;;
        --target)
            shift
            TARGET_DIR="$1"
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--target <path>]"
            echo ""
            echo "Initialize the DevSquad SDD structure in a project."
            echo ""
            echo "Options:"
            echo "  --json          Output in JSON format"
            echo "  --target <path> Target project directory (default: current directory)"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "This creates a .ds/ directory with:"
            echo "  .ds/templates/          Document templates"
            echo "  .ds/scripts/bash/       Shell scripts for the workflow"
            echo "  .ds/memory/             Project memory (constitution, etc.)"
            echo "  specs/                  Feature specs directory"
            echo ""
            echo "For Laravel projects with laravel/boost:"
            echo "  .ai/skills/ds-*/        Command skills (Laravel Boost format)"
            exit 0
            ;;
        *)
            ;;
    esac
    shift
done

# Determine the source directory (where this repo's templates live)
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Determine target directory
if [ -z "$TARGET_DIR" ]; then
    TARGET_DIR="$(pwd)"
fi
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

DS_DIR="$TARGET_DIR/.ds"

# Check if already initialized
if [ -d "$DS_DIR" ]; then
    echo "[ds] .ds/ directory already exists at $TARGET_DIR" >&2
    echo "[ds] Use this script only for fresh initialization." >&2
    exit 1
fi

# Detect Laravel project
IS_LARAVEL=false
HAS_BOOST=false

if [ -f "$TARGET_DIR/composer.json" ]; then
    if grep -q '"laravel/framework"' "$TARGET_DIR/composer.json" 2>/dev/null; then
        IS_LARAVEL=true
        if grep -q '"laravel/boost"' "$TARGET_DIR/composer.json" 2>/dev/null; then
            HAS_BOOST=true
        fi
    fi
fi

# For Laravel projects, require laravel/boost
if [ "$IS_LARAVEL" = true ] && [ "$HAS_BOOST" = false ]; then
    echo "[ds] Laravel project detected but laravel/boost is not installed." >&2
    echo "" >&2
    echo "[ds] Laravel Boost is required for DevSquad SDD in Laravel projects." >&2
    echo "[ds] Install it first:" >&2
    echo "" >&2
    echo "  composer require laravel/boost --dev" >&2
    echo "  php artisan boost:install" >&2
    echo "" >&2
    echo "[ds] Then run 'ds init' again." >&2
    exit 1
fi

# Print branded header
if ! $JSON_MODE; then
    echo ""
    echo "  ┌──────────────────────────────────────────────────┐"
    echo "  │                                                  │"
    echo "  │   ·  DevSquad · Spec-Driven Development  ·       │"
    echo "  │                                                  │"
    echo "  │   https://devsquad.com                           │"
    echo "  │                                                  │"
    echo "  └──────────────────────────────────────────────────┘"
    echo ""
fi

# Prompt for Jira project key
JIRA_KEY=""
if [ -t 0 ]; then
    echo "  Configuration:"
    echo "  ─────────────────────────────────────────────"
    echo "  Link a Jira project so you can run"
    echo "  /ds.specify 23 instead of /ds.specify SPR-23"
    echo ""
    printf "  Project key (e.g., SPR, PROJ) — leave blank to skip: "
    read -r JIRA_KEY_RAW
    if [ -n "$JIRA_KEY_RAW" ]; then
        JIRA_KEY=$(echo "$JIRA_KEY_RAW" | tr '[:lower:]' '[:upper:]')
    fi
    echo ""
fi

# Create directory structure
mkdir -p "$DS_DIR/templates"
mkdir -p "$DS_DIR/scripts/bash"
mkdir -p "$DS_DIR/memory"
mkdir -p "$TARGET_DIR/specs"

# Write Jira config if project key was provided
if [ -n "$JIRA_KEY" ]; then
    if command -v jq >/dev/null 2>&1; then
        jq -cn --arg key "$JIRA_KEY" '{"jira":{"project_key":$key}}' > "$DS_DIR/config.json"
    else
        printf '{\n  "jira": {\n    "project_key": "%s"\n  }\n}\n' "$JIRA_KEY" > "$DS_DIR/config.json"
    fi
fi

# Copy document templates
cp "$SOURCE_ROOT/templates/"*.md "$DS_DIR/templates/"

# Copy scripts
cp "$SOURCE_ROOT/scripts/bash/"*.sh "$DS_DIR/scripts/bash/"
chmod +x "$DS_DIR/scripts/bash/"*.sh

# Copy constitution template to memory as starting point
cp "$DS_DIR/templates/constitution-template.md" "$DS_DIR/memory/constitution.md"

# Install command templates based on project type
SKILLS_COUNT=0
COMMANDS_COUNT=0

if [ "$IS_LARAVEL" = true ]; then
    # Laravel + Boost: install as skills in .ai/skills/ds-{name}/SKILL.md
    for cmd_file in "$SOURCE_ROOT/templates/commands/"*.md; do
        cmd_name=$(basename "$cmd_file" .md)
        skill_name="ds-${cmd_name}"
        skill_dir="$TARGET_DIR/.ai/skills/$skill_name"
        mkdir -p "$skill_dir"

        # Extract description from frontmatter
        description=$(sed -n '/^---$/,/^---$/p' "$cmd_file" | grep '^description:' | sed 's/^description: *//')

        # Get body after frontmatter
        body=$(sed '1,/^---$/{ /^---$/!d; }' "$cmd_file" | sed '1,/^---$/{ /^---$/!d; }' | sed '1d')

        # Write SKILL.md in Boost format
        cat > "$skill_dir/SKILL.md" <<SKILLEOF
---
name: $skill_name
description: $description
---
$body
SKILLEOF

        SKILLS_COUNT=$((SKILLS_COUNT + 1))
    done
else
    # Non-Laravel: install commands in .ds/templates/commands/
    mkdir -p "$DS_DIR/templates/commands"
    cp "$SOURCE_ROOT/templates/commands/"*.md "$DS_DIR/templates/commands/"
    COMMANDS_COUNT=$(find "$DS_DIR/templates/commands" -name "*.md" | wc -l | tr -d ' ')
fi

# Count installed files
TEMPLATES_COUNT=$(find "$DS_DIR/templates" -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')
SCRIPTS_COUNT=$(find "$DS_DIR/scripts/bash" -name "*.sh" | wc -l | tr -d ' ')

if $JSON_MODE; then
    if command -v jq >/dev/null 2>&1; then
        jq -cn \
            --arg target "$TARGET_DIR" \
            --arg ds_dir "$DS_DIR" \
            --argjson is_laravel "$IS_LARAVEL" \
            --arg templates "$TEMPLATES_COUNT" \
            --arg commands "$COMMANDS_COUNT" \
            --arg skills "$SKILLS_COUNT" \
            --arg scripts "$SCRIPTS_COUNT" \
            --arg jira_key "$JIRA_KEY" \
            '{TARGET:$target,DS_DIR:$ds_dir,IS_LARAVEL:$is_laravel,TEMPLATES:($templates|tonumber),COMMANDS:($commands|tonumber),SKILLS:($skills|tonumber),SCRIPTS:($scripts|tonumber),JIRA_KEY:$jira_key}'
    else
        printf '{"TARGET":"%s","DS_DIR":"%s","IS_LARAVEL":%s,"TEMPLATES":%s,"COMMANDS":%s,"SKILLS":%s,"SCRIPTS":%s,"JIRA_KEY":"%s"}\n' \
            "$TARGET_DIR" "$DS_DIR" "$IS_LARAVEL" "$TEMPLATES_COUNT" "$COMMANDS_COUNT" "$SKILLS_COUNT" "$SCRIPTS_COUNT" "$JIRA_KEY"
    fi
else
    if [ "$IS_LARAVEL" = true ]; then
        echo "  Initialized in $TARGET_DIR"
        echo "  Mode: Laravel + Boost"
        echo ""
        echo "  Created:"
        echo "  ─────────────────────────────────────────────"
        echo "  .ai/skills/ds-*/        $SKILLS_COUNT skills (Boost format)"
        echo "  .ds/templates/          $TEMPLATES_COUNT document templates"
        echo "  .ds/scripts/bash/       $SCRIPTS_COUNT scripts"
        echo "  .ds/memory/             constitution.md"
        [ -n "$JIRA_KEY" ] && echo "  .ds/config.json         Jira project: $JIRA_KEY"
        echo "  specs/                  feature specs"
        echo ""
        echo "  Next steps:"
        echo "  ─────────────────────────────────────────────"
        echo "  1. $(printf '\033[32mphp artisan boost:update\033[0m')"
        echo "  2. /ds.constitution — define project constraints and principles"
        echo "  3. /ds.specify <JIRA-CODE> — create first feature spec"
    else
        echo "  Initialized in $TARGET_DIR"
        echo ""
        echo "  Created:"
        echo "  ─────────────────────────────────────────────"
        echo "  .ds/templates/          $TEMPLATES_COUNT document templates"
        echo "  .ds/templates/commands/ $COMMANDS_COUNT command templates"
        echo "  .ds/scripts/bash/       $SCRIPTS_COUNT scripts"
        echo "  .ds/memory/             constitution.md"
        [ -n "$JIRA_KEY" ] && echo "  .ds/config.json         Jira project: $JIRA_KEY"
        echo "  specs/                  feature specs"
        echo ""
        echo "  Next steps:"
        echo "  ─────────────────────────────────────────────"
        echo "  1. /ds.constitution — define project constraints and principles"
        echo "  2. /ds.specify <JIRA-CODE> — create first feature spec"
    fi
    echo ""
fi
