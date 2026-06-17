#!/bin/bash
# Create new feature branch
set -e

FEATURE_NUM=$1
FEATURE_NAME=$2

if [[ -z "$FEATURE_NUM" || -z "$FEATURE_NAME" ]]; then
  echo "Usage: $0 <feature-number> <feature-name>"
  exit 1
fi

BRANCH_NAME="${FEATURE_NUM}-${FEATURE_NAME}"
git checkout -b "$BRANCH_NAME"
echo "Created branch: ${BRANCH_NAME}"
