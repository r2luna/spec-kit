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

set -e

JSON_MODE=false
TARGET_DIR=""
ARGS=()

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
            echo "  .ds/templates/          Command and document templates"
            echo "  .ds/scripts/bash/       Shell scripts for the workflow"
            echo "  .ds/memory/             Project memory (constitution, etc.)"
            echo "  specs/                  Feature specs directory"
            exit 0
            ;;
        *)
            ARGS+=("$1")
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

# Create directory structure
mkdir -p "$DS_DIR/templates/commands"
mkdir -p "$DS_DIR/scripts/bash"
mkdir -p "$DS_DIR/memory"
mkdir -p "$TARGET_DIR/specs"

# Copy templates
cp "$SOURCE_ROOT/templates/"*.md "$DS_DIR/templates/"
cp "$SOURCE_ROOT/templates/commands/"*.md "$DS_DIR/templates/commands/"

# Copy scripts
cp "$SOURCE_ROOT/scripts/bash/"*.sh "$DS_DIR/scripts/bash/"
chmod +x "$DS_DIR/scripts/bash/"*.sh

# Copy constitution template to memory as starting point
cp "$DS_DIR/templates/constitution-template.md" "$DS_DIR/memory/constitution.md"

# Report
TEMPLATES_COUNT=$(find "$DS_DIR/templates" -name "*.md" | wc -l | tr -d ' ')
COMMANDS_COUNT=$(find "$DS_DIR/templates/commands" -name "*.md" | wc -l | tr -d ' ')
SCRIPTS_COUNT=$(find "$DS_DIR/scripts/bash" -name "*.sh" | wc -l | tr -d ' ')

if $JSON_MODE; then
    if command -v jq >/dev/null 2>&1; then
        jq -cn \
            --arg target "$TARGET_DIR" \
            --arg ds_dir "$DS_DIR" \
            --arg templates "$TEMPLATES_COUNT" \
            --arg commands "$COMMANDS_COUNT" \
            --arg scripts "$SCRIPTS_COUNT" \
            '{TARGET:$target,DS_DIR:$ds_dir,TEMPLATES:($templates|tonumber),COMMANDS:($commands|tonumber),SCRIPTS:($scripts|tonumber)}'
    else
        printf '{"TARGET":"%s","DS_DIR":"%s","TEMPLATES":%s,"COMMANDS":%s,"SCRIPTS":%s}\n' \
            "$TARGET_DIR" "$DS_DIR" "$TEMPLATES_COUNT" "$COMMANDS_COUNT" "$SCRIPTS_COUNT"
    fi
else
    echo ""
    echo "[ds] Initialized DevSquad SDD in $TARGET_DIR"
    echo ""
    echo "  .ds/templates/          $TEMPLATES_COUNT document templates"
    echo "  .ds/templates/commands/ $COMMANDS_COUNT command templates"
    echo "  .ds/scripts/bash/       $SCRIPTS_COUNT scripts"
    echo "  .ds/memory/             constitution.md (ready to configure)"
    echo "  specs/                  feature specs directory"
    echo ""
    echo "Next steps:"
    echo "  1. Run /ds.constitution to set up your project principles"
    echo "  2. Run /ds.specify <JIRA-CODE> to create your first feature spec"
fi
