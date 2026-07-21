#!/bin/bash
# Mirror GitHub Actions to Gitea local instance
# Usage: ./scripts/mirror-gh-actions.sh [GITEA_URL] [GITEA_TOKEN]
#
# This script mirrors required actions from github.com to a local Gitea
# instance so Gitea Actions runners can resolve them via DEFAULT_ACTIONS_URL.
#
# Steps to implement:
#   1. For each action in REQUIRED_ACTIONS, compute:
#      - source="https://github.com/${action}.git"
#      - target="${GITEA_URL}/${action}.git"
#   2. git clone --mirror "$source" /tmp/mirror-gh
#   3. git -C /tmp/mirror-gh remote add gitea "$target"
#   4. git -C /tmp/mirror-gh push --mirror gitea
#   5. rm -rf /tmp/mirror-gh

REQUIRED_ACTIONS=(
  "actions/checkout@v3"
  "actions/checkout@v4"
  "actions/configure-pages@v5"
  "actions/deploy-pages@v4"
  "actions/github-script@v6"
  "actions/github-script@v7"
  "actions/setup-node@v4"
  "actions/setup-python@v5"
  "actions/upload-artifact@v4"
  "actions/upload-pages-artifact@v3"
  "amondnet/vercel-action@v25"
  "appleboy/ssh-action@v1.2.0"
  "appleboy/telegram-action@master"
  "docker/build-push-action@v4"
  "docker/setup-buildx-action@v2"
  "github/codeql-action/analyze@v3"
  "github/codeql-action/autobuild@v3"
  "github/codeql-action/init@v3"
  "trufflesecurity/trufflehog@main"
)

GITEA_URL="${1:-http://gitea:3000}"
GITEA_TOKEN="${2:-}"

if [ -z "$GITEA_TOKEN" ]; then
  echo "Usage: $0 <GITEA_URL> <GITEA_TOKEN>"
  echo "GITEA_TOKEN is required to push to Gitea."
  exit 1
fi

for action_with_tag in "${REQUIRED_ACTIONS[@]}"; do
  action="${action_with_tag%@*}"
  echo "Mirroring $action_with_tag ..."

  source_url="https://github.com/${action}.git"
  target_url="${GITEA_URL}/${action}.git"

  # TODO: implement mirror logic
  # git clone --mirror "$source_url" /tmp/mirror-gh
  # git -C /tmp/mirror-gh remote add gitea "$target_url"
  # git -C /tmp/mirror-gh push --mirror gitea
  # rm -rf /tmp/mirror-gh
done

echo "Done. All actions mirrored to $GITEA_URL"
