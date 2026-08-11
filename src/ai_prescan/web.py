"""The interface Maria uses.

Designed around her actual job rather than around the pipeline. She advises forty small companies,
so she works from a client list, not one name at a time; she needs the report readable rather than
raw; and the thing she carries into a meeting is the question list, not the inventory.

Three decisions follow from that:

* **A list in, a queue out.** Paste any number of client names. Scans run one at a time so the
  research APIs are not hammered, and the dashboard shows the queue draining.
* **Questions first.** The discussion list sits above the inventory, because it is the part she
  acts on. The inventory is the evidence behind it.
* **History persists.** A scan she paid for is still there tomorrow.

    python -m ai_prescan.web        # http://127.0.0.1:8000
"""

from __future__ import annotations

import html
import queue
import threading
import uuid
from datetime import datetime, timezone

import markdown as md
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse

from . import browser, config, graph, notify, render, store_jobs
from .schemas import Confidence
from .store_jobs import Scan

app = FastAPI(title="AI Pre-Scan")

_work: "queue.Queue[tuple[Scan, str | None]]" = queue.Queue()
NOTIFY_URL: str | None = None
DEMO = False        # fixtures instead of live research: no keys, no network, deterministic


# ─────────────────────────────── worker ───────────────────────────────

def _worker() -> None:
    """One scan at a time. Research APIs have rate limits and a queue is kinder than a stampede."""
    while True:
        scan, webhook = _work.get()
        scan.status = "running"
        store_jobs.save(scan)
        try:
            report = graph.scan(scan.company, domain=scan.domain, use_fixtures=DEMO)
            scan.markdown = render.to_markdown(report)
            scan.findings = len(report.findings)
            scan.evidenced = sum(1 for f in report.findings if f.confidence is Confidence.EVIDENCED)
            scan.undetermined = report.undetermined_count
            scan.questions = len(report.discussion)
            scan.sources = report.sources_consulted
            scan.unavailable = len(report.unavailable_sources)
            if webhook:
                res = notify.deliver(report, scan.markdown, webhook)
                scan.delivered = "Filed to Notion" if res.ok else f"Not filed — {res.reason}"
            scan.status = "done"
        except Exception as exc:  # noqa: BLE001
            scan.status = "failed"
            # Plain language. "KeyError" tells Maria nothing she can act on.
            scan.error = f"The scan could not finish ({type(exc).__name__}). Nothing was reported."
        scan.finished_at = datetime.now(timezone.utc).isoformat()
        store_jobs.save(scan)
        _work.task_done()


threading.Thread(target=_worker, daemon=True).start()


# ─────────────────────────────── styling ───────────────────────────────

