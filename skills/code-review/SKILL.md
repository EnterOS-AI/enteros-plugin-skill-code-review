---
name: code-review
description: "Review code for best practices, modularity, scalability, appropriate abstraction, test coverage, redundancy, hardcoded values, type safety, performance, naming, API design, async patterns, config/env sync, template consistency, and documentation alignment. Generates detailed report with issues and recommendations."
origin: molecule-skill-code-review
---

# Code Review

Perform a comprehensive code review of recent changes or specified files to ensure quality standards.

## Acquiring the diff (Gitea) — do this FIRST

Before scoring any criterion you MUST have the **full unified diff** in hand.
Most false `REQUEST_CHANGES` verdicts ("the patch body is absent" / "I can't see
the diff" / files listed as `(no patch)`) come from reading the per-file `patch`
field of the PR *files* endpoint, which Gitea **omits** for large, binary, or
many-file PRs — the field is simply not present, so the review sees `(no patch)`
for every file. **Never conclude "I can't see the diff" from an empty `patch`
field.** Fetch the unified diff instead.

### Correct: the `/api/v1` PR diff endpoint

```bash
# OWNER/REPO/N come from the PR. GITEA_API_URL ends in /api/v1 — e.g.
#   internal: http://localhost:3200/api/v1   (preferred; skips the CF edge)
#   public:   https://git.moleculesai.app/api/v1
curl -fsS \
  -H "Authorization: token $GITEA_TOKEN" \
  -H "User-Agent: Mozilla/5.0" \
  "$GITEA_API_URL/repos/$OWNER/$REPO/pulls/$N.diff"
```

This returns the real unified diff (`diff --git …`, HTTP 200, non-empty). The
`.patch` variant (`…/pulls/$N.patch`) returns the same hunks in git-mailbox
format when you also need commit metadata.

### Wrong paths — these ARE the bug, do NOT use

- **The non-`/api/v1` web route** `…/$OWNER/$REPO/pulls/$N.diff` (missing the
  `/api/v1/repos/` prefix) returns **HTTP 404**, and behind Cloudflare on the
  public host it returns a CF-1010 challenge page. This is the single most common
  cause of the false "patch body absent" verdict.
- **`gh pr diff`** targets github.com and cannot read this Gitea instance.
- **Relying solely on `…/pulls/$N/files`** — use it only for per-file metadata
  (status, +/- counts, filenames). Its `patch` field is optional; when it is
  missing, read the hunks from the `.diff` above, not from `files`.

### Auth / host notes

- Always send **both** the `Authorization: token $GITEA_TOKEN` header **and** a
  browser `User-Agent` (e.g. `Mozilla/5.0`); the public host's WAF blocks default
  agents (CF-1010).
- Prefer the internal host (`http://localhost:3200/api/v1`) when reachable; fall
  back to the public `https://git.moleculesai.app/api/v1` with the same headers.

Only after the `.diff` fetch returns non-empty should you begin scoring the
criteria below. A genuinely empty diff (0 bytes, HTTP 200) means the PR has no
changes — only then is "no diff" accurate.

## Review Criteria

### 1. Best Practices
- Follows TypeScript strict mode conventions
- Proper error handling (try/catch, error types, no silent failures)
- No hardcoded values (use environment variables or constants)
- Proper logging with appropriate log levels
- Security best practices (input validation, no SQL injection, XSS prevention)
- No console.log in production code (use logger)

### 2. Modularity
- Single responsibility principle (each function/class does one thing)
- Functions are small and focused (< 50 lines ideally)
- No code duplication (DRY principle) — but don't extract shared helpers until the pattern repeats at least twice
- Clear separation of concerns (routes, services, utilities)
- No speculative generalization — don't introduce interfaces or base classes for a single implementation

### 3. Scalability
- Efficient database queries (proper indexing, no N+1 queries)
- Connection pooling used correctly
- Async operations handled properly
- No blocking operations in hot paths

### 4. Abstraction
- Abstraction is justified by actual usage, not speculative future-proofing
- Interfaces/types used where they solve a real problem (multiple implementations, test mocking, API contracts)
- Avoid abstraction for a single call site — inline until duplication emerges
- Adapter pattern used for external services (LLM, database) where swapability is a real requirement
- Configuration externalized (not hardcoded)
- Prefer concrete types over generic abstractions when the scope is small

### 5. Test Coverage
- Unit tests exist for all utility functions and service functions
- Service layer has integration tests
- Edge cases are covered
- Test files go in `tests/unit/` or `tests/integration/`, named `*.test.ts`
- All exported functions have at least one test

### 6. No Redundancy
- No duplicate code blocks (extract to shared functions/utilities only after the pattern appears twice)
- No repeated logic across files (consolidate into services only when the duplication is real, not coincidentally similar)
- No redundant imports or unused variables
- No copy-pasted code with minor variations (use parameters/generics when the duplication is structural, not accidental)
- No redundant API calls (cache or batch where appropriate)
- No repeated validation logic (create reusable validators when the same rule is enforced in 3+ places)
- No duplicate helper logic in test files (extract shared test utilities when the same setup repeats across multiple test suites)

### 7. No Hardcoded Values
- No hardcoded URLs, API endpoints, or hostnames (use env vars)
- No hardcoded credentials, keys, or secrets (use env vars)
- No magic numbers without named constants
- No hardcoded file paths (use configuration or path utilities)
- No hardcoded timeouts/limits (externalize to config)
- No hardcoded error messages (use constants or i18n)
- No hardcoded feature flags (use configuration system)
- No hardcoded tenant/user IDs in business logic

### 8. Type Safety
- No usage of `any` type (use `unknown` or proper types)
- Proper null/undefined handling (optional chaining, nullish coalescing)
- Generic types used appropriately
- Return types explicitly declared for public functions
- No type assertions (`as`) without validation

### 9. Performance
- No memory leaks (cleanup subscriptions, timers, event listeners)
- Proper memoization for expensive computations
- Lazy loading for heavy components/modules
- Efficient data structures for the use case
- No synchronous operations blocking the event loop
- Batch API calls where possible (e.g., single `messages.modify` with multiple label IDs)

### 10. Naming & Readability
- Descriptive variable/function names (no `x`, `temp`, `data`)
- Consistent naming conventions (camelCase, PascalCase)
- No misleading names (function does what name suggests)
- Boolean variables prefixed appropriately (`is`, `has`, `should`)
- No excessive abbreviations
- Code is self-documenting where possible

### 11. API Design
- Consistent response formats across endpoints
- Proper HTTP status codes used
- Input validation at API boundaries
- Proper error response structure
- RESTful conventions followed
- API versioning considered for breaking changes

### 12. Async & Concurrency
- No unhandled promise rejections
- Proper race condition handling
- Concurrent operations use Promise.all where appropriate
- No floating promises (missing await)
- Proper cleanup on component unmount/request abort
- AbortController used for cancellable operations

### 13. Dependency Management
- No unused dependencies in package.json
- No deprecated packages
- Security vulnerabilities addressed (npm audit)
- Peer dependency conflicts resolved
- Dependencies pinned to specific versions where needed

### 14. Environment & Configuration Sync
- Every env var used in `src/config/env.ts` is documented in `.env.example`
- Every env var in `.env.example` is defined in the Zod schema (`src/config/env.ts`)
- Default values match between `.env.example` comments and Zod `.default()` calls
- Conditional requirements are documented (e.g., "only required when LLM_PROVIDER=openai")
- No env vars referenced directly via `process.env` outside of `src/config/env.ts` and `src/lib/logger.ts`
- `docker-compose.yml` service ports/URLs align with `.env.example` defaults
- `Dockerfile` exposes the correct `PORT` matching `.env.example`
- `docs/railway-deployment.md` env var list matches the Zod schema

### 15. Template & Documentation Consistency
- Email templates in `docs/templates/` have all `{{variable}}` placeholders documented in their "Available Variables" table
- Template variable sources match actual database columns and service outputs
- Classification categories in `docs/classification-design.md` match the `EmailCategory` type in `src/types/email.ts`
- Confidence thresholds in docs match the actual thresholds implemented in code
- Sub-types in docs match the template trigger conditions
- Gmail label names in code (`GmailLabel` const) match labels documented in architecture docs
- API endpoint schemas in `docs/api-spec.md` match actual route handler request/response types
- Error handling strategies in `docs/error-handling.md` match actual retry/error class behavior (e.g., `isRetryable` flags)

### 16. Error Messages & UX
- User-friendly error messages (no technical jargon)
- Loading states for async operations
- Empty states handled gracefully
- Graceful degradation when features fail
- Confirmation for destructive actions
- Success feedback for completed actions
- Error boundaries to prevent full app crashes
- Proper form validation with clear feedback

### 17. Model-Fact Claims (live-source rule — applies to YOUR review verdict)
- A finding that a model ID is "fabricated", "hallucinated", "unknown", "not a real model", or "invalid" — or any claim that a model ID *is* or *is not* valid — is INVALID unless you cite a live/authoritative source. Authoritative sources, in order of preference:
  1. A passing `ci/serving-e2e` arm for that exact model (empirical proof — a real completion was served by the real upstream). Serving-e2e green ⇒ the model demonstrably exists and serves.
  2. The live vendor catalog/docs (Anthropic: `GET https://api.anthropic.com/v1/models` or `https://docs.anthropic.com/.../models`; equivalent live endpoint for any other vendor).
  3. The providers SSOT (`internal/providers/providers.yaml` + derived registry) together with the model-id catalog guard allowlist entry (`cmd/lint-model-id-catalog/anthropic_model_allowlist.txt`), which carries a dated live-source citation per entry.
- Your training data has a cutoff. Any model GA'd AFTER that cutoff is absent from your priors and will LOOK fabricated even when it is real. "I don't recognize this model" is a statement about your training date, NOT evidence of fabrication. The in-weights training catalog is NOT authoritative for any model GA'd after your cutoff.
- If you cannot cite a live check, DEFER — do not block. Raise it as a question ("confirm `<id>` against a live source — serving-e2e or the vendor catalog") and let an authoritative check resolve it. NEVER post a blocking "fabricated model" finding, and NEVER recommend reverting working, serving-e2e-green model support on the strength of an unrecognized name.
- Precedent: `claude-fable-5` was GA 2026-06-09 and real (`ci/serving-e2e`-green, cp#688), yet reviewers repeatedly called it "fabricated" from their in-weights catalog — those calls were wrong. By 2026-06-12 Anthropic had deprecated it (upstream HTTP 404 "Claude Fable 5 is not available. Please use Opus 4.8."); it was removed from `providers.yaml` and its price row expired (controlplane ac60d920, migration 054), and it was the serving-e2e gate that caught it. Both facts came from live sources, not from priors and not from this file. Never treat a model ID named in this checklist as currently valid: check it live.

## Output Format

```markdown
## Code Review Report

### Files Reviewed
- List of files

### Issues Found

#### 🔴 Critical
- [file:line] Description - Recommendation

#### 🟡 Warning
- [file:line] Description - Recommendation

#### 🔵 Suggestions
- [file:line] Description - Recommendation

### Config & Template Sync
- .env.example ↔ env.ts schema: [in sync / N mismatches]
- docs/classification-design.md ↔ src/types/email.ts: [in sync / N mismatches]
- docs/templates/ ↔ template variables: [in sync / N mismatches]
- docs/error-handling.md ↔ src/lib/errors.ts: [in sync / N mismatches]

### Test Coverage
- Files missing tests
- Coverage gaps

### Summary
- Total issues count
- Action items
```
