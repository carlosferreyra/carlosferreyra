# GitHub Issues Script

A simple script to fetch and display open issues from the GitHub repository.

## Usage

```bash
# Run the script
npm run show-issues

# Or run directly with Node.js
node scripts/issues.js
```

## Authentication

For full functionality, set the `GH_TOKEN` environment variable with your GitHub Personal Access Token:

```bash
export GH_TOKEN=your_github_token_here
npm run show-issues
```

## Features

- Fetches open issues and pull requests from the repository
- Displays formatted information including:
  - Issue number and title
  - Type (Issue or Pull Request)
  - Status (Open, Draft, etc.)
  - Author and creation date
  - Labels and assignees
  - Direct URL to the issue

## Example Output

```
📋 Found 2 open issue(s):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. #10 - [WIP] show me open issues
   Type: Pull Request | Status: Draft
   Author: Copilot | Created: 7/3/2025
   Assignees: carlosferreyra, Copilot
   URL: https://github.com/carlosferreyra/carlosferreyra/pull/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```