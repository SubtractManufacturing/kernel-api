# Release Quick Start Guide

## ✅ Prerequisites
- Git repository with all changes committed
- Clean working directory (no uncommitted changes)

## 🚀 Create Your First Release

### Step 1: Run the Release Script
```bash
# For your first release (v0.1.0)
python scripts/create_release.py minor "Initial release with CAD conversion API"

# The script will:
# 1. Show current version (v0.0.0)
# 2. Show new version (v0.1.0)
# 3. Display recent commits
# 4. Ask for confirmation (type 'y' to proceed)
```

### Step 2: Push to GitHub
After the script creates the tag, push it:
```bash
# Push your code and the new tag
git push origin main --tags

# Or separately:
git push origin main
git push origin v0.1.0
```

### Step 3: GitHub Actions Takes Over
Once pushed, GitHub Actions will automatically:
1. Build Docker images for multiple platforms
2. Run tests to verify the build
3. Push images to GitHub Container Registry
4. Create a GitHub release with:
   - Release notes
   - Docker pull commands
   - Download links

### Step 4: Verify the Release
Check your repository's releases page:
```
https://github.com/yourusername/kernel-api/releases
```

## 📝 Common Release Commands

```bash
# Patch release (v0.1.0 → v0.1.1)
python scripts/create_release.py patch "Fix bug in STL converter"

# Minor release (v0.1.1 → v0.2.0)
python scripts/create_release.py minor "Add support for IGES format"

# Major release (v0.2.0 → v1.0.0)
python scripts/create_release.py major "Production-ready release"
```

## 🔍 Check Current Version
```bash
# See current version tag
git describe --tags --abbrev=0

# See all tags
git tag -l

# See version in code
grep __version__ app/__init__.py
```

## ⚠️ Troubleshooting

### "Working directory is not clean"
```bash
# Check what's uncommitted
git status

# Commit changes
git add -A
git commit -m "Your commit message"

# Or stash temporarily
git stash
```

### Tag already exists
```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag (careful!)
git push origin --delete v0.1.0
```

### Need to undo a release
```bash
# Create a new patch version with the fix
python scripts/create_release.py patch "Revert breaking change"
```

## 📚 More Information
- [Full Release Process Documentation](../RELEASE_PROCESS.md)
- [Changelog](../CHANGELOG.md)
- [Semantic Versioning](https://semver.org/)