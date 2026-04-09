---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
handoffs:
  - label: Create Tasks
    agent: ds.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: ds.checklist
    prompt: Create a checklist for the following domain...
scripts:
  sh: scripts/bash/setup-plan.sh --json
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

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Laravel detection**: Check if `composer.json` exists at the project root with `laravel/framework` as a dependency.
   - **If Laravel project**: You MUST activate the `laravel-best-practices` skill (installed by Laravel Boost) before making any architectural or technical decisions. All design choices — routing, models, controllers, services, middleware, validation, testing, queues, events, database migrations — MUST follow the official Laravel conventions as defined in that skill. Do not deviate from Laravel patterns unless the constitution explicitly overrides them.
   - This applies to all phases below (research, data model, contracts, and technical context).

4. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Re-evaluate Constitution Check post-design

5. **Security review (Laravel only)**: If Laravel project detected in step 3, run the `laravel-security-audit` skill against the plan artifacts (data-model.md, contracts/, quickstart.md) to verify no planned changes introduce security vulnerabilities. Review the plan against the 70+ security rules covering XSS, auth, injection, CSRF, secrets, headers, rate limiting, and more. If CRITICAL or HIGH findings are detected, you MUST revise the plan to address them before proceeding.

6. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION -> research task
   - For each dependency -> best practices task
   - For each integration -> patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Laravel projects**: When resolving technology choices, always prefer Laravel's built-in solutions (Eloquent, Blade/Livewire, queues, events, notifications, policies, form requests, etc.) over third-party alternatives unless the constitution or spec explicitly requires otherwise. Reference the `laravel-best-practices` skill for the canonical patterns.

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** -> `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Define interface contracts** (if project has external interfaces) -> `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

**Laravel projects**: Data models MUST use Eloquent conventions (fillable/guarded, casts, relationships, scopes). Contracts MUST follow Laravel's route/controller patterns (API resources, form requests, middleware). Use migrations for schema, factories and seeders for test data.

**Output**: data-model.md, /contracts/*, quickstart.md

### Phase 2: Security Review (Laravel only)

**Prerequisites:** Phase 1 complete, Laravel project detected in step 3

1. **Activate the `laravel-security-audit` skill** and review all plan artifacts against its security rules:
   - Audit `data-model.md` for mass assignment risks (`$guarded = []`, missing `$fillable`), sensitive attributes missing `$hidden`, and insecure field types
   - Audit `contracts/` for missing authorization middleware, unprotected routes, missing rate limiting, CSRF gaps, and API resource leaks
   - Audit `quickstart.md` for insecure patterns in the implementation guidance

2. **Cross-check planned patterns** against the Top 10 Laravel security risks:
   - XSS: Any planned use of `{!! !!}`, `HtmlString`, or unescaped output
   - Authorization: Every route/endpoint has middleware and policy coverage
   - Rate limiting: Login, API, OTP, and registration endpoints are throttled
   - Input validation: Using Form Requests with `$request->validated()`, not `$request->all()`
   - Cryptography: No `md5()`/`sha1()` for security, proper `hash_equals()` for comparisons
   - Mass assignment: All models define `$fillable` or `$guarded` properly
   - IDOR: Model bindings scoped to authenticated user/tenant

3. **Produce a security review summary** appended to the IMPL_PLAN:
   - List any CRITICAL/HIGH findings with required plan revisions
   - List MEDIUM/LOW findings as recommendations
   - If CRITICAL or HIGH findings exist, **revise the plan artifacts** to address them before stopping

**Output**: Security review summary in IMPL_PLAN, revised artifacts if needed

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
