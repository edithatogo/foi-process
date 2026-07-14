#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${TARGET_REPO:=edithatogo/foi-process}"
APPLY=false
case "${1:-}" in
  --apply) APPLY=true ;;
  ""|--dry-run) ;;
  *) echo "usage: $0 [--dry-run|--apply]" >&2; exit 2 ;;
esac

shopt -s nullglob
files=("$ROOT"/github/issues/*.md)
if ((${#files[@]} == 0)); then
  echo "no issue bodies found under $ROOT/github/issues" >&2
  exit 1
fi
for file in "${files[@]}"; do
  title=$(sed -n '1s/^# //p' "$file")
  [[ -n "$title" ]] || { echo "missing level-1 title in $file" >&2; exit 1; }
  cmd=(gh issue create --repo "$TARGET_REPO" --title "$title" --body-file "$file" --label track)
  if $APPLY; then
    "${cmd[@]}"
  else
    printf 'DRY RUN: '
    printf '%q ' "${cmd[@]}"
    echo
  fi
done
