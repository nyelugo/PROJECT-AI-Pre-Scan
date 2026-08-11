# n8n — report delivery

The secondary stack. LangGraph researches and decides; n8n files the result where the adviser works.

## What it does

`POST` webhook receives a finished report from the CLI (`--notify <webhook-url>`) and creates a page
under a parent Notion page, titled `AI Pre-Scan — <company>`.

## Verified

Sent through the real bridge on 11 August 2026. Notion's API — not n8n's status indicator —
returned the created page:

```
id:   3b9cd051-…-013478fe        (redacted)
name: AI Pre-Scan — Fitzgerald Recruitment Ltd
url:  https://app.notion.com/p/AI-Pre-Scan-Fitzgerald-Recruitment-Ltd-…
```

The distinction matters here more than usual: n8n reports success for the workflow, and the only
evidence that a page exists is the object Notion sent back.

## Two traps, both hit while building this

**n8n's UI reports parameter values it may not have stored.** A scripted fill on the Parent Page
field read back correctly and was never committed to the node. Worse, when re-checked by reading
`innerText` of the parameter block — which does not include `<input>` values — it looked empty, so
the "fix" typed a second URL into the middle of the first. Read `.value`, not the rendering.

**The expression editor auto-closes braces.** Typing `{{ … }}` in full produces `{{ … }} }}`. Type
the opening `{{` and the content, and let the editor supply the close.

## Setup

1. Import this file into a **new, empty** workflow — importing over an existing one appends a second
   disconnected copy of every node rather than replacing it.
2. Attach a Notion credential and set the parent page URL.
3. **Share that page with the integration** — Notion grants are per-page and do not cascade. A page
   you can see is not necessarily one the integration can write to, and it fails as a 404, which
   reads like a wrong ID.
4. Run a scan with `--notify <webhook-url>`.
