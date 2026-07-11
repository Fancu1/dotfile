# Development Protocol

## Identity & Communication

- Respond in the same language I use (Chinese or English)
- Be concise and direct. No filler, no pleasantries, no trailing summaries
- When unsure, ask directly instead of guessing
- Push back with evidence when you think I'm wrong

## Core Principles

1. **Verify first.** Check official docs and current syntax before coding. Training data goes stale.
2. **Fix root causes.** Never patch symptoms, never modify tests to make them pass, never dismiss failures as pre-existing.
3. **Minimal changes.** Don't refactor, add features, or "improve" code beyond what was asked.
4. **Match existing style.** Follow the repository's patterns, even if they differ from your preferences.
5. **No breadcrumbs.** If you delete or move code, don't leave "// moved to X" comments. Just remove it.
6. **Evergreen naming.** Never name things "new", "improved", "enhanced", or "v2". What's new today is old tomorrow.

## Decision Framework

### Green - Do It (proceed immediately)
- Fix lint errors, type errors, failing tests
- Implement single functions with clear specs
- Fix typos, formatting, missing imports
- Single-file refactors for readability

### Yellow - Propose First (explain approach, then proceed)
- Changes affecting multiple files or modules
- New features or significant functionality
- API or interface modifications
- Adding new dependencies

### Red - Always Ask
- Rewriting existing working code from scratch
- Changing core business logic
- Security-related modifications
- Anything that could cause data loss
- Destructive git operations

## Language: Go

- Handle all errors explicitly; never silently ignore
- Use `errors.Is`/`errors.As`, not string comparison
- `context.Context` as first parameter
- Interfaces defined at the consumer, not the implementor
- Don't edit `gen/` directories; use `go generate`
- Prefix commands with `CGO_ENABLED=1` when SQLite or race detection is needed
- Table-driven tests as default test pattern
- Use `golangci-lint` for linting

## Language: Python

- **Virtual env priority:** If a pyenv virtualenv already exists in the project (check `.python-version` or `pyenv local`), use it directly. Only fall back to `uv` when no existing venv is present. Never install packages directly into the host system Python.
- Use `pyproject.toml` for project config. Avoid bare `requirements.txt` or Poetry unless the project already uses them.
- Type hints everywhere; use `pydantic` for data modeling, not bare dicts
- Use `ruff` for linting and formatting
- Prefer `pathlib` over `os.path`

## Language: TypeScript

- `strict: true` always
- Never use `any`; never use `as` type assertions unless absolutely necessary
- Model real shapes with proper types
- React components: small, focused, composable. Composition over inheritance
- Prefer modern browser APIs; no unnecessary polyfills

## Browser Automation

- **Prefer agent-browser** as the primary tool for browser control
- Playwright MCP as secondary option
- Chrome DevTools MCP for debugging and inspection
- Always take screenshots before and after critical operations to verify state
- Use explicit wait conditions (element visibility, network idle), never `sleep`

## Testing

- Prefer integration tests and e2e tests over unit tests
- Avoid mocks when real calls are practical; mocks hide real bugs
- Go: table-driven tests; Python: pytest; TypeScript: vitest or the repo's existing runner
- Run only affected tests, not the full suite, unless asked
- Never add tests just to increase coverage numbers

## Tools & Workflow

- **Git:** Use `glab` for GitLab repos, `gh` for GitHub repos. Never raw API calls when CLI works.
- **Debugging:** CLI-first. Use `dlv` (Go), `pdb`/`ipdb` (Python), browser DevTools Protocol. Prefer CLI tools over IDE debuggers.
- **Search:** Use `rg` for code search, `jq` for JSON processing
- **Docs lookup:** Context7 MCP for library docs, then web search as fallback
- **MCP priority:** Use available MCP tools (Jenkins, Jira, Playwright, etc.) before falling back to bash scripts

## Git Hygiene

- Never use `--no-verify` when committing
- Never force push to main/master
- Conventional commits: feat, fix, docs, refactor, test, chore
- Non-interactive git commands only: `git --no-pager diff`, `git diff | cat`
- Treat dirty working tree as intentional; never revert changes you didn't make

## Forbidden

- `--no-verify` or `--no-hooks` on git commands
- Throwing away old implementation to rewrite without explicit permission
- Leaving "// moved to X" or "// removed" comments
- Adding mock mode for testing
- Using `any`, `unknown`, or `interface{}` as escape hatches
- Creating new files when editing existing ones would work
- Silent error swallowing or catch-all exception handlers

