#!/bin/bash
# Fork a product into its own GitHub repo
# Usage: bash scripts/fork-product.sh <product-name> <github-repo>
# Example: bash scripts/fork-product.sh content-studio sonoradigitalcorp-H/content-studio

set -e
PRODUCT=$1
REPO=$2

if [ -z "$PRODUCT" ] || [ -z "$REPO" ]; then
  echo "Usage: bash scripts/fork-product.sh <product-name> <owner/repo>"
  echo ""
  echo "Available: content-studio, omnivoice, open-notebook"
  echo ""
  echo "1. Create the repo at https://github.com/new"
  echo "2. Run this script"
  echo "3. Done — the product is in its own repo"
  exit 1
fi

TMPDIR=$(mktemp -d)
echo "→ Clonando producto $PRODUCT..."

cp -r /home/ubuntu/sonora-digital-corp/products/$PRODUCT/* $TMPDIR/
# Add infra files if they exist
[ -f /home/ubuntu/sonora-digital-corp/infra/docker/$PRODUCT/Dockerfile ] && \
  cp /home/ubuntu/sonora-digital-corp/infra/docker/$PRODUCT/Dockerfile $TMPDIR/
[ -f /home/ubuntu/sonora-digital-corp/products/$PRODUCT/docker-compose.yml ] && \
  cp /home/ubuntu/sonora-digital-corp/products/$PRODUCT/docker-compose.yml $TMPDIR/
# Fallback: products docker-compose has the service definition
if [ ! -f $TMPDIR/docker-compose.yml ]; then
  echo "→ Nota: sin docker-compose propio, usa infra/docker-compose.products.yml"
fi

cd $TMPDIR
[ ! -f .gitignore ] && echo "__pycache__/\\n*.pyc\\n.env\\n" > .gitignore
git init && git branch -m main
git config user.email "mystic@sonoradigitalcorp.com"
git config user.name "Mystic AI"
git add -A && git commit -m "init: $PRODUCT standalone" --allow-empty

echo "→ Repositorio listo en $TMPDIR"
echo ""
echo "Para pushear:"
echo "  cd $TMPDIR"
echo "  git remote add origin git@github.com:$REPO.git"
echo "  git push -u origin main"
echo ""
echo "Luego:"
echo "  rm -rf $TMPDIR"
