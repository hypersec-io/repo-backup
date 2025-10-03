# repo-backup

Enterprise repository backup tool for GitHub, GitLab, and Bitbucket

[![semantic-release: conventional](https://img.shields.io/badge/semantic--release-conventional-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Enterprise repository backup tool that syncs corporate Git repositories from GitHub, GitLab, and Bitbucket to local storage or AWS S3.

## Features

- **Multi-Platform Support**: Backup repositories from GitHub, GitLab, and Bitbucket
- **Corporate Repository Focus**: Automatically excludes personal repositories (configurable)
- **Direct S3 Upload**: Streams repositories directly to S3 without storing locally
- **Multiple Backup Methods**: 
  - Git bundle format (recommended) - preserves full git history
  - Tar.gz archive format
- **Parallel Processing**: Backup multiple repositories simultaneously
- **Filtering**: Include/exclude repositories based on name patterns
- **Multiple Accounts**: Support for multiple accounts per platform
- **Progress Tracking**: Visual progress bars and detailed logging

## Prerequisites

- Python 3.9+
- Git installed and configured
- Access tokens for your git platforms
- Optional: AWS account with S3 bucket for cloud storage

## Quick Install

**System-wide installation (recommended):**
```bash
# Download and install system-wide
sudo python3 install.py

# Test the installation
repo-backup --help
```

**Development installation:**
```bash
# Clone and setup development environment
git clone https://github.com/hypersec-io/infra-repo-backup.git
cd infra-repo-backup
uv sync

# Test functionality
uv run repo-backup local /tmp/test-backup --test
```

## Initial Setup

### Step 1: S3 Bucket Setup (For S3 Backups)

**NOTE: See [AWS.md](AWS.md) for comprehensive AWS configuration guide**

The setup process requires specific AWS permissions to create infrastructure (S3 bucket, IAM user, policies). This does **NOT** require AWS administrator access - only permissions to create S3 buckets and IAM users.

For detailed information, see:
- [AWS.md - For Cloud Administrators](AWS.md#for-cloud-administrators) - Set up permissions for users
- [AWS.md - Permission Details](AWS.md#permission-details) - Exact permissions required
- [AWS.md - Security Best Practices](AWS.md#security-best-practices) - IAM roles, encryption, MFA

#### Quick Setup

```bash
# Basic setup (uses your current AWS CLI session)
repo-backup s3 --setup

# Setup with specific AWS profile (NOT from .env)
repo-backup s3 --setup --setup-profile admin-profile
# OR
repo-backup s3 --setup --profile admin-profile

# With Glacier for cost-optimized long-term storage
repo-backup s3 --setup --enable-glacier

# Custom bucket name and region
repo-backup s3 --setup --bucket-name my-backup-bucket --region us-east-1
```

**Note:** The `--setup` command uses your AWS credentials (NOT `.env` credentials) to create infrastructure. See [AWS.md - Setup Permissions](AWS.md#setup-permissions-required-once) for details on required permissions.

This automated setup will:
- Create S3 bucket with unique name (or use your custom name)
- Enable versioning for backup history
- Configure encryption (AES256)
- Block all public access
- Set up lifecycle policies (Standard or with Glacier)
- Create dedicated IAM user with minimal permissions
- Configure AWS CLI profile
- Generate `.env` file with all settings
- Test bucket access and permissions

**After setup completes:**
- Note the bucket name, IAM user, and AWS profile displayed
- The `.env` file will be created with S3 configuration
- Add your Git platform tokens to the `.env` file (see below)

### Step 2: Configure Access Tokens

1. Copy the example configuration (if S3 setup didn't create one):
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```bash
# Git Platform Tokens (REQUIRED - see Authentication section for details)
GITHUB_TOKEN=ghp_your_token_here         # Classic PAT with repo, read:org scopes
GITLAB_TOKEN=glpat_your_token_here       # Personal Access Token with read_api, read_repository
BITBUCKET_TOKEN=ATCTT_your_token_here    # Workspace Access Token (workspace-scoped)
BITBUCKET_WORKSPACE=workspace-slug       # Required for workspace tokens

# Backup Destinations (choose one or both)
LOCAL_BACKUP_PATH=/mnt/backups/repo-backup  # For local backups
AWS_S3_BUCKET=repo-backup-123456789  # Auto-filled by S3 setup

# AWS Configuration (auto-filled by S3 setup)
AWS_PROFILE=repo-backup-s3-my-bucket-name
AWS_REGION=us-west-2

# Optional: Performance settings
PARALLEL_WORKERS=5
BACKUP_METHOD=direct  # or 'archive'
```

### Getting Access Tokens

*Note: These instructions are current as of August 2025. Platform interfaces may change - check official documentation if these steps don't match.*

#### GitHub

**Option 1: Personal Access Token (Classic) - Still widely used**
1. Navigate to: **Settings → Developer settings → Personal access tokens → Tokens (classic)**
   - Direct URL: https://github.com/settings/tokens
2. Click **Generate new token → Generate new token (classic)**
3. Set expiration (max 1 year, recommend: 90 days)
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Required for organization repositories)
5. Click **Generate token**
6. Copy immediately - token starts with `ghp_`
7. Store securely - you won't see it again!

**Option 2: Fine-grained Personal Access Token (GitHub's recommended approach)**
1. Navigate to: **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
   - Direct URL: https://github.com/settings/tokens?type=beta
2. Click **Generate new token**
3. Configure:
   - Token name: `repo-backup`
   - Expiration: Up to 1 year
   - Repository access: Select specific repos or "All repositories"
4. Set repository permissions:
   - Contents: Read
   - Metadata: Read (automatically selected)
   - Actions: Read (if backing up workflows)
5. Click **Generate token**
6. Copy the token - starts with `github_pat_`

#### GitLab
1. Navigate to: **User Settings → Access Tokens**
   - Direct URL: https://gitlab.com/-/profile/personal_access_tokens
2. Fill in token details:
   - Token name: `repo-backup`
   - Expiration date: Set as needed
3. Select scopes:
   - `read_repository`
   - `read_api` (for group/project listing)
4. Click **Create personal access token**
5. Copy the token - starts with `glpat-`

#### Bitbucket

**IMPORTANT: Bitbucket Authentication Changes (August 2025)**

Bitbucket uses **workspace-scoped tokens** unlike GitHub and GitLab which provide organization-wide access. This means:
- One token per workspace (cannot access multiple workspaces with a single token)
- Must specify `BITBUCKET_WORKSPACE` in configuration
- Different from other platforms that can discover all accessible organizations

**Workspace Access Tokens (Recommended - Current Method)**
1. Navigate to your workspace settings
2. Click **Access tokens** under **Security**
3. Create token with **Repositories: Read** permission
4. Note: Workspace tokens are a Premium feature
5. Token starts with `ATCTT` prefix
6. In `.env` file configure:
   ```bash
   BITBUCKET_TOKEN=ATCTT_your_workspace_token_here
   BITBUCKET_WORKSPACE=your-workspace-slug
   ```

**App Passwords (Legacy - Being Deprecated)**
1. Navigate to: **Personal Bitbucket settings → App passwords**
   - Direct URL: https://bitbucket.org/account/settings/app-passwords/
2. Click **Create app password**
3. Label: `repo-backup`
4. Select permissions:
   - Account: Read
   - Workspace membership: Read
   - Repositories: Read
5. Click **Create**
6. In `.env` file use:
   ```bash
   BITBUCKET_USERNAME=your-username
   BITBUCKET_TOKEN=your-app-password
   ```

**Why Bitbucket Works Differently:**
Unlike GitHub (with `read:org` scope) and GitLab (with group discovery), Bitbucket's API architecture requires workspace-specific tokens. This is a platform limitation, not a tool limitation.
   - pullrequest:read (optional)
7. Create and copy token (shown only once!)
8. Use with your username as before

**Bitbucket Server/Data Center (self-hosted):**
1. Navigate to: **Profile picture → Manage account → Personal access tokens**
   - URL: `https://your-bitbucket-server/plugins/servlet/access-tokens/manage`
2. Click **Create a token**
3. Token details:
   - Token name: `repo-backup`
   - Expiry: As needed
4. Permissions:
   - Repository: Read
   - Project: Read
5. Click **Create**
6. Copy the HTTP access token
7. In `.env` file:
   ```bash
   BITBUCKET_SERVER_URL=https://your-bitbucket-server
   BITBUCKET_TOKEN=your-token
   ```

**Important Notes:**
- Bitbucket Cloud uses **app passwords** (not tokens like GitHub/GitLab)
- The app password must be combined with your username for authentication
- For Bitbucket Server, use the token directly
- All tokens should have **read-only** permissions for security

## Usage

### Basic Backup Commands

```bash
# Local backup to filesystem
repo-backup local /path/to/backup/directory

# S3 backup (bucket must be configured first)
repo-backup s3

# Both local and S3
repo-backup both /path/to/local/backup
```

### Filtering Options

```bash
# Backup only specific platforms
repo-backup local /backup/dir --platform github
repo-backup local /backup/dir --platform gitlab,bitbucket

# Backup specific repositories
repo-backup local /backup/dir --repos owner/repo1,owner/repo2

# Use pattern matching
repo-backup local /backup/dir --pattern "frontend-*"
repo-backup local /backup/dir --pattern-type regex --pattern ".*-service$"

# Exclude forks and personal repos (default behavior)
repo-backup local /backup/dir --include-forks  # To include forks
```

### List Existing Backups

```bash
# List all local backups
repo-backup local /backup/dir --list

# List S3 backups
repo-backup s3 --list

# List backups from specific platform
repo-backup local /backup/dir --list --platform github
```

### Advanced Options

```bash
# Control parallel processing
repo-backup local /backup/dir --workers 10  # Set worker count
repo-backup local /backup/dir --workers 1   # Disable parallel processing

# Test mode - backup only smallest repo
repo-backup local /backup/dir --test
repo-backup s3 --test

# Archive format instead of bundles
repo-backup local /backup/dir --archive

# Force re-backup even if unchanged
repo-backup local /backup/dir --force

# Verbose logging
repo-backup local /backup/dir --verbose

# Diagnostic commands
repo-backup --health-check           # Test platform connectivity
repo-backup --validate-config        # Verify configuration
repo-backup --verify-backup /path    # Check backup integrity
```

## How It Works

1. **Discovery**: Connects to each configured platform and lists all accessible repositories
2. **Filtering**: 
   - Excludes personal repositories (if configured)
   - Excludes forks (if configured)
   - Applies include/exclude patterns
3. **Backup**: For each repository:
   - Clones the repository with full history (`git clone --mirror`)
   - Creates a git bundle or tar.gz archive
   - Uploads directly to S3 with metadata
   - Cleans up temporary files
4. **Verification**: Reports success/failure statistics

## Backup Format

### Git Bundle (Recommended)
- File format: `repos/{platform}/{owner}/{repo_name}_{timestamp}.bundle`
- Preserves complete git history and all branches
- Can be cloned directly: `git clone repo.bundle restored-repo`

### Archive Format
- File format: `repos/{platform}/{owner}/{repo_name}_{timestamp}.tar.gz`
- Contains the bare git repository
- Extract with: `tar -xzf repo.tar.gz`

## S3 Configuration

**NOTE: For detailed AWS setup instructions, see [AWS.md](AWS.md)**

The tool automatically creates and configures S3 buckets with proper security settings. See the [Initial Setup](#initial-setup) section for quick start, or [AWS.md](AWS.md) for:

- **Administrator Guide**: [Setting up permissions for users](AWS.md#for-cloud-administrators)
- **User Guide**: [Running setup and daily backups](AWS.md#for-backup-tool-users)
- **Security**: [IAM roles, encryption, MFA, cost optimization](AWS.md#security-best-practices)
- **Troubleshooting**: [Common issues and solutions](AWS.md#troubleshooting)

## S3 Structure

```
s3://your-bucket/
├── repos/
│   ├── github/
│   │   ├── organization-name/
│   │   │   ├── repo1_20250825_120000.bundle
│   │   │   └── repo2_20250825_120100.bundle
│   ├── gitlab/
│   │   ├── group-name/
│   │   │   └── project1_20250825_120200.bundle
│   └── bitbucket/
│       └── workspace-name/
│           └── repository1_20250825_120300.bundle
```

## Restoring Backups

### From Git Bundle

#### Method 1: Direct clone from bundle
```bash
# Download bundle from S3 to your root directory
cd /path/to/your/root/directory
aws s3 cp s3://your-bucket/repos/github/org/repo.bundle repo.bundle

# Clone directly from the bundle file
git clone repo.bundle restored-repo

# Enter the restored repository
cd restored-repo

# (Optional) Set the correct remote origin
git remote set-url origin https://github.com/org/repo.git

# Verify the restoration
git log --oneline -5  # Check commit history
git branch -a         # See all branches
git tag -l           # List all tags
```

#### Method 2: Fetch into existing repository
```bash
# Download bundle from S3
aws s3 cp s3://your-bucket/repos/github/org/repo.bundle repo.bundle

# Add bundle as remote to existing repo
git remote add backup repo.bundle
git fetch backup

# Merge or checkout branches as needed
git checkout backup/main
```

### From Archive
```bash
# Download and extract
aws s3 cp s3://your-bucket/repos/github/org/repo.tar.gz repo.tar.gz
tar -xzf repo.tar.gz

# Convert bare repo to normal repo
git clone repo.git restored-repo
```

## Automation

### Using Cron (Linux/Mac)
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/repo-backup && uv run repo-backup s3 --all >> repo-backup.log 2>&1
```

### Using Task Scheduler (Windows)
1. Create a batch file:
```batch
cd C:\path\to\repo-backup
uv run repo-backup s3 --all
```
2. Schedule it in Task Scheduler

### Using GitHub Actions
```yaml
name: Backup Repos
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          uv run repo-backup s3 --all
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Security Best Practices

1. **Never commit credentials** to version control
2. Use **environment variables** for sensitive data:
```bash
export GITHUB_TOKEN=ghp_...
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

3. **Rotate tokens** regularly
4. **AWS Security**: See [AWS.md - Security Best Practices](AWS.md#security-best-practices) for IAM roles, encryption, MFA, and cost optimization

## Troubleshooting

### Authentication Errors
- Verify tokens have correct permissions
- Check token expiration
- Ensure network access to git platforms

### S3 Upload Failures
- See [AWS.md - Troubleshooting](AWS.md#troubleshooting) for detailed AWS issue resolution
- Verify AWS credentials and permissions
- Ensure bucket exists and is accessible

### Large Repository Issues
- Increase timeout values
- Use fewer parallel workers
- Consider backing up large repos separately

### Out of Disk Space
- Tool uses `./.tmp` for temporary files
- Ensure sufficient disk space (2x largest repo size)
- Temporary files are cleaned automatically

## Performance Tips

1. **Parallel Workers**: Adjust based on network and CPU
   - Default: 5 workers
   - High-speed connection: 10-20 workers
   - Limited bandwidth: 2-3 workers

2. **Filtering**: Use patterns to skip unnecessary repos
   - Exclude test/demo repositories
   - Focus on production code

3. **Scheduling**: Run during off-peak hours

4. **Incremental Backups**: Consider implementing incremental backups for very large repositories

## License

Apache License 2.0 - See LICENSE file for details

## Security

**IMPORTANT: Token Security**
- Never commit real tokens to version control
- Use `.env.local` for your actual tokens (automatically ignored by git)
- The `.env` file in the repository contains only placeholder values
- Rotate tokens regularly and use minimal required permissions
- For CI/CD, use separate tokens with limited scope

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify configuration in `.env` file
3. Ensure all prerequisites are installed
4. Review the authentication section above for token setup