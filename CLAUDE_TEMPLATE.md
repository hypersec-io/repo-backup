# Universal CLAUDE.md Template for All Projects

Copy everything below this line into your project's CLAUDE.md file:

---

# Claude Code Configuration

## MANDATORY: Recency and Currency Requirements

**⚠️ CRITICAL: This project requires bleeding-edge, up-to-date knowledge**

### Core Requirements for Claude

1. **ALWAYS check current date first** - Use the actual current year, not 2024 or 2023
2. **ALWAYS verify current information** via WebSearch before providing:
   - Platform UI instructions (GitHub, GitLab, AWS, etc.)
   - API/SDK usage patterns
   - Package versions and dependencies
   - Authentication methods (tokens, OAuth, etc.)
   - Cloud service configurations
   - Framework best practices

3. **Strong Recency Bias Required**:
   - Information >6 months old is likely outdated for bleeding-edge work
   - Information >30 days old should be verified for platform UIs
   - Prefer search results from current month/year
   - When searching, use: "{topic} {current_month} {current_year} latest"
   - If multiple sources conflict, prefer the most recent

4. **Deprecation Awareness**:
   - Check for deprecation warnings in all tools/APIs
   - Verify migration paths for deprecated features
   - Alert user to upcoming deprecations (like Bitbucket app passwords)

5. **Version Verification**:
   - Check latest stable versions of all packages
   - Verify compatibility with current ecosystem
   - Don't assume old patterns still work

### Search Pattern Requirements
Instead of generic searches, ALWAYS use dated searches:
- "GitHub personal access token {current_month} {current_year} latest steps"
- "AWS S3 bucket policy {current_year} current best practices"
- "{package_name} {current_month} {current_year} latest version features"
- "{platform} API authentication {current_year} deprecation changes"

### Why This Matters
- Out-of-date guidance wastes engineering time
- Deprecated features break in production
- Security practices evolve rapidly
- Platform UIs change without notice
- API endpoints get versioned/retired
- We work on bleeding-edge technology

### Verification Checklist
Before providing ANY technical guidance:
- [ ] Checked current date and using correct year?
- [ ] Searched for current information if uncertain?
- [ ] Verified no deprecation warnings?
- [ ] Confirmed approach works in current version?
- [ ] Updated documentation if >30 days old?

### Documentation Update Requirements
- When README or docs show dates >30 days old, update them
- Add "Current as of {Month} {Year}" to time-sensitive instructions
- Note deprecation timelines explicitly
- Update command syntax to latest versions

## AWS Best Practices

### S3 Setup Mode Authentication
- **NEVER** use .env credentials for administrative tasks like S3 setup
- Setup mode should use current AWS session or explicitly specified admin profile
- Clear AWS_PROFILE environment variable when not using profiles
- Priority: --setup-profile > explicit --profile > current AWS session

### Error Handling
- Always handle expired AWS sessions gracefully
- Provide specific, actionable error messages for:
  - Expired tokens (with refresh commands)
  - Invalid credentials
  - Access denied (with permission requirements)
- Exit cleanly with SystemExit(1) after showing error

### S3 Bucket Creation
- Always add README.md to newly created buckets documenting:
  - Purpose and structure
  - Configuration settings
  - Restoration instructions
- Use placeholder syntax (<variable>) not {variable} in f-string literals
- Test bucket access after creation (read/write/versioning)

## Git Platform Authentication (August 2025)
- **GitHub**: Classic tokens (ghp_) and fine-grained tokens (github_pat_)
- **GitLab**: Max 365-400 day expiration as of 2025
- **Bitbucket**: App passwords deprecated Sept 2025/June 2026 - use API tokens
- Always note "Current as of {Month} {Year}" in documentation

## File Operations
- Use last commit date for backup filenames, not current date
- Check if backups already exist before re-downloading/creating
- Implement rsync-like behavior (only backup newer/missing)

## Project-Specific Configuration

[Add your project-specific configuration below]

---

END OF UNIVERSAL TEMPLATE