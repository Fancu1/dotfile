# PRD: Verify Tooling

## 0. Background and Goal
- Goal: Establish a single, reliable verification entrypoint for all PRDs using make verify.

## 1. Scope
### In scope
- Makefile with make verify (required)
- Optional targets: lint, test, format, typecheck
- Lint/format config aligned with repo tech stack
- Minimal unit/integration test skeleton
- CI pipeline to run make verify
- Local failure reproduction steps

### Out of scope
- Production deployment
- Feature development beyond verification tooling

## 2. Requirements
- Makefile:
  - make verify must run a deterministic set of checks
  - Provide optional targets if applicable: make lint, make test, make format, make typecheck
- Lint/format:
  - Choose tools matching stack
  - Provide config files and minimal rules
- Tests:
  - Minimal tests that pass on a clean repo
  - Include at least one unit test and one integration test where applicable
- CI:
  - Provide a CI pipeline (GitHub Actions or repo standard)
  - Pipeline must run make verify
- Failure handling:
  - Clear steps to reproduce locally

## 3. Acceptance Criteria
- [ ] make verify passes on a minimal scaffold (no app features required)
- [ ] Lint/format tools are configured and runnable
- [ ] Test skeleton exists and passes
- [ ] CI pipeline runs make verify successfully
- [ ] Clear local repro steps documented

## 4. Verification
- Required command: make verify
- Additional commands (if any):

## 5. Dependencies
- None (must be first PRD)
