# Release Quick Start Guide

## Prerequisites

- Git repository with the release work merged to the branch you ship from (typically `main`).
- Clean working directory for the commit that will receive the tag (no uncommitted changes you care about losing).

## Cut a new release

### 1. Pick a version (SemVer)

Use [semantic versioning](https://semver.org/): `vMAJOR.MINOR.PATCH` (for example `v1.2.3`). The leading `v` is required so GitHub Actions treats the push as a release tag (see workflow `tags: "v*"`).

### 2. (Optional) Bump `__version__` in code

Runtime code reads the version from `app/__init__.py`:

```bash
grep __version__ app/__init__.py
```

If you keep this in sync with tags, update `__version__`, commit, and push that commit before tagging.

### 3. Tag the release commit

From the commit you want to ship (usually the tip of `main` after your release PR is merged):

```bash
git checkout main
git pull origin main

# Example: first release or next patch
git tag -a v0.1.0 -m "Initial release with CAD conversion API"
# or
git tag -a v1.0.1 -m "Fix bug in STL converter"
```

Use `git tag -a` so the tag has an explicit message; plain `git tag v1.0.0` works but is lightweight only.

### 4. Push the tag

```bash
git push origin main
git push origin v0.1.0
```

Or push branch and all tags:

```bash
git push origin main --tags
```

Pushing a `v*` tag triggers the **Docker Build and Push** workflow: it builds and pushes images to GHCR and the **release** job creates a GitHub release (with generated notes).

### 5. Verify

- **Actions**: confirm the workflow run for the tag succeeded.
- **Packages / container**: image tags should include the semver from the tag.
- **Releases**: `https://github.com/<owner>/<repo>/releases`

## Useful Git commands

```bash
# Latest tag
git describe --tags --abbrev=0

# All tags
git tag -l

# Version in Python package
grep __version__ app/__init__.py
```

## Troubleshooting

### Working directory is not clean

```bash
git status
git add -A && git commit -m "Your message"
# or
git stash
```

### Tag already exists (local)

```bash
git tag -d v0.1.0
```

### Tag already exists (remote)

```bash
git push origin --delete v0.1.0
```

Only delete remote tags if you are sure no one depends on that release.

### Fix a bad release

Publish a **new** patch tag from a fixed commit (do not rewrite public tags unless your team agrees).

## More information

- Workflow: `.github/workflows/docker-build.yml` (build, push, and GitHub release on `v*` tags).
- [Semantic versioning](https://semver.org/)
