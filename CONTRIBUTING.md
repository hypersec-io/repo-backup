# Contributing to repo-backup

Thank you for your interest in contributing to repo-backup! This document outlines the development process and standards for this project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/hypersec-io/infra-repo-backup.git
cd infra-repo-backup
```

2. Install development dependencies:
```bash
uv sync --extra dev --extra test
```

3. Run tests to verify setup:
```bash
uv run pytest tests/ -v
```

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature (triggers MINOR version bump)
- **fix**: A bug fix (triggers PATCH version bump)
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Breaking Changes

For breaking changes, add `!` after the type or add `BREAKING CHANGE:` in the footer:

```bash
feat!: remove deprecated backup methods

BREAKING CHANGE: The legacy backup methods have been removed. 
Use the new unified backup API instead.
```

### Examples

```bash
# Feature addition
feat(cli): add --test option for integration testing

# Bug fix
fix(s3): handle empty repositories correctly

# Breaking change
feat(api)!: restructure backup configuration format

# Documentation
docs: update installation instructions

# Performance improvement
perf(backup): optimize parallel repository processing

# Test addition
test: add integration tests for --test mode
```

### Scopes

Common scopes for this project:
- `cli`: Command-line interface changes
- `github`: GitHub platform integration
- `gitlab`: GitLab platform integration  
- `bitbucket`: Bitbucket platform integration
- `s3`: AWS S3 integration
- `local`: Local backup functionality
- `api`: Core API changes
- `tests`: Test-related changes
- `docs`: Documentation changes

## Pull Request Process

1. Create a feature branch from `main`:
```bash
git checkout -b feat/your-feature-name
```

2. Make your changes following the coding standards
3. Add tests for new functionality
4. Ensure all tests pass:
```bash
uv run pytest tests/ -v
```

5. Commit your changes using conventional commits
6. Push your branch and create a pull request

## Testing

### Unit Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_repository_backup.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Integration Tests
```bash
# Test with real repositories (requires .env configuration)
uv run repo-backup local /tmp/test-backup --test

# Test different platform combinations
uv run repo-backup local /tmp/test --test --platform github
```

## Release Process

This project uses automated semantic versioning:

1. Commits are analyzed for semantic meaning
2. Version numbers are automatically determined
3. Changelog is automatically generated
4. Git tags are created automatically

### Creating a Release

Releases happen automatically when commits are pushed to the `main` branch. To create a release:

1. Ensure your commits follow conventional commit format
2. Merge pull request to `main` branch
3. The CI will automatically:
   - Analyze commits since last release
   - Determine the next version number
   - Update CHANGELOG.md
   - Create and push a git tag
   - Create a GitHub release

### Manual Release (if needed)

```bash
# Dry run to see what would be released
uv run semantic-release version --noop

# Create a release
uv run semantic-release version
```

## Code Standards

### Python Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes
- Keep functions focused and modular

### Error Handling
- Use structured logging with appropriate levels
- Handle exceptions gracefully with meaningful error messages
- Return boolean success indicators from backup operations

### Testing Standards
- Write tests for new features and bug fixes
- Use descriptive test names that explain what is being tested
- Mock external dependencies (git operations, API calls)
- Test both success and failure scenarios

## Documentation

- Update README.md for user-facing changes
- Update CONTRIBUTING.md for development process changes
- Add docstrings to new functions and classes
- Update configuration examples when adding new options

## Questions or Problems?

- Check existing [issues](https://github.com/hypersec-io/infra-repo-backup/issues)
- Create a new issue for bugs or feature requests
- Follow the conventional commit format for all contributions

Thank you for contributing to repo-backup! 🚀