CSS = """
:root{--ink:#1c1c1c;--mut:#6b6b6b;--line:#e4e2dd;--bg:#faf9f7;--card:#fff;
      --accent:#2f6f4f;--warn:#8a6a12;--bad:#9b2226}
*{box-sizing:border-box}
body{margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,sans-serif;
     color:var(--ink);background:var(--bg)}
a{color:var(--accent)}
.wrap{max-width:920px;margin:0 auto;padding:0 24px}
header{background:var(--card);border-bottom:1px solid var(--line);padding:26px 0 20px}
h1{margin:0;font-size:24px;letter-spacing:-.01em}
h1 a{color:inherit;text-decoration:none}
.sub{color:var(--mut);margin:6px 0 0;font-size:15px}
main{padding:28px 0 70px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:22px 24px;
      margin-bottom:20px}
textarea,input[type=text]{width:100%;padding:12px 14px;font:15px/1.5 inherit;border:1px solid var(--line);
     border-radius:8px;background:#fff;resize:vertical}
textarea:focus,input:focus{outline:2px solid var(--accent);outline-offset:-1px}
button{padding:12px 22px;font-size:15px;border:0;border-radius:8px;background:var(--accent);
       color:#fff;cursor:pointer}
.hint{color:var(--mut);font-size:13.5px;margin:8px 0 0}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
tr:last-child td{border-bottom:0}
.pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12.5px;border:1px solid var(--line)}
.p-done{background:#eef5f0;color:var(--accent);border-color:#cfe3d7}
.p-run{background:#fdf7e6;color:var(--warn);border-color:#f0e2b8}
.p-fail{background:#fdeeee;color:var(--bad);border-color:#f2cccc}
.tiles{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 20px}
.tile{border:1px solid var(--line);border-radius:9px;padding:11px 15px;background:var(--card);min-width:104px}
.tile b{display:block;font-size:22px;line-height:1.2}
.tile span{color:var(--mut);font-size:12.5px}
.tile.warn b{color:var(--warn)}
.ask{background:#fffdf5;border:1px solid #f0e2b8;border-radius:10px;padding:20px 24px;margin-bottom:22px}
.ask h2{margin:0 0 10px;font-size:17px}
.ask li{margin-bottom:10px}
.report h2{font-size:18px;margin:26px 0 10px;padding-top:16px;border-top:1px solid var(--line)}
.report h3{font-size:15.5px;margin:20px 0 6px}
.report blockquote{margin:8px 0;padding:9px 14px;border-left:3px solid var(--line);
      background:#fafafa;color:#333;font-size:14.5px}
.report table{margin:10px 0 18px}
.report code{background:#f4f4f2;padding:1px 5px;border-radius:4px;font-size:13.5px}
.empty{color:var(--mut);padding:18px 0}
.row{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.actions a{margin-left:14px;font-size:14px}
.demo{margin:12px 0 0;padding:8px 12px;background:#fdf7e6;border:1px solid #f0e2b8;border-radius:7px;font-size:13.5px;color:#6b5510}
.spin{display:inline-block;width:12px;height:12px;border:2px solid var(--line);
      border-top-color:var(--warn);border-radius:50%;animation:s .8s linear infinite;vertical-align:-1px}
@keyframes s{to{transform:rotate(360deg)}}
"""


def _page(title: str, body: str, refresh: bool = False) -> str:
    meta = '<meta http-equiv="refresh" content="5">' if refresh else ""
    banner = ('<p class="demo">Demo mode — fixed sample data, no live research. '
              'Run without <code>--demo</code> once your API keys are set.</p>') if DEMO else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{meta}
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header><div class="wrap"><h1><a href="/">AI Pre-Scan</a></h1>
<p class="sub">What AI is my client actually running — and what should I ask them?</p>
{banner}</div></header>
<main class="wrap">{body}</main></body></html>"""


# ─────────────────────────────── routes ───────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    scans = store_jobs.recent()
    active = any(s.status in ("queued", "running") for s in scans)

    rows = []
    for s in scans:
        cls = {"done": "p-done", "failed": "p-fail"}.get(s.status, "p-run")
        label = s.status if s.status != "running" else f'<span class="spin"></span> running'
        name = html.escape(s.company)
        link = f'<a href="/scan/{s.id}">{name}</a>' if s.status == "done" else name
        if s.domain:
            link += f"<div class='hint' style='margin:2px 0 0'>{html.escape(s.domain)}</div>"
        rows.append(
            f"<tr><td>{link}</td><td><span class='pill {cls}'>{label}</span></td>"
            f"<td>{html.escape(s.summary_line())}</td><td>{s.elapsed}s</td></tr>"
        )

    table = ("<table><tr><th>Client</th><th>Status</th><th>Result</th><th>Took</th></tr>"
             + "".join(rows) + "</table>") if rows else \
            "<p class='empty'>No scans yet. Add a client above to start.</p>"

    return _page("AI Pre-Scan", f"""
<div class="card">
  <form method="post" action="/scan">
    <label for="names"><b>Client names</b></label>
    <p class="hint" style="margin:4px 0 8px">One per line, and add the client's website after a
       comma when you know it — <code>Acme Ltd, acme.ie</code>. A bare name can match the wrong
       company, and on a long list a wrong report looks just like a right one.</p>
    <textarea id="names" name="names" rows="4"
      placeholder="Fitzgerald Recruitment Ltd, fitzgeraldrecruitment.ie&#10;Colten Care, coltencare.co.uk&#10;Ballymaloe Foods"></textarea>
    <p style="margin:14px 0 0"><button type="submit">Scan</button></p>
    <p class="hint">Each scan takes two to three minutes. Anything the public evidence cannot settle
       comes back as <b>undetermined</b> and becomes a question for the client, rather than a guess.</p>
  </form>
