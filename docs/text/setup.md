# AuroraAI Setup Guide

## Prerequisites
- Node.js 18+ or Python 3.10+
- Access to the AuroraAI developer portal
- API key with Assistant-level permissions
- Optional: GitHub, Jira, or Confluence integration tokens

## Installation
```bash
yarn global add auroraai
# OR
pip install auroraai-cli
```

## Initialization
```bash
aurora init
```
This command:
- Creates a project directory
- Generates a `.aurora/config.json` file
- Prompts you to add your API key

## Configuration File Example
```json
{
  "apiKey": "YOUR_API_KEY",
  "model": "aurora-pro",
  "contextWindow": 200000,
  "integrations": {
    "github": true,
    "jira": false
  }
}
```

## Connecting Knowledge Sources
```bash
aurora connect ./docs
```
This indexes your local documentation for retrieval.
