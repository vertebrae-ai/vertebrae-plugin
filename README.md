# Vertebrae plugin

Bring your [Vertebrae](https://vertebrae.ai) meeting notes into the agent you already use. Vertebrae transcribes meetings and calls on your own device; this plugin lets Grok Build, Cursor, Grok Bot, and Claude Code search those meetings, read the transcripts and AI summaries, and carry a meeting's decisions into the task in front of you.

The plugin adds Vertebrae's hosted MCP server plus three skills. It installs no binary, reads no local files, and needs no API key. It is read-only.

> Status: pre-release. Marketplace submissions are in progress; install from this repository in the meantime (see below).

## What you can do

| Tool | What it does |
| --- | --- |
| `list_sessions` | The most recent meetings and calls, newest first, with metadata and a truncated AI summary. Optional `limit`, `after`, `before` (ISO-8601). |
| `search_transcripts` | Find sessions matching a query. Ranks title matches above participants, above summaries, above transcript text. Covers the 300 most recent sessions, with transcript bodies read for the 25 most recent; the response reports the window it actually searched. |
| `get_transcript` | One session in full: metadata, the complete AI summary, and every transcript segment in order with speaker labels and timestamps. |

All three tools are read-only. There is nothing here that can change or delete a note.

Example requests:

```text
What did we decide about the onboarding flow in yesterday's call?
Recap this week's meetings with Priya and list my action items.
Before I start on the export feature, pull up where we discussed it.
Write the PR description from what we agreed in the planning meeting.
Create GitHub issues for the action items from Tuesday's standup.
```

## Skills

| Skill | What it does |
| --- | --- |
| `meeting-context` | Before a task that was planned in a meeting, find the relevant sessions, read them, and surface the decisions and constraints with citations. |
| `meeting-recap` | Recap one or several meetings into decisions, action items with owners, and open questions. |
| `action-items-to-work` | Turn a meeting's action items into issues, tickets, a PR description, or a task list using the host's own tools, linking back to the meeting. |

## Install

### Grok Build

Once listed, open `/plugins` in Grok Build, switch to the **Marketplace** tab, find **Vertebrae**, and press `i`. Or from a shell:

```bash
grok plugin install vertebrae --trust
```

Before the listing goes live, install a pinned revision straight from this repository:

```bash
grok plugin install vertebrae-ai/vertebrae-plugin@<full-commit-sha> --trust
```

Start a new session. The first Vertebrae tool call opens your browser to sign in (see below); `/mcps` shows the connection and lets you authenticate with `i`.

If you only want the server without the skills:

```bash
grok mcp add --transport http vertebrae https://mcp.vertebrae.ai/mcp
```

### Cursor

Once listed, open **Customize** in the sidebar, find **Vertebrae** in the Marketplace, and choose **Install**. Cursor signs in on its own and shows the pairing code.

Without the plugin, put this in `~/.cursor/mcp.json` (every project) or `.cursor/mcp.json` (one project), merging with what is already there:

```json
{
  "mcpServers": {
    "vertebrae": {
      "url": "https://mcp.vertebrae.ai/mcp"
    }
  }
}
```

### Grok Bot

Once listed, open **Marketplace** from the sidebar, find **Vertebrae**, and choose **Add**. Until then, tell any Bot:

```text
Add a custom MCP server called Vertebrae at https://mcp.vertebrae.ai/mcp
```

Tap **Authorize** on the card it shows, sign in as below, then attach it to a task with `@`. Grok Bot runs on a cloud computer, so the connection is made from there, not from your laptop; that is fine, the server is public.

### Claude Code

```bash
claude mcp add --transport http vertebrae https://mcp.vertebrae.ai/mcp
```

Or install this repository as a plugin; Claude Code reads `.claude-plugin/plugin.json`.

## Signing in

Vertebrae has no web login. When your agent first connects, a browser page shows an 8-character pairing code. Open the Vertebrae app on your Mac or iPhone, go to **Settings > AI Connections**, and enter the code. The page notices and the agent is connected. Each agent you connect is approved this way, one at a time, and every connected agent is listed in the app where you can disconnect it at any time. Disconnecting takes effect immediately.

**AI Connections has to be switched on** in the app first. While it is off, the server answers every request with 403 rather than an empty list, so the agent can tell you the connector is off instead of telling you that you have no meetings.

## Authentication, data, and permissions

- The plugin connects to two Vertebrae hosts and nothing else: `https://mcp.vertebrae.ai/mcp` (the MCP server and its protected-resource metadata) and `https://api.vertebrae.ai` (the OAuth authorization server: `/oauth/authorize`, `/oauth/token`, `/oauth/register`). Your agent finds the second from the first through standard discovery (RFC 9728 and RFC 8414); nothing is hardcoded here.
- Authentication is OAuth 2.1 with PKCE, handled by your agent; the plugin ships no credentials, reads no environment variables, `.env` files, or local secrets, and runs no local process.
- The only scope is `transcripts:read`. Every tool is read-only.
- While AI Connections is on, the transcripts and summaries on your account are stored on Vertebrae's servers in plaintext so they can be handed to an agent you approved. Audio is never included. Turning AI Connections off deletes that copy and disconnects every agent. This is described in full in the [Vertebrae privacy policy](https://vertebrae.ai/privacy).
- What the agent does with what it reads is between you and the maker of that agent.

## Try a single shared note without an account

Anyone with a Vertebrae shared note link can point an agent at that one note by appending `/mcp` to the link (for example `https://notes.vertebrae.ai/<note-id>/mcp`). It is a separate, read-only server with a single `get_note` tool, no sign-in, and access to nothing but that note. The link is the key, so treat it like one.

## Development

- `.grok-plugin/plugin.json` and `.claude-plugin/plugin.json` are identical; `.cursor-plugin/plugin.json` carries the same fields plus Cursor's component paths.
- `.mcp.json` (Grok Build, Claude Code) and `mcp.json` (Cursor) declare the same server. CI fails if they drift.
- Validate locally with `grok plugin validate .`

## Support and resources

- [Vertebrae](https://vertebrae.ai)
- [Privacy policy](https://vertebrae.ai/privacy)
- [Report a plugin issue](https://github.com/vertebrae-ai/vertebrae-plugin/issues)

## License

Apache License 2.0. See [LICENSE](LICENSE).
