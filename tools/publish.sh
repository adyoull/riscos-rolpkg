#!/bin/bash
# publish.sh SITE: puts SITE (pool/ and dists/, from build.sh and
# index.py) on the gh-pages branch, which GitHub Pages serves at
# https://adyoull.github.io/riscos-rolpkg/. Old versions stay in pool/,
# so that an update can be rolled back. Run from the repository.
#
# Copyright (c) 2026 Andrew Youll. MIT licence (see LICENSE).
set -euo pipefail
site=$(cd "$1" && pwd)
repo=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
git -C "$repo" worktree add -q --detach "$work"
cd "$work"
git checkout -q --orphan gh-pages-new
git rm -rq --cached . >/dev/null 2>&1 || true
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$site"/. .
cp "$repo/keys/riscos-rolpkg.asc" .
cp "$repo/riscos-rolpkg.sources" .
touch .nojekyll
git add -A
git commit -qm "Repository of $(date -u +%Y-%m-%d)"
git branch -f gh-pages
cd "$repo"
git worktree remove --force "$work"
git branch -D gh-pages-new >/dev/null 2>&1 || true
git push -f origin gh-pages || echo "publish.sh: the push failed: gh-pages is ready locally"