</div>
<div class="card"><h2 style="margin:0 0 14px;font-size:17px">Recent scans</h2>{table}</div>
""", refresh=active)


def parse_line(line: str) -> tuple[str, str | None]:
    """`Acme Ltd` or `Acme Ltd, acme.ie` — the domain is optional and always wins when given."""
    if "," in line:
        name, _, dom = line.partition(",")
        dom = dom.strip().lower().removeprefix("https://").removeprefix("http://") \
                 .removeprefix("www.").rstrip("/")
        return name.strip(), (dom or None)
    return line.strip(), None


@app.post("/scan")
async def start(names: str = Form("")) -> RedirectResponse:
    for line in [n for n in names.splitlines() if n.strip()][:40]:
        company, domain = parse_line(line)
        if not company:
            continue
        scan = Scan(id=uuid.uuid4().hex[:10], company=company, domain=domain)
        store_jobs.save(scan)
        _work.put((scan, NOTIFY_URL))
    return RedirectResponse("/", status_code=303)


# Declared before /scan/{scan_id}: FastAPI matches in order, and the catch-all would otherwise
# swallow "abc.md" as a scan id — which made the Download button lead to "that scan no longer
# exists". Found by a test, not by looking at the page.
@app.get("/scan/{scan_id}.md", response_class=PlainTextResponse)
async def download(scan_id: str) -> str:
    s = store_jobs.get(scan_id)
    return s.markdown if s else "not found"


@app.get("/scan/{scan_id}", response_class=HTMLResponse)
async def report(scan_id: str) -> str:
    s = store_jobs.get(scan_id)
    if not s:
        return _page("Not found", "<div class='card'>That scan no longer exists.</div>")
    if s.status != "done":
        note = s.error or "This scan is still running."
        return _page(s.company, f"<div class='card'>{html.escape(note)}</div>", refresh=s.status != "failed")

    body_html = md.markdown(s.markdown, extensions=["tables"])

    # Lift the questions out of the report and put them first — that is what she carries in.
    questions = ""
    if "## Questions to discuss with the client" in s.markdown:
        chunk = s.markdown.split("## Questions to discuss with the client", 1)[1]
        chunk = chunk.split("\n## ", 1)[0]
        questions = (f"<div class='ask'><h2>Ask {html.escape(s.company)}</h2>"
                     f"{md.markdown(chunk)}</div>")

    return _page(s.company, f"""
<div class="card">
  <div class="row">
    <div><b style="font-size:19px">{html.escape(s.company)}</b>
      <div class="hint">Scanned {html.escape(s.started_at[:10])} · {s.sources} sources read
        {' · ' + html.escape(s.delivered) if s.delivered else ''}</div></div>
    <div class="actions"><a href="/scan/{s.id}.md">Download report</a><a href="/">All scans</a></div>
  </div>
  <div class="tiles" style="margin-top:18px">
    <div class="tile"><b>{s.findings}</b><span>systems found</span></div>
    <div class="tile"><b>{s.evidenced}</b><span>evidenced</span></div>
    <div class="tile warn"><b>{s.undetermined}</b><span>undetermined</span></div>
    <div class="tile"><b>{s.questions}</b><span>to ask client</span></div>
  </div>
</div>
{questions}
<div class="card report">{body_html}</div>
""")


@app.get("/api/scans")
async def api_scans() -> JSONResponse:
    return JSONResponse([{"id": s.id, "company": s.company, "status": s.status,
                          "findings": s.findings, "undetermined": s.undetermined}
                         for s in store_jobs.recent()])


def main() -> int:
    import argparse

    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--notify", help="n8n webhook to file each finished report")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--demo", action="store_true",
                    help="run on fixed sample data: no API keys, no network")
    args = ap.parse_args()

    global NOTIFY_URL
    NOTIFY_URL = args.notify

    global DEMO
    DEMO = args.demo

    if not DEMO:
        try:
            config.preflight(require_live=True)
        except RuntimeError as exc:
            print(f"\n{exc}\n\n"
                  f"Add them to {config.KEY_STORE}, or start with sample data instead:\n"
                  f"    ai-prescan-web --demo\n")
            return 1
        browser.install()

    print(f"AI Pre-Scan{' (demo)' if DEMO else ''} — open http://127.0.0.1:{args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
