# Development Configuration Notes

## CRITICAL: Public Repository Requirements - COMPLETED
**PUBLIC REPOSITORY**: This project has been successfully prepared for public release.
- **COMPLETED** - All AI/LLM references removed from code, comments, and documentation
- **COMPLETED** - All code and documentation written as professional human-developed software
- **COMPLETED** - All sensitive tokens secured and removed from committed files
- **COMPLETED** - Professional standards maintained throughout codebase

## PROJECT STATUS: PRODUCTION READY
**Final Version**: 1.2.1 (August 25, 2025)
**Repository**: https://github.com/hypersec-io/infra-repo-backup.git
**Status**: Ready for public release and enterprise deployment

## CRITICAL: Always Use Current Information
**RECENCY REQUIREMENT**: This project requires bleeding-edge, up-to-date knowledge. 
- **ALWAYS** use WebSearch to verify current information before providing guidance
- **ALWAYS** check the current date and use the current year (not 2024 or older)
- **Platform UIs change frequently** - if instructions are >30 days old, verify them
- **Deprecated features cause problems** - always check for deprecation notices
- **Token/API changes are common** - verify authentication methods are still current
- When documentation in README shows a date >1 month old, update it with current info
- Prioritize 2025 search results over older information
- If uncertain about current state, explicitly search for "{topic} {current_month} 2025 latest"

## Important Paths
- **Working directory**: `/var/tmp/repo-backup` (S3 mode) or `local_path/tmp/repo-backup` (local mode)
- **Local backup path**: `/mnt/hypersec/repo-backup`
- **Log files**: `./logs/repo-backup.log`
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

## Semantic Release Configuration
- **VERSION file pattern**: Use `VERSION:{version}` not `VERSION:version` in pyproject.toml
- **Configuration precedence**: CLI args > ENV vars > .env file > defaults
- **Test releases**: Always use `python -m semantic_release version --noop` before production
- **Commit format**: `type(scope): description` (e.g., `feat(auth): add user login`)
- **Version sync**: VERSION file, pyproject.toml, and src/__init__.py are kept in sync
- **Conventional commits**: feat (minor), fix (patch), BREAKING CHANGE (major)

## Project Path Management
- **Always detect project root** using `git rev-parse --show-toplevel` on startup
- **Use pushd/popd** instead of `cd` for safe directory navigation
- **Validate paths** before operations to prevent errors
- **Relative paths**: Use paths relative to project root for portability
- **Error handling**: Handle path detection failures gracefully with clear messages

## Bitbucket Platform Limitations
- **Workspace-scoped tokens**: Unlike GitHub/GitLab, Bitbucket tokens access ONE workspace only
- **Cannot discover workspaces**: Must specify `BITBUCKET_WORKSPACE` for workspace tokens
- **Different architecture**: GitHub has `read:org`, GitLab has group discovery, Bitbucket is workspace-specific
- **This is a platform limitation, not a tool limitation**

## PROJECT COMPLETION SUMMARY
**Total Repositories Successfully Backed Up**: 195
- GitHub: 24 repositories (2 organizations)
- GitLab: 131 repositories (hypersec-repo group)
- Bitbucket: 40 repositories (hs26123228 workspace)

**Key Technical Achievements**:
- Multi-platform authentication (GitHub Classic PAT, GitLab Personal Token, Bitbucket Workspace Token)
- S3 integration with proper IAM, lifecycle policies, and versioning
- Semantic versioning automation with conventional commits
- CI/CD pipeline with separate production and CI tokens
- Professional documentation and security hardening
- Git bundle backup method with full history preservation
- Large repository handling (successfully handled repos with large binaries)

**Security Implementation**:
- Production tokens secured in .env.local (git-ignored)
- CI tokens separated from production tokens
- All sensitive data removed from public repository
- Enhanced .gitignore protection for credentials

**Final Status**: Production-ready enterprise backup solution, fully automated, publicly releasable.