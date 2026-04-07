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

1. **Run the init script**: Execute `{SCRIPT}` from the repo root and parse JSON output for TARGET, DS_DIR, and counts.

   **IMPORTANT**: This script should only run once per project. If `.ds/` already exists, it will error — inform the user and suggest checking the existing setup.

2. **Report what was created**:
   - `.ds/templates/` — document templates (spec, plan, tasks, constitution, checklist, agent-file)
   - `.ds/templates/commands/` — command prompt templates (init, constitution, specify, clarify, checklist, plan, tasks, implement)
   - `.ds/scripts/bash/` — shell scripts for branch creation, prerequisites, plan setup
   - `.ds/memory/constitution.md` — project constitution (copied from template, ready to fill)
   - `specs/` — directory where feature specs will live

3. **Suggest next steps**:
   - Run `/ds.constitution` to define the project's non-negotiable principles
   - Then use `/ds.specify <JIRA-CODE>` to create the first feature spec from a Jira issue
