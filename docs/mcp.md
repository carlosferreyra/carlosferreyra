# Model Context Protocol (MCP) Servers Setup

This guide explains how to configure different MCP servers in Visual Studio Code. MCP servers
enhance GitHub Copilot's capabilities by providing additional context and functionality.

## Available MCP Servers

### GitHub MCP Server

The GitHub MCP server provides access to GitHub-specific functionality like repository management,
issue tracking, and more.

#### Setup

1. Make sure you have Docker installed and running on your system
2. Add the following configuration to your VS Code `settings.json`:

```json
{
	"mcp": {
		"servers": {
			"github": {
				"command": "docker",
				"args": [
					"run",
					"-i",
					"--rm",
					"-e",
					"GITHUB_PERSONAL_ACCESS_TOKEN",
					"ghcr.io/github/github-mcp-server"
				],
				"env": {
					"GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-pat-here"
				}
			}
		}
	}
}
```

3. Replace `your-github-pat-here` with a GitHub Personal Access Token that has the necessary
   permissions for your use case.

#### Required Permissions

The GitHub PAT should have these permissions:

- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)
- `read:org` (Read organization information)
- `read:user` (Read user information)

#### Features

- Repository management
- Issue and PR operations
- GitHub Actions workflow management
- Organization and team management
- And more...

For more information, visit the
[GitHub MCP Server repository](https://github.com/github/github-mcp-server).

### Playwright MCP Server

The Playwright MCP server provides browser automation capabilities for web interactions. It uses
structured accessibility snapshots for better performance and reliability compared to traditional
screenshot-based approaches.

#### Setup

1. Install the Playwright MCP server using NPM:

```bash
npm install @playwright/mcp
```

2. Add the following configuration to your VS Code `settings.json`:

```json
{
	"mcp": {
		"servers": {
			"playwright": {
				"command": "npx",
				"args": ["@playwright/mcp@latest"]
			}
		}
	}
}
```

#### Features

- Fast and lightweight browser automation using Playwright's accessibility tree
- LLM-friendly interaction without requiring vision models
- Deterministic tool application
- Web navigation and form-filling
- Data extraction from structured content

#### Configuration Options

The server supports different modes and configurations:

##### Vision Mode

To enable screenshot-based interactions (useful for coordinate-based element interactions):

```json
{
	"mcp": {
		"servers": {
			"playwright": {
				"command": "npx",
				"args": ["@playwright/mcp@latest", "--vision"]
			}
		}
	}
}
```

##### Headless Mode

For background or batch operations without GUI:

```json
{
	"mcp": {
		"servers": {
			"playwright": {
				"command": "npx",
				"args": ["@playwright/mcp@latest", "--headless"]
			}
		}
	}
}
```

#### CLI Options

- `--browser <browser>`: Choose browser (chrome, firefox, webkit, msedge) or specific channel
- `--caps <caps>`: Enable specific capabilities (tabs, pdf, history, wait, files, install)
- `--headless`: Run browser in headless mode
- `--port <port>`: Custom port for SSE transport
- `--user-data-dir <path>`: Custom user data directory
- `--vision`: Enable screenshot-based interactions

#### Data Storage

Browser profiles are stored at:

- Windows: `%USERPROFILE%\AppData\Local\ms-playwright\mcp-chrome-profile`
- macOS: `~/Library/Caches/ms-playwright/mcp-chrome-profile`
- Linux: `~/.cache/ms-playwright/mcp-chrome-profile`

For more information, visit the
[Playwright MCP Server repository](https://github.com/microsoft/playwright-mcp).

## Adding New MCP Servers

This section will be updated as more MCP servers become available. Each new MCP server will include:

- Setup instructions
- Required permissions/credentials
- Configuration examples
- Feature list
- Additional resources

---

> Note: Always keep your tokens and credentials secure. Never commit them directly to your
> repository.
