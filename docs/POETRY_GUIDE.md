# Poetry Usage Guide

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

## Why Poetry?

- **Dependency Resolution**: Automatically resolves and locks dependencies
- **Virtual Environments**: Manages virtual environments automatically
- **Build System**: Modern Python packaging with pyproject.toml
- **Scripts**: Easy-to-use command aliases for common tasks
- **Dev Dependencies**: Separate development dependencies from production

## Installation

If you don't have Poetry installed:

```bash
# Install Poetry (official installer)
curl -sSL https://install.python-poetry.org | python3 -

# Or via pipx (recommended)
pipx install poetry

# Verify installation
poetry --version
```

## Common Commands

### Installing Dependencies

```bash
# Install all dependencies (production + dev)
poetry install

# Install only production dependencies
poetry install --no-dev

# Update dependencies to latest versions
poetry update
```

### Running Commands

```bash
# Run the controller
poetry run bpp-controller

# Run Python directly
poetry run python -m src.controller.main

# Run tests
poetry run pytest

# Run code quality checks
poetry run pre-commit run --all-files

# Sync database
poetry run bpp-sync

# Test MQTT module
poetry run bpp-mqtt-test
```

### Managing Dependencies

```bash
# Add a new dependency
poetry add requests

# Add a development dependency
poetry add --group dev pytest

# Remove a dependency
poetry remove requests

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree
```

### Virtual Environment

```bash
# Show virtual environment info
poetry env info

# Activate the virtual environment
poetry shell

# Deactivate (when inside poetry shell)
exit

# Remove virtual environment
poetry env remove python
```

## Project Structure

### pyproject.toml

This is the main configuration file that defines:

```toml
[tool.poetry]
name = "bpp-supershow-overlay"
version = "0.1.0-alpha"
# ... metadata

[tool.poetry.dependencies]
# Production dependencies
python = "^3.10"
paho-mqtt = "^2.0.0"
# ...

[tool.poetry.group.dev.dependencies]
# Development dependencies
pytest = "^7.4.0"
ruff = "^0.4.3"
# ...

[tool.poetry.scripts]
# Command aliases
bpp-controller = "src.controller.main:main"
bpp-sync = "src.shared.example_usage:main"
# ...

[tool.ruff]
# Ruff linter configuration
# ...
```

### poetry.lock

This file locks exact versions of all dependencies (including transitive ones) for reproducible builds. **Commit this file to git!**

## Scripts

The project defines these convenience scripts in `pyproject.toml`:

| Script | Command | Description |
|--------|---------|-------------|
| `bpp-controller` | `poetry run bpp-controller` | Launch controller GUI |
| `bpp-sync` | `poetry run bpp-sync` | Sync database and images |
| `bpp-mqtt-test` | `poetry run bpp-mqtt-test` | Test MQTT connectivity |

## Pre-commit Hooks

Poetry manages pre-commit as a dev dependency. After installation:

```bash
# Install git hooks
poetry run pre-commit install

# Run manually on all files
poetry run pre-commit run --all-files

# Run on staged files only
poetry run pre-commit run
```

Hooks configured:
- **Ruff**: Linting and formatting (replaces black + flake8)
- **Xenon**: Code complexity checking
- **Poetry check**: Validates pyproject.toml

## Dependency Version Constraints

Poetry uses semantic versioning constraints:

- `^2.0.0` - Compatible with 2.0.0 (allows 2.x.x, not 3.0.0)
- `~2.0.0` - Approximately 2.0.0 (allows 2.0.x, not 2.1.0)
- `>=2.0.0` - Greater than or equal to 2.0.0
- `2.0.0` - Exact version

Example:
```toml
paho-mqtt = "^2.0.0"  # Allows 2.0.0, 2.1.0, 2.9.9, but not 3.0.0
```

## Exporting Dependencies

If you need a requirements.txt:

```bash
# Export production dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Export with dev dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

## Configuration

Poetry settings are stored in `~/.config/pypoetry/config.toml`.

Useful settings:

```bash
# Use in-project .venv directory
poetry config virtualenvs.in-project true

# Show what's configured
poetry config --list
```

## Troubleshooting

### "Poetry not found"
```bash
# Add Poetry to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Clear cache
```bash
poetry cache clear pypi --all
```

### Lock file out of sync
```bash
poetry lock --no-update
```

### Dependency conflicts
```bash
# Show why a package is required
poetry show <package>

# Update lock file
poetry update

# Reinstall everything
poetry install --remove-untracked
```

## Migration from requirements.txt

The original `requirements.txt` has been replaced by `pyproject.toml`. All dependencies are now managed by Poetry:

**Before (pip):**
```bash
pip install -r requirements.txt
python -m src.controller.main
```

**After (Poetry):**
```bash
poetry install
poetry run bpp-controller
```

## CI/CD Integration

For GitHub Actions or other CI:

```yaml
- name: Install Poetry
  run: pipx install poetry

- name: Install dependencies
  run: poetry install

- name: Run tests
  run: poetry run pytest

- name: Run linting
  run: poetry run pre-commit run --all-files
```

## Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Commands](https://python-poetry.org/docs/cli/)
- [Dependency Specification](https://python-poetry.org/docs/dependency-specification/)
- [pyproject.toml Reference](https://python-poetry.org/docs/pyproject/)
