---
description: Create or update the feature specification from a Jira issue, pulling all context via MCP and creating a gitflow-compliant branch.
handoffs:
  - label: Build Technical Plan
    agent: ds.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: ds.clarify
    prompt: Clarify specification requirements
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
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

## Project Configuration

Before interpreting the user input, check for a default Jira project key:

1. Read `.ds/config.json` (relative to repo root). If it exists and contains `jira.project_key`, store that as the **default project key**.
2. **Expand bare numbers**: If the user input is a bare number (e.g., `23`, `142`), prepend the default project key to form the full Jira code (e.g., `SPR-23`).
3. **Full codes pass through**: If the user input already contains a hyphen and letters (e.g., `SPR-23`, `PROJ-142`), use it as-is — the explicit code always wins, even if it differs from the default project.
4. **No config + bare number**: If `.ds/config.json` does not exist or has no `jira.project_key`, and the user provides only a bare number, ask the user for the full Jira issue code before proceeding.

## Outline

The user provides a **Jira issue code** (e.g., `SPR-23`, `PROJ-142`) or a **bare issue number** (e.g., `23`) when a default project is configured. This is the primary input. If the user also provides additional context or description, use it to supplement the Jira content.

Given the Jira issue code, do this:

1. **Fetch the Jira issue via MCP**: Use the Notion search tool (which has Jira connected as a source) to look up the issue by its code. Extract:
   - Issue title / summary
   - Issue type (Story, Bug, Task, Sub-task, Epic, etc.)
   - Description and acceptance criteria
   - Priority, labels, components
   - Linked issues and dependencies
   - Any attachments or comments with relevant context
   - Sprint or milestone information

   If the issue cannot be found, ask the user to verify the code and try again.

2. **Ask the user for the branch type**: Present the gitflow branch types and ask which one applies to this work:

   | Type | Branch prefix | Use when |
   |------|--------------|----------|
   | Feature | `feat/` | New functionality or user story |
   | Fix | `fix/` | Bug fix |
   | Chore | `chore/` | Maintenance, dependency updates, config changes |
   | Refactor | `refactor/` | Code restructuring without behavior change |
   | Docs | `docs/` | Documentation only |
   | Hotfix | `hotfix/` | Urgent production fix |

   **Auto-suggest based on Jira issue type**: If the Jira issue type is "Story" or "Epic", suggest `feat/`. If "Bug", suggest `fix/`. Otherwise suggest based on best match. The user always has final say.

   The branch name will be: `{type}/{JIRA_CODE}` (e.g., `feat/SPR-23`, `fix/PROJ-142`).

3. **Create the feature branch** by running the script with `--branch-name` and `--json`:

   ```bash
   {SCRIPT} --json --branch-name "{type}/{JIRA_CODE}" "{Jira issue title}"
   ```

   **IMPORTANT**:
   - Always include the JSON flag (`--json`) so the output can be parsed reliably
   - You must only ever run this script once per feature
   - The JSON output will contain BRANCH_NAME and SPEC_FILE paths
   - The `--branch-name` flag passes the full gitflow branch name (e.g., `feat/SPR-23`)

4. Load `templates/spec-template.md` to understand required sections.

5. Follow this execution flow, using the **Jira issue content** as the primary source:

    1. Parse Jira issue content
       If the issue has no description: use the title and any acceptance criteria or comments as the base
    2. Extract key concepts from the Jira issue
       Identify: actors, actions, data, constraints, acceptance criteria
    3. For unclear aspects:
       - Make informed guesses based on Jira context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       Map Jira acceptance criteria to user scenarios where available
       If no clear user flow: ERROR "Cannot determine user scenarios from Jira issue"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use Jira acceptance criteria as the foundation
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

6. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the Jira issue while preserving section order and headings.

   **Include Jira traceability**: Add a `## Jira Source` section at the top of the spec with:
   - Jira issue code and title (use the fully expanded code, e.g., `SPR-23`)
   - Project key (from config or as provided)
   - Issue type and priority
   - Link to the original Jira issue (if URL is available)
   - Date the spec was generated

7. **Specification Quality Validation**: After writing the initial spec, validate against quality criteria:

   a. **Run Validation Check**: Review the spec against these quality criteria:

      **Content Quality**:
      - No implementation details (languages, frameworks, APIs)
      - Focused on user value and business needs
      - Written for non-technical stakeholders
      - All mandatory sections completed

      **Requirement Completeness**:
      - Requirements are testable and unambiguous
      - Success criteria are measurable
      - Success criteria are technology-agnostic (no implementation details)
      - All acceptance scenarios are defined
      - Edge cases are identified
      - Scope is clearly bounded
      - Dependencies and assumptions identified

      **Feature Readiness**:
      - All functional requirements have clear acceptance criteria
      - User scenarios cover primary flows
      - Feature meets measurable outcomes defined in Success Criteria
      - No implementation details leak into specification

   b. **Handle Validation Results**:

      - **If all items pass**: Proceed to step 8

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

8. Report completion with:
   - Jira issue code and title
   - Branch name (gitflow format)
   - Spec file path
   - Validation results
   - Readiness for the next phase (`/ds.clarify` or `/ds.plan`)

**NOTE:** The script creates and checks out the new branch and initializes the spec file before writing.

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec.
- The Jira issue is the **source of truth** — the spec enriches and structures its content, not replaces it.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a Jira issue:

1. **Use Jira content as the foundation**: Acceptance criteria, description, and comments are the primary source
2. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
3. **Document assumptions**: Record reasonable defaults in the Assumptions section
4. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
5. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
6. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
7. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.)

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)
