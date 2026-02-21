# Repository Guidelines

## Project Structure & Module Organization
This repository is currently in an early setup state (root is empty except documentation). Keep the top-level clean and introduce a predictable layout as you add code:
- `src/` for application code
- `tests/` for automated tests mirroring `src/`
- `docs/` for design notes, decisions, and operational docs
- `scripts/` for repeatable local/CI utilities
- `assets/` for static files (images, fixtures, sample data)

Example:
`src/reporting/generator.py` -> `tests/reporting/test_generator.py`

## Build, Test, and Development Commands
No build/test task runner is defined yet. Until one is added, use lightweight local checks:
- `Get-ChildItem -Force` to inspect repository contents
- `git status` to verify pending changes before commits
- `rg "TODO|FIXME" .` to find unfinished work quickly

When introducing a runtime/toolchain, add explicit project commands (for example in `Makefile`, `package.json`, or `pyproject.toml`) and document them here.

## Coding Style & Naming Conventions
- Use UTF-8 text files and 4-space indentation for source code.
- Use descriptive names:
  - modules/files: `snake_case`
  - classes/types: `PascalCase`
  - functions/variables: `snake_case`
- Keep functions small and single-purpose; prefer explicit inputs/outputs.
- Run repository formatting/lint tools before opening a PR once they are configured.

## Testing Guidelines
- Place tests under `tests/` with names like `test_<feature>.py`, `*.spec.ts`, or equivalent for the chosen stack.
- Cover happy path, edge cases, and one failure path for each new feature.
- Add regression tests for bug fixes.
- If tests are missing for a change, explain why in the PR description.

## Commit & Pull Request Guidelines
No commit history is available yet, so use Conventional Commits from now on:
- `feat: add monthly report parser`
- `fix: handle empty input rows`
- `docs: clarify setup steps`

PRs should include:
- clear summary of what changed and why
- linked issue/ticket (if applicable)
- test evidence (command + result)
- screenshots for UI changes
