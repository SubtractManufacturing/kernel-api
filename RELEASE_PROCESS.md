# Release Process Guide

This guide explains how to create and publish releases for the Kernel API project.

## 🏷️ Version Tagging Strategy

We follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and minor improvements

## 📋 Pre-Release Checklist

Before creating a release, ensure:

- [ ] All tests pass locally
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Code is committed and pushed
- [ ] PR is merged to main branch

## 🚀 Creating a Release

### Method 1: Using Python Release Script (Recommended - Cross-Platform)

The Python script works on all platforms (Windows, Linux, Mac):

```bash
# Create a patch release (bug fixes)
python scripts/create_release.py patch "Fix STEP file conversion issue"

# Create a minor release (new features)
python scripts/create_release.py minor "Add support for IGES format"

# Create a major release (breaking changes)
python scripts/create_release.py major "API v2 with breaking changes"

# Default patch release
python scripts/create_release.py
```

#### What the script does:
1. Checks that your working directory is clean
2. Shows current version and calculates new version
3. Displays recent commits since last release
4. Updates version in `app/__init__.py`
5. Creates a git commit for the version bump
6. Creates an annotated git tag
7. Provides instructions for pushing to GitHub

### Method 2: Using Platform-Specific Scripts

#### On Linux/Mac/WSL:
```bash
# Make script executable (first time only)
chmod +x scripts/release.sh

# Create releases
./scripts/release.sh patch "Fix STEP file conversion issue"
./scripts/release.sh minor "Add support for IGES format"
./scripts/release.sh major "API v2 with breaking changes"
```

#### On Windows (PowerShell):
```powershell
# Create releases
.\scripts\release.ps1 -BumpType patch -Message "Fix STEP file conversion issue"
.\scripts\release.ps1 -BumpType minor -Message "Add support for IGES format"
.\scripts\release.ps1 -BumpType major -Message "API v2 with breaking changes"
```

### Method 2: Manual Git Commands

```bash
# 1. Ensure you're on main branch with latest changes
git checkout main
git pull origin main

# 2. Create an annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0: Add GLTF export support"

# 3. Push the tag to trigger GitHub Actions
git push origin v1.0.0
```

### Method 3: GitHub Web Interface

1. Go to your repository on GitHub
2. Click on "Releases" → "Create a new release"
3. Click "Choose a tag" → Enter new tag (e.g., `v1.0.0`)
4. Select target branch (usually `main`)
5. Enter release title and description
6. Click "Publish release"

## 🔄 What Happens After Tagging

When you push a version tag, the GitHub Actions workflow automatically:

1. **Builds** multi-architecture Docker images (amd64, arm64)
2. **Tests** the Docker image with health checks and conversions
3. **Pushes** images to GitHub Container Registry
4. **Creates** a GitHub release with:
   - Docker pull commands
   - Quick start guide
   - Auto-generated changelog
5. **Runs** security scans with Trivy

## 📦 Docker Image Tags

After release, the following Docker tags are available:

```bash
# Latest stable version
docker pull ghcr.io/yourusername/kernel-api:latest

# Specific version
docker pull ghcr.io/yourusername/kernel-api:v1.0.0

# Major.minor version (updates with patches)
docker pull ghcr.io/yourusername/kernel-api:1.0

# Branch-based development versions
docker pull ghcr.io/yourusername/kernel-api:main
docker pull ghcr.io/yourusername/kernel-api:develop
```

## 🏷️ Pre-Release Versions

For beta or release candidate versions:

```bash
# Beta release
git tag -a v1.0.0-beta.1 -m "Beta release for v1.0.0"

# Release candidate
git tag -a v1.0.0-rc.1 -m "Release candidate for v1.0.0"

# Push pre-release tag
git push origin v1.0.0-beta.1
```

## 📝 Release Notes Template

When creating releases, use this template:

```markdown
## 🚀 Kernel API v1.0.0

### ✨ Highlights
- Brief summary of major changes
- Key features or improvements

### 🎯 What's New
- Feature 1: Description
- Feature 2: Description

### 🐛 Bug Fixes
- Fixed issue with STEP file conversion on Windows
- Resolved memory leak in large file processing

### 💥 Breaking Changes (if any)
- API endpoint `/old` renamed to `/new`
- Parameter `oldParam` now required

### 📦 Docker Images
Pull the latest version:
\`\`\`bash
docker pull ghcr.io/yourusername/kernel-api:v1.0.0
\`\`\`

### 📚 Documentation
- [API Reference](./docs/API_REFERENCE.md)
- [Integration Guide](./docs/API_INTEGRATION_GUIDE.md)

### 🙏 Contributors
Thanks to everyone who contributed to this release!
```

## 🔍 Verifying a Release

After creating a release:

1. **Check GitHub Actions**: Ensure the workflow completed successfully
2. **Verify Docker Image**: 
   ```bash
   docker pull ghcr.io/yourusername/kernel-api:v1.0.0
   docker run -p 8000:8000 ghcr.io/yourusername/kernel-api:v1.0.0
   curl http://localhost:8000/api/v1/health
   ```
3. **Check GitHub Release**: Verify the release appears on the releases page
4. **Test the API**: Run integration tests against the new version

## 🚨 Hotfix Process

For urgent fixes to production:

```bash
# 1. Create hotfix from the release tag
git checkout -b hotfix/1.0.1 v1.0.0

# 2. Make the fix
# ... make changes ...

# 3. Commit and tag
git commit -am "Fix critical bug in STEP converter"
git tag -a v1.0.1 -m "Hotfix: Critical STEP converter bug"

# 4. Push branch and tag
git push origin hotfix/1.0.1
git push origin v1.0.1

# 5. Merge back to main
git checkout main
git merge hotfix/1.0.1
git push origin main
```

## 📊 Version History Commands

Useful commands for managing versions:

```bash
# List all tags
git tag -l

# Show details of a specific tag
git show v1.0.0

# Delete a local tag
git tag -d v1.0.0

# Delete a remote tag
git push origin --delete v1.0.0

# Check current version
git describe --tags --abbrev=0

# See commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Compare two versions
git diff v1.0.0..v1.1.0
```

## 🔄 Rollback Process

If a release has issues:

1. **Keep the problematic release** (don't delete for history)
2. **Mark as pre-release** on GitHub if needed
3. **Create a new patch release** with fixes
4. **Update Docker tags** if necessary:
   ```bash
   # Pull the previous stable version
   docker pull ghcr.io/yourusername/kernel-api:v0.9.0
   
   # Retag as latest
   docker tag ghcr.io/yourusername/kernel-api:v0.9.0 \
             ghcr.io/yourusername/kernel-api:latest
   
   # Push the retagged image
   docker push ghcr.io/yourusername/kernel-api:latest
   ```

## 📅 Release Schedule

Recommended release cadence:

- **Patch releases**: As needed for bug fixes
- **Minor releases**: Every 2-4 weeks with new features
- **Major releases**: Quarterly or as needed for breaking changes

## 🤝 Contributing to Releases

If you're a contributor:

1. Update CHANGELOG.md with your changes
2. Ensure tests pass
3. Update documentation if needed
4. Create a PR to main branch
5. Once merged, maintainers will handle the release

## 📞 Support

For release-related issues:
- Check GitHub Actions logs
- Review Docker build output
- Open an issue if problems persist