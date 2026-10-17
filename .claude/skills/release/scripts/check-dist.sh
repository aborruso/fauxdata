#!/usr/bin/env bash
# Check dist/ before uploading to PyPI. Usage: check-dist.sh X.Y.Z
set -euo pipefail
ver="${1:?usage: check-dist.sh X.Y.Z}"
cd "$(git rev-parse --show-toplevel)"

sdist="dist/fauxdata_cli-${ver}.tar.gz"
wheel="dist/fauxdata_cli-${ver}-py3-none-any.whl"
[[ -f $sdist && -f $wheel ]] || { echo "FAIL: missing $sdist or $wheel"; ls dist/ 2>/dev/null; exit 1; }

extra=$(ls dist/ | grep -v -e "^fauxdata_cli-${ver}.tar.gz$" -e "^fauxdata_cli-${ver}-py3-none-any.whl$" || true)
[[ -z $extra ]] || { echo "FAIL: other files in dist/ (twine would upload them too):"; echo "$extra"; exit 1; }

# sdist: only the whitelist in pyproject.toml (only-include) plus files hatch always adds
bad=$(tar tzf "$sdist" | sed "s#^fauxdata_cli-${ver}/##" \
  | grep -v -E '^$|^(src|tests|schemas)/|^(README\.md|LICENSE|pyproject\.toml|PKG-INFO|\.gitignore)$' || true)
[[ -z $bad ]] || { echo "FAIL: unexpected files in sdist:"; echo "$bad"; exit 1; }

meta=$(unzip -p "$wheel" '*/METADATA')
grep -qx "Version: ${ver}" <<<"$meta" || { echo "FAIL: wheel METADATA version is not ${ver}"; exit 1; }
grep '^Requires-Dist: pointblank' <<<"$meta"

echo "OK: dist/ ready for ${ver}"
