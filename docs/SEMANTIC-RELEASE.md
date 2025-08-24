# Semantic Release Workflow Guide for Claude Code Projects

This guide provides comprehensive instructions for implementing semantic release workflows in Claude Code and VS Code environments across different technology stacks.

## Table of Contents
- [Overview](#overview)
- [Setup in Claude Code](#setup-in-claude-code)
- [VS Code Integration](#vs-code-integration)
- [Technology-Specific Configurations](#technology-specific-configurations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Semantic release automates the entire package release workflow: determining the next version number, generating the changelog, and publishing the release. It follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Key Benefits
- **Automated versioning** based on commit messages
- **Generated changelogs** with proper categorization
- **Consistent releases** across all projects
- **Integration** with CI/CD pipelines
- **Git tag management** with proper formatting

## Setup in Claude Code

### Initial Project Setup

1. **Configure commit message standards:**
```bash
# In any project directory, create or update pyproject.toml, package.json, etc.
# depending on your project type (see technology-specific sections below)

# Ask Claude Code to:
"Please configure semantic release for this project using conventional commits. Set up the configuration file, update the project metadata, and create proper documentation."
```

2. **Install dependencies:**
```bash
# Claude Code can help install the right tools:
"Please install python-semantic-release and configure it for this Python project"
# or
"Please install semantic-release and configure it for this Node.js project"
```

3. **Create conventional commit templates:**
```bash
# Ask Claude Code:
"Please create git commit message templates following conventional commits for this project type"
```

### Using Claude Code for Releases

1. **Check release status:**
```bash
# Ask Claude Code:
"Please check what the next semantic version would be and show me the changelog that would be generated"
```

2. **Create commits with proper format:**
```bash
# Instead of manual commits, ask Claude Code:
"Please commit these changes as a new feature that adds user authentication"
# Claude Code will format as: "feat(auth): add user authentication system"
```

3. **Generate releases:**
```bash
# Ask Claude Code:
"Please create a semantic release for this project and tag it properly"
```

## VS Code Integration

### Extensions Setup

Install these VS Code extensions:
- **Conventional Commits** (`vivaxy.vscode-conventional-commits`)
- **GitLens** (`eamodio.gitlens`) 
- **Semantic Release Helper** (`semantic-release.semantic-release-vscode`)

### VS Code Configuration

Add to your `.vscode/settings.json`:
```json
{
  "conventionalCommits.scopes": [
    "api",
    "cli", 
    "docs",
    "tests",
    "ci",
    "deps"
  ],
  "conventionalCommits.showEditor": true,
  "git.inputValidation": "warn",
  "git.inputValidationLength": 72,
  "gitlens.codeLens.enabled": true,
  "gitlens.currentLine.enabled": true
}
```

### Commit Message Templates

Create `.gitmessage` template:
```
# <type>[optional scope]: <description>
# |<----  Using a Maximum Of 50 Characters  ---->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or other resources
# Example: Github issue #23

# --- COMMIT END ---
# Type can be 
#    feat     (new feature)
#    fix      (bug fix)
#    refactor (refactoring production code)
#    style    (formatting, missing semi colons, etc; no code change)
#    docs     (changes to documentation)
#    test     (adding or refactoring tests; no production code change)
#    chore    (updating build tasks etc; no production code change)
# --------------------
# Remember to
#    Capitalize the subject line
#    Use the imperative mood in the subject line
#    Do not end the subject line with a period
#    Separate subject from body with a blank line
#    Use the body to explain what and why vs. how
#    Can use multiple lines with "-" for bullet points in body
```

## Technology-Specific Configurations

### Python Projects

**Setup:**
```toml
# pyproject.toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.9"

[project.optional-dependencies]
dev = [
    "python-semantic-release>=10.0.0",
    "build>=1.0.0"
]

[tool.semantic_release]
version_variables = [
    "src/__init__.py:__version__",
    "pyproject.toml:version"
]
build_command = "python -m build"
commit_parser = "conventional"
tag_format = "v{version}"
major_on_zero = true

[tool.semantic_release.changelog.default_templates]
changelog_file = "CHANGELOG.md"

[tool.semantic_release.remote]
type = "github"
```

**Commands:**
```bash
# Install
pip install python-semantic-release

# Check next version
semantic-release version --print

# Create release
semantic-release version

# Generate changelog only
semantic-release changelog
```

### Node.js Projects

**Setup:**
```json
{
  "name": "your-project",
  "version": "1.0.0",
  "devDependencies": {
    "semantic-release": "^22.0.0",
    "@semantic-release/git": "^10.0.0",
    "@semantic-release/changelog": "^6.0.0"
  },
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator", 
      "@semantic-release/changelog",
      "@semantic-release/npm",
      "@semantic-release/github",
      [
        "@semantic-release/git",
        {
          "assets": ["CHANGELOG.md", "package.json"],
          "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
        }
      ]
    ]
  }
}
```

**Commands:**
```bash
# Install
npm install --save-dev semantic-release

# Run release
npx semantic-release --dry-run  # Test
npx semantic-release            # Release
```

### Bash/Shell Projects

**Setup (using Node.js semantic-release):**
```json
{
  "name": "bash-project",
  "version": "1.0.0",
  "devDependencies": {
    "semantic-release": "^22.0.0",
    "@semantic-release/exec": "^6.0.0",
    "@semantic-release/git": "^10.0.0"
  },
  "release": {
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      [
        "@semantic-release/exec",
        {
          "prepareCmd": "sed -i 's/VERSION=.*/VERSION=${nextRelease.version}/' version.sh"
        }
      ],
      [
        "@semantic-release/git",
        {
          "assets": ["version.sh", "CHANGELOG.md"],
          "message": "chore(release): ${nextRelease.version}\n\n${nextRelease.notes}"
        }
      ]
    ]
  }
}
```

**Version file (version.sh):**
```bash
#!/bin/bash
VERSION=1.0.0
export VERSION
```

### Helm Charts

**Setup:**
```yaml
# Chart.yaml
apiVersion: v2
name: my-chart
version: 1.0.0
appVersion: "1.0.0"
```

**Semantic release config (.releaserc.yaml):**
```yaml
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - - "@semantic-release/exec"
    - prepareCmd: |
        yq eval '.version = "${nextRelease.version}"' -i Chart.yaml
        yq eval '.appVersion = "${nextRelease.version}"' -i Chart.yaml
  - - "@semantic-release/git"
    - assets:
        - "Chart.yaml"
        - "CHANGELOG.md"
      message: "chore(release): ${nextRelease.version}\n\n${nextRelease.notes}"
```

### Terraform Modules

**Setup:**
```hcl
# version.tf
terraform {
  required_version = ">= 1.0"
}

# outputs.tf
output "module_version" {
  value = "1.0.0"
}
```

**Semantic release config:**
```json
{
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/exec", 
      {
        "prepareCmd": "sed -i 's/value = \".*\"/value = \"${nextRelease.version}\"/' outputs.tf"
      }
    ],
    [
      "@semantic-release/git",
      {
        "assets": ["outputs.tf", "CHANGELOG.md"]
      }
    ]
  ]
}
```

### Kubernetes Manifests

**Setup:**
```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
commonLabels:
  version: v1.0.0
```

**Semantic release config:**
```yaml
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"  
  - - "@semantic-release/exec"
    - prepareCmd: |
        yq eval '.commonLabels.version = "v${nextRelease.version}"' -i kustomization.yaml
  - - "@semantic-release/git"
    - assets:
        - "kustomization.yaml"
        - "CHANGELOG.md"
```

### Vector.dev Configuration

**Setup:**
```toml
# vector.toml
[api]
enabled = true
address = "0.0.0.0:8686"

# Metadata
[sources.version]
type = "demo_logs" 
format = "json"
interval = 1.0
count = 1

[sources.version.log_schema]
version = "1.0.0"
```

**Semantic release config:**
```json
{
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/exec",
      {
        "prepareCmd": "sed -i 's/version = \".*\"/version = \"${nextRelease.version}\"/' vector.toml"
      }
    ],
    [
      "@semantic-release/git", 
      {
        "assets": ["vector.toml", "CHANGELOG.md"]
      }
    ]
  ]
}
```

## Best Practices

### Commit Message Guidelines

1. **Use imperative mood**: "Add feature" not "Added feature"
2. **Be specific**: "Fix user authentication timeout" not "Fix bug"
3. **Include scope when relevant**: "feat(api): add user endpoints"
4. **Use breaking change notation**: "feat!: remove deprecated methods"

### Common Commit Types

- `feat`: New features (minor version bump)
- `fix`: Bug fixes (patch version bump)  
- `docs`: Documentation changes
- `style`: Code style changes (no functional changes)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### Release Strategy

1. **Feature branches**: Use conventional commits on feature branches
2. **Main branch**: Merge to main triggers automatic releases
3. **Hotfixes**: Use `fix` commits for critical bug fixes
4. **Breaking changes**: Always use `BREAKING CHANGE:` footer or `!` notation

### Claude Code Workflow

1. **Start new feature:**
   ```
   "Please create a new feature branch for adding user authentication"
   ```

2. **Make changes with proper commits:**
   ```
   "Please implement user login functionality and commit it with a proper semantic commit message"
   ```

3. **Review before merge:**
   ```
   "Please review my changes and check what semantic version this would create"
   ```

4. **Create release:**
   ```
   "Please merge this to main and create a semantic release"
   ```

### VS Code Workflow  

1. **Use Conventional Commits extension** for guided commit creation
2. **Configure Git hooks** to validate commit messages
3. **Set up branch protection** requiring conventional commits
4. **Use GitLens** to view version history and releases

## Troubleshooting

### Common Issues

**"No new version to release"**
- Check if commits since last release follow conventional format
- Ensure commits are reachable from release branch

**"Reference does not exist"**
- Initialize git repository: `git init && git add . && git commit -m "feat: initial commit"`
- Push to remote repository

**"Token value is missing"**  
- Set `GITHUB_TOKEN` or appropriate VCS token
- Configure token in CI/CD environment

**Version not updating in files**
- Check `version_variables` configuration
- Ensure file paths are correct
- Verify file write permissions

### Debug Commands

```bash
# Python projects
semantic-release version --print  # Check next version
semantic-release version --no-push --no-tag  # Local test

# Node.js projects  
npx semantic-release --dry-run  # Test configuration
npx semantic-release --debug    # Verbose output
```

### Getting Help in Claude Code

Ask Claude Code specific questions:
- "Why is my semantic release not detecting any changes?"
- "Please fix my semantic release configuration for this Python project"
- "Help me create a proper conventional commit for this bug fix"
- "Please set up semantic release CI/CD integration for GitHub Actions"

## Integration with CI/CD

### GitHub Actions

```yaml
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: actions/setup-python@v4  # or setup-node@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: pip install python-semantic-release
        
      - name: Create release
        run: semantic-release version
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This workflow ensures consistent, automated releases across all your projects while maintaining proper version control and changelog management.