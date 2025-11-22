# AuroraAI Troubleshooting Guide

## Common Issues & Fixes

### 1. Assistant Not Responding
**Symptoms:** Long delays or no output.

**Possible Causes & Fixes:**
- Network issue → Check VPN/firewall.
- Expired API key → Run `aurora auth refresh`.
- Large file uploads throttled → Compress or split files.

### 2. Incorrect or Irrelevant Answers
**Symptoms:** Hallucinations, outdated info.

**Fixes:**
- Re-index documentation: `aurora connect ./docs --force`.
- Add explicit context to prompts.
- Enable strict retrieval with: `--retrieval=strict`.

### 3. Authentication Errors
| Code | Meaning | Fix |
|------|---------|------|
| 401 | Invalid token | Re-enter API key |
| 403 | Permission denied | Check role settings |
| 429 | Rate limit exceeded | Reduce request size or upgrade plan |

### 4. Integration Sync Failures
**Fixes:**
- Validate GitHub/Jira tokens.
- Re-auth via: `aurora integrate github --reset`.
- Clear cache: `aurora cache purge`.
