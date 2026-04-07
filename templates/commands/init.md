---
description: Initialize the DevSquad SDD structure in the current project.
handoffs:
  - label: Create Constitution
    agent: ds.constitution
    prompt: Set up the project constitution with our principles
scripts:
  sh: scripts/bash/init.sh --json
---

<!--
  DevSquad Spec-Driven Development Toolkit
  https://devsquad.com

  Built and maintained by DevSquad.
  Licensed under MIT. See LICENSE for details.
-->

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command initializes the DevSquad Spec-Driven Development structure in the current project. It creates the `.ds/` directory with all templates, scripts, and memory needed for the SDD workflow.

### Laravel Detection

The init script automatically detects Laravel projects:

- **Laravel project detected** (composer.json has `laravel/framework`):
  - **Requires `laravel/boost`** — if not installed, the script will stop and ask the user to install it first (`composer require laravel/boost --dev && php artisan boost:install`)
  - Command templates are installed as **Laravel Boost skills** in `.ai/skills/ds-*/SKILL.md` following the [Boost skills format](https://laravel.com/docs/boost)
  - Document templates, scripts, and memory still go in `.ds/`

- **Non-Laravel project**:
  - Everything goes in `.ds/` (templates, commands, scripts, memory)

### Execution

1. **Run the init script**: Execute `{SCRIPT}` from the repo root and parse JSON output for TARGET, DS_DIR, IS_LARAVEL, JIRA_KEY, and counts.

   The script will interactively prompt for a **Jira project key** (e.g., `SPR`, `PROJ`). If provided, it writes `.ds/config.json` with the key so that `/ds.specify` can expand bare issue numbers (e.g., `/ds.specify 23` → `SPR-23`). The user can skip this by pressing Enter.

   **IMPORTANT**: This script should only run once per project. If `.ds/` already exists, it will error — inform the user and suggest checking the existing setup.

2. **Report what was created**:

   **For Laravel + Boost projects:**
   - `.ai/skills/ds-*/` — command skills in Boost format (auto-discovered by Boost)
   - `.ds/templates/` — document templates (spec, plan, tasks, constitution, checklist, agent-file)
   - `.ds/scripts/bash/` — shell scripts for branch creation, prerequisites, plan setup
   - `.ds/memory/constitution.md` — project constitution (copied from template, ready to fill)
   - `.ds/config.json` — Jira project configuration (if a project key was provided)
   - `specs/` — directory where feature specs will live

   **For non-Laravel projects:**
   - `.ds/templates/commands/` — command prompt templates
   - `.ds/templates/` — document templates
   - `.ds/scripts/bash/` — shell scripts
   - `.ds/memory/constitution.md` — project constitution
   - `.ds/config.json` — Jira project configuration (if a project key was provided)
   - `specs/` — directory where feature specs will live

3. **Suggest next steps**:
   - For Laravel: run `php artisan boost:update` to register the new skills
   - Run `/ds.constitution` to define the project's non-negotiable principles
   - Then use `/ds.specify <JIRA-CODE>` (or just `/ds.specify <number>` if a Jira project key was configured) to create the first feature spec from a Jira issue
