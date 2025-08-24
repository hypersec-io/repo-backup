# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enterprise repository backup tool for GitHub, GitLab, and Bitbucket
- Local filesystem backup with git bundles and tar.gz archives
- AWS S3 backup with encryption and lifecycle management
- Parallel processing for efficient backups
- Pattern matching (exact, glob, regex) for repository selection
- LFS support for large file repositories
- Test mode for integration testing with smallest repository
- Professional logging with structured output
- Installation script for system-wide deployment
- Comprehensive test suite with pytest

### Features
- **Multi-platform support**: GitHub, GitLab, Bitbucket integration
- **Dual backup modes**: Local filesystem and AWS S3 storage
- **Smart filtering**: Corporate repos only, exclude forks and personal
- **Professional security**: AWS IAM roles, S3 encryption, lifecycle policies
- **High performance**: Parallel processing with configurable workers
- **Flexible selection**: Repository patterns, file-based lists, test mode
- **Rich CLI**: Progress bars, colored output, detailed logging
- **Easy deployment**: System installer with proper isolation

### Technical Details
- Python 3.9+ requirement
- UV package manager support
- Dataclass-based repository modeling
- ThreadPoolExecutor for parallel operations
- Git LFS support for large files
- Empty repository handling
- Working directory management
- Comprehensive error handling

---

*This changelog is automatically generated using semantic-release*
