# Deployment rules

## Pre-release checklist (always)

1. Run tests locally — must all pass:

```bash
uv run pytest
```

Coverage must stay above 80%. If it drops, fix before proceeding.

2. Bump version in **both**:
   - `src/fauxdata/__init__.py` → `__version__ = "X.Y.Z"`
   - `pyproject.toml` → `version = "X.Y.Z"`

3. Update `LOG.md` with a summary of changes under a new date heading.

---

## GitHub release (tag + release notes)

```bash
# Create and push annotated tag
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

Then create a GitHub release via `gh`:

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes "$(cat <<'EOF'
## What's new

- Short bullet list of user-facing changes
- Include new fields, commands, bug fixes

## Breaking changes

- List any breaking changes here (or remove section if none)

## Installation

\`\`\`bash
pip install fauxdata-cli==X.Y.Z
\`\`\`

Full changelog: https://github.com/aborruso/fauxdata/commits/vX.Y.Z
EOF
)"
```

Release notes style: **concise, nerd-friendly, technical**. List the actual changes with enough detail that a developer understands what changed and why.

---

## PyPI publish (via twine)

```bash
# Build
uv build

# Check the dist
twine check dist/*

# Publish
twine upload dist/*
```

Requires `~/.pypirc` configured with PyPI token, or set `TWINE_USERNAME`/`TWINE_PASSWORD` env vars.

---

## Order of operations

```
uv run pytest          # must pass 100%
bump version           # __init__.py + pyproject.toml
update LOG.md
git commit + git push
git tag + git push tag
gh release create      # with release notes
uv build
twine check dist/*
twine upload dist/*
```

Never publish to PyPI without a corresponding GitHub release.
