#!/bin/bash
# Common git helper functions
set -e

ensure_clean_working_tree() {
  if [[ -n $(git status --porcelain) ]]; then
    echo "Working tree is not clean. Commit or stash changes first."
    exit 1
  fi
}

get_current_branch() {
  git rev-parse --abbrev-ref HEAD
}
