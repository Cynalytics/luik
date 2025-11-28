# Claude Code Guidelines for Luik Project

## Commit Message Format

**IMPORTANT**: Do NOT include Claude Code branding or attribution in commit messages.

### Structure

- Short, descriptive title (imperative mood)
- Keep commit focused on a single feature/change
- If a commit only implements one feature, the title alone is sufficient - don't add extra bullet points
- For multi-part changes, add a blank line followed by bullet points explaining specific changes
- Focus on what and why, not how

### Examples

Single feature (title only):

```
Add SSL/TLS support for API server
```

Multiple related changes (with bullets):

```
Remove TOKEN_SECRET configuration and update environment variables

- Remove TOKEN_SECRET from config and environment examples
- Add LUIK_OUTPUT_URL to environment configuration
- Update pytest workflow with required environment variables
- Update test environment configuration in pyproject.toml
```

## Development Workflow

### Pre-commit Hooks

- All commits must pass pre-commit hooks (ruff, mypy, poetry-check, etc.)
- If hooks modify files (like end-of-file-fixer), amend the commit with those changes
- Never skip hooks unless explicitly requested

**Known Issue: requirements-dev.txt flipping**

- The `poetry export` command is non-deterministic and may flip the order of OR conditions (e.g., `sys_platform == "win32" or platform_system == "Windows"` vs `platform_system == "Windows" or sys_platform == "win32"`)
- This causes the `update-requirements-dev-txt` hook to continuously modify the file even when nothing has changed
- When this happens, use `--no-verify` to skip hooks for that commit:
  ```bash
  git commit --no-verify -m "Your commit message"
  ```
- This is a known Poetry limitation with no configuration fix available

### Testing

- Run pytest with proper environment variables configured
- **IMPORTANT**: Environment variables for tests are ONLY defined in `pyproject.toml` under `[tool.pytest.ini_options]`
- DO NOT duplicate environment variables in GitHub workflow files - pytest will use the config from pyproject.toml

### Code Quality

- Follow ruff linting and formatting standards
- Pass mypy type checking
- No trailing whitespace
- Proper end-of-file newlines
- No private keys or secrets in code

## Project Stack

- **Language**: Python 3.12
- **Package Manager**: Poetry
- **Database**: PostgreSQL (psycopg3)
- **Testing**: pytest
- **Code Quality**: ruff, mypy, pyupgrade
- **CI/CD**: GitHub Actions

## Environment Configuration

Key environment variables:

- `OCTOPOES_API`
- `KATALOGUS_API`
- `SCHEDULER_API`
- `BOEFJE_RUNNER_API`
- `KATALOGUS_DB_URI`
- `API`
- `LUIK_OUTPUT_URL`

**IMPORTANT**: When adding or changing environment variables, update:

1. `.env.example` for documentation
2. `pyproject.toml` test environment under `[tool.pytest.ini_options]`

DO NOT add environment variables to GitHub workflow files - they should only be in pyproject.toml

## Git Workflow

1. Make changes
2. Stage files with `git add`
3. Commit (pre-commit hooks will run automatically)
4. If hooks modify files, amend commit with changes
5. Pull with rebase if needed (`git pull --rebase`)
6. Push to remote

## Code Style

- Keep changes focused and minimal
- Don't over-engineer solutions
- Remove unused code completely (no commented-out code or backwards-compatibility hacks)
- Follow existing patterns in the codebase
