#!/bin/bash
# Initialize Git repository
set -e

if [[ ! -d .git ]]; then
  git init
  echo "Git repository initialized."
else
  echo "Git repository already exists."
fi
