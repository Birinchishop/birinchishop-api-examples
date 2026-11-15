# Birinchi Shop MCP server (for AI agents)

Endpoint: `https://birinchishop.uz/api/v1/mcp` (Streamable HTTP, stateless).

**Claude.ai / ChatGPT:** add a custom connector with this URL — sign in with OAuth, no key needed.

**Claude Code:**

```bash
claude mcp add --transport http birinchishop https://birinchishop.uz/api/v1/mcp --header "Authorization: Bearer $BSK_KEY"
```

**Cursor / generic client** (`mcp.json`):

```json
{
  "mcpServers": {
    "birinchishop": {
      "type": "http",
      "url": "https://birinchishop.uz/api/v1/mcp",
      "headers": { "Authorization": "Bearer ${BSK_KEY}" }
    }
  }
}
```

Tools include searching offers, creating tracking links, reading orders and stats, and a daily review of results and Meta ad campaigns.
Actions that could increase ad spend (resume, budget change) are never executed directly — the partner confirms them in the panel or Telegram bot.
Full list: https://birinchishop.uz/api/v1/guide.md#ai-agents-mcp
