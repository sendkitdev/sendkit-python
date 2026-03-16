#!/bin/bash
set -e

CURRENT=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
MAJOR=$(echo "$CURRENT" | cut -d. -f1)
MINOR=$(echo "$CURRENT" | cut -d. -f2)
PATCH=$(echo "$CURRENT" | cut -d. -f3)
VERSION="$MAJOR.$MINOR.$((PATCH + 1))"

echo "Current version: $CURRENT"
echo "New version: $VERSION"

sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

git add pyproject.toml
git commit -m "bump version to $VERSION"
git push

git tag "$VERSION"
git push origin "$VERSION"

echo "Released $VERSION successfully!"
