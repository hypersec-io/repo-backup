# repo-backup

[![semantic-release: conventional](https://img.shields.io/badge/semantic--release-conventional-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Enterprise repository backup tool that syncs corporate Git repositories from GitHub, GitLab, and Bitbucket to local storage or AWS S3 with professional security and lifecycle management.

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

## Configuration

1. Copy the example configuration:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials and preferences:
```bash
# Required: Platform tokens
GITHUB_TOKEN=ghp_your_token_here
GITLAB_TOKEN=glpat_your_token_here  
BITBUCKET_TOKEN=ATCTT_your_token_here

# Required: Backup destination
LOCAL_BACKUP_PATH=/mnt/backups/repo-backup
AWS_S3_BUCKET=your-backup-bucket

# Optional: Advanced settings
PARALLEL_WORKERS=5
BACKUP_METHOD=direct  # or 'archive'
```

### Getting Access Tokens

#### GitHub
1. Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy the token (starts with `ghp_`)

#### GitLab
1. Go to User Settings → Access Tokens
2. Create token with `read_repository` scope
3. Copy the token (starts with `glpat-`)

#### Bitbucket
**Cloud:**
1. Go to Personal settings → App passwords
2. Create app password with repository read permissions
3. Use your username and app password

**Server/Data Center:**
1. Go to Profile → Manage account → Personal access tokens
2. Create token with repository read permissions

## Usage

### Basic Backup

Run backup for all configured platforms:
```bash
python backup_repos.py
```

### With Custom Config

```bash
python backup_repos.py --config /path/to/config.yaml
```

### List Existing Backups

```bash
# List all backups
python backup_repos.py --list

# List backups from specific platform
python backup_repos.py --list --platform github
```

### Advanced Options

```bash
# Disable parallel processing
python backup_repos.py --parallel false

# Set number of parallel workers
python backup_repos.py --workers 10

# Enable verbose logging
python backup_repos.py --verbose
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

## S3 Structure

```
s3://your-bucket/
├── repos/
│   ├── github/
│   │   ├── organization-name/
│   │   │   ├── repo1_20240101_120000.bundle
│   │   │   └── repo2_20240101_120100.bundle
│   ├── gitlab/
│   │   ├── group-name/
│   │   │   └── project1_20240101_120200.bundle
│   └── bitbucket/
│       └── workspace-name/
│           └── repository1_20240101_120300.bundle
```

## Restoring Backups

### From Git Bundle
```bash
# Download from S3
aws s3 cp s3://your-bucket/repos/github/org/repo.bundle repo.bundle

# Clone from bundle
git clone repo.bundle restored-repo

# Or add as remote to existing repo
git remote add backup repo.bundle
git fetch backup
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
0 2 * * * cd /path/to/repo-backup && ./venv/bin/python backup_repos.py >> backup.log 2>&1
```

### Using Task Scheduler (Windows)
1. Create a batch file:
```batch
cd C:\path\to\repo-backup
venv\Scripts\python.exe backup_repos.py
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
          python backup_repos.py
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
4. Use **IAM roles** when running on EC2
5. **Encrypt** S3 bucket with SSE-S3 or SSE-KMS
6. Enable **versioning** on S3 bucket
7. Set up **lifecycle policies** to manage old backups

## Troubleshooting

### Authentication Errors
- Verify tokens have correct permissions
- Check token expiration
- Ensure network access to git platforms

### S3 Upload Failures
- Verify AWS credentials
- Check S3 bucket permissions
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

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify configuration in `config/config.yaml`
3. Ensure all prerequisites are installed
4. Review S3 setup in [S3.md](S3.md)