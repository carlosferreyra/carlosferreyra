# Claude Pro — Quickstart Cheatsheet

> Quick reference for Carlos on Claude Pro via VSCode + claude.ai

---

## Claude Code (VSCode Extension)

### Getting Started

- **Invoke:** Open Command Palette → `Claude Code` or use the sidebar panel
- **Inline chat:** Select code → right-click → `Ask Claude` or `Ctrl+Shift+I` (Mac: `Cmd+Shift+I`)
- **Status bar:** Shows active model and usage at the bottom of VSCode

### Key Commands (type in chat)

| Command      | What it does                                          |
| ------------ | ----------------------------------------------------- |
| `/help`      | List all available slash commands                     |
| `/commit`    | Generate a git commit message from staged changes     |
| `/review-pr` | Review a pull request                                 |
| `/fast`      | Toggle fast mode (same Opus 4.6 model, faster output) |
| `/clear`     | Clear conversation context                            |

### Pro Model Access

- Default model: **Claude Sonnet 4.6** (`claude-sonnet-4-6`)
- Pro unlocks higher rate limits vs free tier
- Switch models via settings or `/model` command

### Agents & Tools

- Claude Code can run **sub-agents** for complex multi-step tasks
- Has access to: file read/write, grep, glob, bash, web search/fetch
- Use natural language: _"refactor this file"_, _"find all usages of X"_, _"fix the failing test"_

### Hooks (Automation)

- Configure automated behaviors in `settings.json` (e.g., run lint after every edit)
- Use `/update-config` skill to set up hooks without editing JSON manually

### Memory System

- Claude Code maintains a **persistent memory** across sessions at `~/.claude/projects/`
- Remembers your preferences, feedback, and project context between conversations
- Say _"remember that..."_ to explicitly save something

### Tips

- Be specific: include file paths and line numbers in requests
- Use `@filename` to reference files in chat
- Long tasks: Claude will use TodoWrite to track progress — you can follow along

---

## Web Features (claude.ai)

### Chat

- **Extended thinking:** Available on Pro — Claude reasons step-by-step before answering
- **Projects:** Create persistent workspaces with custom instructions and uploaded docs
- **Artifacts:** Claude generates runnable code, diagrams, and documents in a side panel

### Projects

- Upload PDFs, docs, or code as **project knowledge**
- Set a **custom system prompt** per project (great for domain-specific assistants)
- All chats in a project share the same context window

### Artifacts (Side Panel)

| Type          | Example use                           |
| ------------- | ------------------------------------- |
| Code          | Generate and run JS/Python in-browser |
| Markdown      | Docs, README drafts                   |
| SVG / Mermaid | Diagrams, flowcharts                  |
| React         | Interactive UI prototypes             |

### Voice (Mobile)

- Claude Pro includes voice input on the mobile app
- Great for dictating long prompts on the go

### Rate Limits (Pro vs Free)

- Pro: ~5x more messages per hour on Opus/Sonnet models
- Priority access during high-traffic periods
- Extended context window: **200K tokens** per conversation

---

## Model Reference

| Model      | ID                          | Best for                        |
| ---------- | --------------------------- | ------------------------------- |
| Sonnet 4.6 | `claude-sonnet-4-6`         | Default — fast + capable        |
| Opus 4.6   | `claude-opus-4-6`           | Complex reasoning, architecture |
| Haiku 4.5  | `claude-haiku-4-5-20251001` | Speed-critical, simple tasks    |

---

## Useful Links

- Docs: <https://docs.anthropic.com/claude-code>
- Issues / feedback: <https://github.com/anthropics/claude-code/issues>
- Claude web app: <https://claude.ai>
- API reference: <https://docs.anthropic.com/api>

---

_Generated 2026-04-08 — Claude Pro plan_
