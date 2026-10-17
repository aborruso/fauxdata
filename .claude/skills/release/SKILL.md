---
name: release
description: Prepare and publish a fauxdata release - version bump, LOG, tests, build, dist check, commit, tag, PyPI upload, GitHub Release in English. Argument - the new version (X.Y.Z).
disable-model-invocation: true
---

# Release fauxdata

`RELEASING.md` is the reference procedure; this skill runs it with the checks that past releases showed are needed. Argument: the new version `X.Y.Z` (if missing, ask; SemVer rules are in `RELEASING.md`).

Chat with the user in Italian. Commit messages, tag message and GitHub Release title and notes in English.

## 1. Preconditions

- On `main`, in sync with `origin/main` (`git fetch` then `git status -sb`). Untracked files are fine: the sdist is built from a whitelist.
- `uv run pytest tests/ -q` all green.
- The tag `vX.Y.Z` does not exist (`git tag -l vX.Y.Z`) and the version is not on PyPI (`https://pypi.org/pypi/fauxdata-cli/X.Y.Z/json` returns 404).

## 2. Prepare (local, reversible)

1. Bump the version in both `pyproject.toml` and `src/fauxdata/__init__.py`, then `uv lock` (the lock file records the package version) → check: `uv run fauxdata --version` prints `X.Y.Z`.
2. `LOG.md`: new dated section on top, `## YYYY-MM-DD — X.Y.Z: <summary>` (Italian, short bullets, each on one line).
3. If the release touches docs, run the `doc-sync-reviewer` agent and fix what it reports.
4. Build: `rm -rf dist && uv build`.
5. Check: `.claude/skills/release/scripts/check-dist.sh X.Y.Z` must print `OK`. It fails on extra files in `dist/`, files outside the sdist whitelist, or a wrong version in the wheel metadata.
6. Commit: `chore: vX.Y.Z — <summary>` with the files from steps 1-2.
7. Draft the GitHub Release notes in English, following the style of the previous release (`gh release view v<previous> --json body --jq .body`): sections such as Highlights, Fixes, Behavior changes, only those that apply. A patch release can be a short list.

## 3. Stop and ask

Show the user: the commit, the `check-dist.sh` output, the draft notes. Publishing is irreversible (a version uploaded to PyPI cannot be uploaded again), so wait for an explicit yes before step 4.

## 4. Publish

1. `git push origin main`
2. `git tag -a vX.Y.Z -m "vX.Y.Z — <summary>"` and `git push origin vX.Y.Z`
3. `twine upload dist/*` (token in `~/.pypirc`)
4. `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <notes file>` (the tag alone does not create the release page)

## 5. Verify and wrap up

- `uvx --refresh --from fauxdata-cli==X.Y.Z fauxdata --version` prints `X.Y.Z` (the package is `fauxdata-cli`, the command is `fauxdata`).
- `uv tool install --reinstall dist/fauxdata_cli-X.Y.Z-py3-none-any.whl` → local `fauxdata --version` prints `X.Y.Z`.
- If the release closes fauxdata issues, comment on each with a link to the release and close it.
- Report to the user: PyPI URL, GitHub Release URL, what was verified.
