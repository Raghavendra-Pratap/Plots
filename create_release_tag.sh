#!/bin/bash

# Script to create release tags for testing
# Usage: ./create_release_tag.sh [version] [type]
# Types: stable, test, beta, alpha

VERSION=${1:-"1.0.0"}
TYPE=${2:-"test"}

case $TYPE in
  "stable")
    TAG="v$VERSION"
    echo "Creating stable release tag: $TAG"
    ;;
  "test")
    TAG="v$VERSION"_test
    echo "Creating test release tag: $TAG"
    ;;
  "beta")
    TAG="v$VERSION-beta1"
    echo "Creating beta release tag: $TAG"
    ;;
  "alpha")
    TAG="v$VERSION-alpha1"
    echo "Creating alpha release tag: $TAG"
    ;;
  *)
    echo "Invalid type. Use: stable, test, beta, alpha"
    exit 1
    ;;
esac

echo "Creating and pushing tag: $TAG"
git tag -a "$TAG" -m "Release $TAG - $TYPE release for testing"
git push origin "$TAG"

echo "✅ Tag $TAG created and pushed!"
echo "🚀 This will trigger the release workflow in GitHub Actions"
echo "📋 Check the Actions tab to see the release build progress"
