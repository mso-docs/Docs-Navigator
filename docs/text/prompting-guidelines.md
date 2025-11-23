# AuroraAI Prompting Guidelines

## Core Prompting Principles

### Precision in Instruction Design
Effective prompts leverage **explicit parameter specification** and **contextual grounding**. Treat each prompt as a function call with defined inputs, constraints, and expected outputs.

#### Key Components
1. **Role Definition**: Specify the persona or expertise level (e.g., "As a senior backend engineer...")
2. **Task Specification**: Use action verbs with clear scope (analyze, refactor, generate, validate)
3. **Context Injection**: Provide relevant code snippets, schemas, API contracts, or system architecture
4. **Output Schema**: Define structure using formats like JSON Schema, TypeScript interfaces, or Markdown templates
5. **Constraint Parameters**: Set boundaries (token limits, style guides, programming paradigms, security requirements)

### Prompt Engineering Techniques

#### Chain-of-Thought (CoT)
Request step-by-step reasoning: *"Explain your reasoning before providing the solution."*

#### Few-Shot Learning
Provide 2-3 examples of input-output pairs to establish patterns and expected quality.

#### Delimiter-Based Parsing
Use delimiters (```, XML tags, JSON blocks) to separate code, data, and instructions clearly.

#### Iterative Refinement Protocol
- Start with broad requirements
- Add constraints incrementally
- Validate intermediate outputs
- Adjust temperature/creativity parameters as needed

### Technical Prompt Syntax

```
ROLE: [expertise level and domain]
TASK: [specific action with measurable outcome]
CONTEXT: [relevant code/data/architecture]
CONSTRAINTS: [format, style, security, performance]
OUTPUT: [structured format definition]
VALIDATION: [success criteria or test cases]
```

### Token Budget Management
- Front-load critical information within first 2000 tokens
- Use reference notation for large codebases (file paths, function signatures)
- Employ **sliding window context** for multi-turn interactions
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
