---
description: Audit a Laravel project for security vulnerabilities based on the Securing Laravel knowledge base
model: sonnet
---

# Laravel Security Audit

Analyze a Laravel project for security vulnerabilities using the consolidated knowledge from the Securing Laravel blog (Stephen Rees-Carter).

## Knowledge Base

Before starting, read the rules file (relative to this skill):
`references/rules.md`

This contains 70+ rules organized by category (XSS, Secrets, Dependencies, Crypto, Auth, CSP, HSTS, SRI, Type Juggling, Rate Limiting, API Leaks, CSRF, Authentication, File Uploads, Injection). Each rule has an ID, grep pattern, severity, and fix.

For deeper context on any finding, reference:
`references/tips.md`

## Input

The user will provide `$ARGUMENTS` which should be one of:
- A **path** to a Laravel project directory
- A **GitHub repo URL** to clone/analyze
- `--full` to run all checks
- `--quick` to run only the Top 10 checks
- Specific categories like `--xss`, `--auth`, `--api`, `--config`, `--injection`, `--headers`, `--crypto`, `--csrf`, `--dependencies`

If no arguments, ask the user for the project path.

## Audit Process

### Phase 1: Project Discovery

1. Verify it's a Laravel project (check `artisan`, `composer.json`, `app/` structure)
2. Detect Laravel version from `composer.lock`
3. Detect PHP version from `composer.json` require
4. Check if it uses Livewire, Inertia, Vue, React, or Blade
5. List installed packages from `composer.json`

### Phase 2: Passive Scans (from Pentesting Part 1)

Run these automated checks in parallel:

**Dependencies**
- Run `composer audit --locked` for known vulnerabilities
- Check for outdated packages via `composer outdated --direct --locked`
- Check for debug dependencies in production (`require-dev` packages like debugbar, telescope in `require`)
- Look for `npm audit` issues if `package-lock.json` exists

**Committed Secrets**
- Search for hardcoded credentials in `config/*.php`, `.env.example`, Service Providers
- Look for API keys, passwords, tokens in source code
- Check if `.env` is in `.gitignore`
- Look for hardcoded admin emails in `app/` and `config/`

**Configuration**
- Check `APP_DEBUG` in `.env.example` (should be `false`)
- Check `APP_ENV` in `.env.example` (should be `production`)
- Check `SESSION_SECURE_COOKIE` setting
- Check `SESSION_HTTP_ONLY` setting
- Verify `env()` is NOT used outside config files: search `app/`, `routes/`, `resources/` for `env(` calls
- Check for `phpinfo()` in routes or controllers

### Phase 3: Code Analysis (from Pentesting Parts 2-4)

**#1 XSS (Top 10 #1)**
Search for unescaped output patterns:
- `{!! ` in Blade templates (should be rare and justified)
- `new HtmlString(` without proper escaping
- `Js::from()` misuse
- `@php echo` in Blade
- `strip_tags()` used as XSS protection (insufficient)
- `nl2br()` usage (unsafe)
- Inline `<script>` tags in Blade with user data
- Check if Blade components pass unescaped user data

**#2 Credentials & Hardcoded Values (Top 10 #2)**
- Hardcoded admin emails or domains in code
- API keys or secrets in source files
- Database credentials outside `.env`

**#3 Outdated Dependencies (Top 10 #3)**
- Already covered in Phase 2

