#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <repo-dir> <ref> <tag-or-commit> [compare-ref]" >&2
  exit 1
fi

repo_dir=$1
ref=$2
target=$3
compare_ref=${4:-}

echo "== repo =="
echo "$repo_dir"
echo

echo "== describe =="
git -C "$repo_dir" describe --tags --abbrev=0 "$ref" || true
echo

echo "== describe-debug =="
git -C "$repo_dir" describe --debug --tags --abbrev=0 "$ref" || true
echo

echo "== show-ref =="
git -C "$repo_dir" show -s --format='%H%n%P%n%ci%n%s' "$target"
echo

echo "== tag-contains =="
git -C "$repo_dir" tag --contains "$target" || true
echo

echo "== branch-contains =="
git -C "$repo_dir" branch -r --contains "$target" || true
echo

echo "== merge-base-ancestor target->ref =="
if git -C "$repo_dir" merge-base --is-ancestor "$target" "$ref"; then
  echo 0
else
  status=$?
  echo "$status"
fi
echo

if [[ -n "$compare_ref" ]]; then
  echo "== merge-base =="
  git -C "$repo_dir" merge-base "$ref" "$compare_ref"
  echo
fi
