<!--
  DevSquad Spec-Driven Development Toolkit
  https://devsquad.com

  Built and maintained by DevSquad.
  Licensed under MIT. See LICENSE for details.
-->

# DevSquad SDD Toolkit

A template repository for **Spec-Driven Development (SDD)**: a structured workflow where specifications drive implementation, not the other way around.

## Quick Start

Initialize in any project — no install required:

```bash
uvx --from git+https://github.com/elitedevsquad/spec-kit.git ds init
```

This creates the `.ds/` directory with all templates, scripts, and memory. Then follow the workflow below.

## The Workflow

```
init → constitution → specify → clarify → plan → tasks → implement
                                   ↑         ↓
                                   └── checklist
```

| Command | Purpose | Output |
|---------|---------|--------|
| `init` | Set up the `.ds/` structure in your project | `.ds/` directory |
| `constitution` | Define project principles and constraints | `.ds/memory/constitution.md` |
| `specify` | Pull a Jira issue and generate a structured spec | `specs/<feature>/spec.md` |
| `clarify` | Reduce ambiguity in the spec via targeted questions | Updated `spec.md` |
| `plan` | Design the implementation (architecture & decisions) | `specs/<feature>/plan.md` + artifacts |
| `checklist` | Validate requirement quality for a given domain | `specs/<feature>/checklists/<domain>.md` |
| `tasks` | Break the plan into ordered, executable tasks | `specs/<feature>/tasks.md` |
| `implement` | Execute tasks phase by phase | Working code |

## What Gets Installed

Running `/ds.init` creates this structure in your project:

```
.ds/
├── templates/
│   ├── commands/              # The 8 SDD command prompts
│   │   ├── init.md
│   │   ├── constitution.md
│   │   ├── specify.md
│   │   ├── clarify.md
│   │   ├── checklist.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── implement.md
│   ├── constitution-template.md
│   ├── spec-template.md
│   ├── plan-template.md
│   ├── tasks-template.md
│   ├── checklist-template.md
│   └── agent-file-template.md
├── scripts/bash/
│   ├── init.sh
│   ├── create-new-feature.sh
│   ├── setup-plan.sh
│   ├── check-prerequisites.sh
│   ├── update-agent-context.sh
│   └── common.sh
└── memory/
    └── constitution.md        # Ready to configure

specs/                         # Feature specs live here
```

## How to Use

1. **Initialize**: Run `uvx --from git+https://github.com/devsquad/spec-kit.git ds init` in your project root. This creates the `.ds/` directory with everything you need. (Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/))

2. **Create a constitution**: Run `/ds.constitution` to define your project's non-negotiable principles.

3. **Specify a feature**: Run `/ds.specify <JIRA-CODE>` (e.g., `/ds.specify SPR-23`). It fetches the Jira issue via MCP, asks you for the branch type (feat/fix/chore/etc.), creates a gitflow branch, and generates a structured spec.

4. **Clarify** (optional): Run `/ds.clarify` to identify and resolve ambiguities before planning.

5. **Plan the implementation**: Run `/ds.plan` to generate architecture decisions, data models, and interface contracts.

6. **Generate tasks**: Run `/ds.tasks` to break the plan into an ordered, dependency-aware task list.

7. **Implement**: Run `/ds.implement` to execute tasks phase by phase.

## Document Flow

Each step builds on the previous one:

- **Constitution** sets the rules that all specs must respect
- **Spec** pulls Jira issue content and structures it as a proper specification (WHAT & WHY)
- **Clarify** identifies and resolves ambiguities in the spec before planning
- **Plan** makes technical decisions constrained by the constitution
- **Checklist** validates requirement quality for specific domains (UX, security, API, etc.)
- **Tasks** decompose the plan into parallelizable work units
- **Implementation** follows the task order, marking progress as it goes

## Learn More

See [spec-driven.md](spec-driven.md) for the full philosophy and workflow guide behind Spec-Driven Development.
