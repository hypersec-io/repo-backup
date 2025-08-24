# Claude Code Universal Configuration

## MANDATORY: Recency and Currency Requirements

**THIS SECTION MUST BE IN ALL PROJECT CLAUDE.MD FILES**

### Critical Instructions for Claude
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

### Example Search Patterns
Instead of generic searches, use:
- "GitHub personal access token August 2025 latest steps"
- "AWS S3 bucket policy 2025 current best practices"
- "Python uv package manager August 2025 features"
- "Bitbucket API authentication 2025 deprecation app password"

### Why This Matters
- Out-of-date guidance wastes engineering time
- Deprecated features break in production
- Security practices evolve rapidly
- Platform UIs change without notice
- API endpoints get versioned/retired

### Verification Checklist
Before providing any technical guidance:
- [ ] Checked current date and using correct year?
- [ ] Searched for current information if uncertain?
- [ ] Verified no deprecation warnings?
- [ ] Confirmed approach works in current version?
- [ ] Updated documentation if >30 days old?

---
*Add project-specific configuration below this line*