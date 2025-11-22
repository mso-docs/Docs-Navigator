# AuroraAI Prompting Guidelines

## Best Practices
- **Be explicit** about the output format (tables, JSON, Markdown, etc.).
- **Provide context** such as code samples, user stories, or error logs.
- **Use constraints** like tone, word limits, or style rules.
- **Iterate** by refining instructions rather than restarting.

## Example Prompts
### Technical Writing Prompt
"Rewrite this API overview in a concise style and include an authentication section. Output in Markdown."

### Engineering Prompt
"Given this error log, diagnose the root cause and propose three fixes ranked by difficulty."

### Documentation Prompt
"Create troubleshooting steps for users who can't authenticate. Include a table of error codes."

## Anti-Patterns to Avoid
- Vague commands like "Fix this".
- Multi-task prompts that blend unrelated asks.
- Lack of constraints when requesting decisions.