**#4 Insecure Cryptography (Top 10 #4)**
- Usage of `md5()` or `sha1()` for security purposes
- Custom encryption implementations (don't roll your own)
- Weak bcrypt rounds (check config/hashing.php)
- Missing `hash_equals()` for sensitive comparisons (using `==` or `===` instead)
- `rand()` or `mt_rand()` for security-sensitive values (should use `random_int()` or `Str::random()`)

**#5 Missing Authorisation (Top 10 #5)**
- Routes without middleware: check `routes/web.php`, `routes/api.php` for unprotected routes
- Controllers without `authorize()`, `$this->authorize()`, or Policy usage
- Missing `Gate::define()` or Policy classes for models
- Resource controllers without `authorizeResource()`
- `orWhere` without proper scoping (can leak data across users)
- Check broadcast channels for proper auth
- Webhook routes without signature verification
- `findOrFail($id)` without scope of tenant/user (IDOR)
- Routes with `Route::model()` binding without policy

**#6 Missing CSP (Top 10 #6)**
- Check for Content-Security-Policy header in middleware or server config
- Check for `unsafe-inline` in existing CSP
- Alpine.js without CSP build

**#7 Missing HSTS (Top 10 #7)**
- Check for Strict-Transport-Security header
- Check if HTTPS is forced (TrustProxies, `URL::forceScheme('https')`)

**#8 Missing SRI (Top 10 #8)**
- Check `<script>` and `<link>` tags for `integrity` attributes on external resources

**#9 Type Juggling (Top 10 #9)**
- Loose comparisons `==` with sensitive values (should be `===`)
- Missing `hash_equals()` for token/key comparisons
- Type coercion in broadcast routes

**#10 Rate Limiting (Top 10 #10)**
- Login routes without `throttle` middleware
- API routes without rate limiting
- OTP/2FA verification without rate limiting
- Registration forms without rate limiting
- Password reset without rate limiting

### Phase 4: Additional Checks

**API Security**
- Models without `$hidden` for sensitive attributes
- Controllers returning full models (`return $user`) instead of API Resources
- `$request->all()` usage (should be `$request->validated()`)
- Missing `$fillable`/`$guarded` on models
- API responses on GET requests that include sensitive data

**CSRF**
- Routes excluded from CSRF without justification
- File upload endpoints that might bypass CSRF

**Authentication**
- Check for `MustVerifyEmail` on User model
- Check password validation rules (compromised password check, length, etc.)
- Check bcrypt rounds in `config/hashing.php`
- 2FA implementation (if exists)
- Password reset token security
- Session configuration (`config/session.php`)

**Session & Cookie Security**
- `config/session.php` — `same_site` should be `lax` or `strict`
- `encrypt` cookies enabled
- Session driver `file` in multi-server environments (should be `redis`/`database`)

**Environment & Debug**
- `dump()`, `dd()`, `ray()` calls left in code
- Telescope/Debugbar enabled in production config
- Telescope/Pulse gate not configured (open to all users in production)
- Stack trace exposure (check `config/app.php` debug setting)
- `phpinfo()` accessible routes

**Sensitive Data in Logs**
- `Log::` calls logging passwords, tokens, credit card numbers, or PII
- `report()` helper logging full request with auth headers
- Custom exception handlers exposing sensitive data in messages
- `context()` or `withContext()` adding sensitive request data to all log entries
- `config/logging.php` — check if log channel exposes data to third-party services (Slack, Papertrail, etc.)
- Request/response logging middleware capturing sensitive payloads
- Mail templates with `{!! !!}` (XSS via email)

**Mail & Notifications**
- Header injection in `Mail::to($userInput)`
- SMS/notification flooding without rate limiting

**File Security**
- File upload validation (checking actual file type, not just extension)
- SVG uploads allowed in image validation
- Local file access restrictions
- Temporary file URL handling

**Injection**
- `DB::raw()`, `whereRaw()`, `selectRaw()` with user input
- `orderByRaw()`, `groupByRaw()`, `havingRaw()` with user input
- `DB::statement()` with string concatenation
- `->when()` with raw queries inside
- Dynamic column names from request (`$request->get('sort_by')` used directly in `orderBy()`)
- Shell commands via `Process` or similar with user input
- `unserialize()` with user data
- `json_decode()` + class morphing / polymorphic relations with unrestricted `$morphMap`

**Open Redirect**
- `redirect($request->input('url'))` or `redirect()->to($userInput)`
- `back()` without referer validation
- `intended()` without URL whitelist

**SSRF (Server-Side Request Forgery)**
- `Http::get($userInput)` — HTTP requests with user-controlled URLs
- `file_get_contents($url)` with external input
- Webhook URLs provided by users without destination validation

**Mass Assignment**
- `$guarded = []` on models (empty guarded = everything fillable)
- `forceFill()` or `forceCreate()` with user input
- Missing `$fillable`/`$guarded` on models

**Livewire-Specific** (if detected in Phase 1)
- Public properties exposing sensitive data
- `#[Locked]` missing on properties that should not be changed by client
- File uploads via Livewire without proper validation
- Public methods exposed without authorization checks

**Queue & Job Security**
- Jobs dispatched with unvalidated data
- `ShouldBeUnique` missing on jobs that should not duplicate
- Missing timeout/retry config allowing resource exhaustion

## Output Format

Generate a security audit report as a markdown file saved to the project root as `SECURITY-AUDIT.md`:

```markdown
# Security Audit Report

**Project**: {project name}
**Laravel Version**: {version}
**PHP Version**: {version}
**Date**: {date}
**Auditor**: Claude (based on Securing Laravel methodology)

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | X |
| HIGH     | X |
| MEDIUM   | X |
| LOW      | X |
| INFO     | X |

## Findings

### [CRITICAL] Finding Title
- **Category**: {Top 10 category or OWASP reference}
- **File**: `path/to/file.php:line`
- **Description**: What the issue is
- **Impact**: What could happen if exploited
- **Fix**: How to fix it with code example
- **Reference**: Link to Securing Laravel article

### [HIGH] ...
(repeat for each finding)

## Checklist

- [ ] XSS: No unescaped user output
- [ ] Auth: All routes have proper authorisation
- [ ] API: No leaky model attributes
- [ ] Config: Debug mode disabled, .env protected
- [ ] Crypto: No MD5/SHA-1, proper bcrypt rounds
- [ ] Headers: CSP, HSTS, SRI configured
- [ ] Rate Limiting: Login, API, OTP protected
- [ ] Dependencies: No known vulnerabilities
- [ ] CSRF: All forms protected
- [ ] Secrets: No hardcoded credentials
- [ ] SSRF: No HTTP requests with user-controlled URLs
- [ ] Open Redirect: All redirects use whitelisted URLs
- [ ] Mass Assignment: No empty $guarded or unscoped forceFill
- [ ] IDOR: All model bindings have proper scoping/policies
- [ ] Livewire: Locked properties and authorized methods
- [ ] Session: SameSite, secure cookies, appropriate driver
- [ ] Logging: No sensitive data (passwords, tokens, PII) in logs
- [ ] Queues: Jobs validated, unique where needed, timeouts configured
```

## Severity Classification

| Severity | Criteria |
|----------|----------|
| CRITICAL | Directly exploitable, data breach risk (SQLi, RCE, auth bypass) |
| HIGH | Exploitable with some conditions (XSS, IDOR, missing auth on sensitive routes) |
| MEDIUM | Security weakness, defense-in-depth (missing headers, weak config) |
| LOW | Minor issue, best practice (outdated non-vulnerable deps, missing SRI) |
| INFO | Informational, no direct risk (suggestions, improvements) |

## Rules

- **DO NOT** modify any project files -- this is a read-only audit
- **DO NOT** run the project or execute artisan commands
- **DO** use parallel agents for independent checks to speed up the audit
- **DO** provide specific file paths and line numbers for every finding
- **DO** include code examples for fixes
- **DO** reference the relevant Securing Laravel article for each finding
- **PRIORITIZE** findings by severity -- CRITICAL and HIGH first
- **SKIP** findings you're not confident about (avoid false positives)
- For `--quick` mode, only check the Top 10 items
- For `--full` mode, run all phases including additional checks
- Default to `--full` if no flag specified
