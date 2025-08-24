# Claude Code Configuration Notes

## Important Paths
- **Working directory**: `/var/tmp/repo-backup` (S3 mode) or `local_path/tmp/repo-backup` (local mode)
- **Local backup path**: `/mnt/hypersec/repo-backup`
- **Log files**: `./logs/backup-repo.log`
- **Config**: `.env` (copy from `.env.example`)

## Testing Commands
- **Lint**: `uv run ruff check src/`
- **Type check**: `uv run mypy src/`
- **Format**: `uv run black src/`

## Repository Filters
- **GitLab**: Set `GITLAB_INCLUDE_GROUPS` to filter groups (e.g., `hypersec-repo`)
- **Bitbucket**: Set `BITBUCKET_INCLUDE_GROUPS` to filter workspaces (e.g., `hs26123228`)
- **GitHub**: Set `GITHUB_INCLUDE_ORGS` to filter organizations (e.g., `hypersec-io,user`)
- Use `user` keyword to include user's personal repositories

## Default Behavior
- Without filters: Includes all accessible repositories (user + all organizations/groups)
- With filters: Only includes specified organizations/groups
- Repository name filters (`--repos`) apply within the org/group scope

## AWS Configuration
- S3 bucket is auto-configured with versioning and lifecycle rules
- Use `--profile` for S3 operations (stored as `AWS_PROFILE` in .env)
- Local mode doesn't need AWS profile

## Backup Methods
- **direct**: Creates git bundles (efficient, preserves full history)
- **archive**: Creates tar.gz archives (larger, includes working tree)

## Error Handling
- Empty repositories (no commits) will fail bundle creation - this is expected
- 97-98% success rate is normal due to empty repos
- LFS repositories are supported with `git lfs fetch --all`

## Release Management
- **IMPORTANT**: Use semantic-release workflow instead of direct git commands
- Use `./scripts/ci` to run CI pipeline before any commits
- Use `./scripts/release` to create semantic releases with conventional commits
- Never use `git add`, `git commit`, `git tag` directly - always use semantic-release
- CI pipeline includes: formatting, linting, testing, security scanning, building
- All changes must pass CI before being committed via semantic-release