<!--
  DevSquad Spec-Driven Development Toolkit
  https://devsquad.com

  Built and maintained by DevSquad.
  Licensed under MIT. See LICENSE for details.
-->

# Spec Kit — Template Repository

A template repository for **Spec-Driven Development (SDD)**: a structured workflow where specifications drive implementation, not the other way around.

Copy the `.specify/` structure into any project to get a repeatable, AI-friendly development workflow built around seven commands: **constitution, specify, clarify, checklist, plan, tasks, implement**.

## The Workflow

```
constitution → specify → clarify → plan → tasks → implement
                           ↑         ↓
                           └── checklist
```

| Command | Purpose | Output |
|---------|---------|--------|
| `constitution` | Define project principles and constraints | `memory/constitution.md` |
| `specify` | Pull a Jira issue and generate a structured spec | `specs/<feature>/spec.md` |
| `clarify` | Reduce ambiguity in the spec via targeted questions | Updated `spec.md` |
| `plan` | Design the implementation (architecture & decisions) | `specs/<feature>/plan.md` + artifacts |
| `checklist` | Validate requirement quality for a given domain | `specs/<feature>/checklists/<domain>.md` |
| `tasks` | Break the plan into ordered, executable tasks | `specs/<feature>/tasks.md` |
| `implement` | Execute tasks phase by phase | Working code |

## What's Inside

```
templates/
├── commands/              # The 7 SDD command prompts
│   ├── constitution.md
│   ├── specify.md
│   ├── clarify.md
│   ├── checklist.md
│   ├── plan.md
│   ├── tasks.md
│   └── implement.md
├── constitution-template.md   # Project principles template
├── spec-template.md           # Feature specification template
├── plan-template.md           # Implementation plan template
├── tasks-template.md          # Task breakdown template
└── agent-file-template.md     # AI agent guidelines template

scripts/bash/
├── create-new-feature.sh      # Scaffold new feature directories
├── setup-plan.sh              # Initialize plan workspace
├── check-prerequisites.sh     # Verify required docs exist
├── update-agent-context.sh    # Update agent context file
└── common.sh                  # Shared utilities

spec-driven.md                 # End-to-end SDD workflow guide
```

## How to Use

1. **Copy into your project**: Copy the `templates/` and `scripts/` directories into your project's `.specify/` directory.

2. **Create a constitution**: Run the `constitution` command to define your project's non-negotiable principles.

3. **Specify a feature**: Run `specify` with a Jira issue code (e.g., `SPR-23`). It fetches the issue via MCP, asks you for the branch type (feat/fix/chore/etc.), creates a gitflow branch, and generates a structured spec from the Jira content.

4. **Plan the implementation**: Run `plan` to generate architecture decisions, data models, and interface contracts based on the spec.

5. **Generate tasks**: Run `tasks` to break the plan into an ordered, dependency-aware task list organized by user story.

6. **Implement**: Run `implement` to execute tasks phase by phase, with progress tracking and validation.

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
