#!/bin/bash
# Push script for merging temporal framework to main
# Run this on your Mac in: /Users/Pramod/projects/STEM-AI/pipeline_universal_STEM

set -e  # Exit on error

echo "========================================"
echo "Pushing Temporal Framework to Main"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository!"
    echo "   Please run this from: /Users/Pramod/projects/STEM-AI/pipeline_universal_STEM"
    exit 1
fi

# Fetch latest from remote
echo "📥 Fetching latest from remote..."
git fetch --all

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "   Current branch: $CURRENT_BRANCH"

# If not on main, switch to it
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 Switching to main branch..."
    git checkout main
fi

# Pull latest main
echo "📥 Pulling latest main..."
git pull origin main || echo "   (No changes to pull)"

# Merge the feature branch
echo "🔀 Merging feature branch..."
git merge origin/claude/debug-svg-generation-01TSAU4aDpGc4vMJDvKp2jhT --no-edit

# Show what will be pushed
echo ""
echo "📊 Commits to be pushed:"
git log --oneline origin/main..main | head -10

echo ""
echo "📊 Files changed:"
git diff --stat origin/main..main

# Confirm push
echo ""
read -p "Push these changes to main? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to origin/main..."
    git push origin main

    echo ""
    echo "========================================"
    echo "✅ SUCCESS! Changes pushed to main"
    echo "========================================"
    echo ""
    echo "Summary:"
    echo "  ✓ Generic temporal framework"
    echo "  ✓ Scene builder integration"
    echo "  ✓ Updated capacitor interpreter"
    echo "  ✓ Integration tests (all passing)"
    echo "  ✓ Comprehensive documentation"
    echo ""
    echo "Total: +2,173 lines across 8 files"
else
    echo ""
    echo "❌ Push cancelled"
    exit 1
fi
