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
import time
import uuid
from datetime import datetime, timezone

import markdown as md
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse

from . import (browser, clients, config, graph, notify, render, sample_clients,
               store_jobs, tools)
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
        if scan.client_id:
            clients.record_scan(scan.client_id, scan)
        _work.task_done()


def _domain_resolver() -> None:
    """Fill in websites Maria did not supply — as suggestions she reviews, never as fact.

    Runs quietly in the background so importing forty clients stays one paste. The system is good
    at finding a likely domain and cannot know it is the right company; she can, in a glance.
    """
    while True:
        pending = clients.needs_domain() if not DEMO else []
        if not pending:
            time.sleep(20)
            continue
        for c in pending:
            try:
                clients.suggest_domain(c.id, tools.identity(c.name).domain)
            except Exception:  # noqa: BLE001 — resolution failing must not stop the app
                clients.suggest_domain(c.id, None)
            time.sleep(1)


threading.Thread(target=_worker, daemon=True).start()
threading.Thread(target=_domain_resolver, daemon=True).start()


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
.book td:first-child{width:26px}
.never{color:var(--bad);font-weight:600}
.unconfirmed{font-size:13px;color:var(--warn)}
.noweb{font-size:13px;color:var(--bad)}
.linkish{background:none;border:0;color:var(--accent);padding:0 0 0 4px;font-size:13px;
  text-decoration:underline;cursor:pointer}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
.chip{padding:5px 12px;border:1px solid var(--line);border-radius:20px;font-size:13.5px;
  text-decoration:none;color:var(--ink);background:#fff}
.chip.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.chip .n{opacity:.65;margin-left:5px}
.rowscan{background:none;border:1px solid var(--line);border-radius:6px;padding:4px 10px;
  font-size:12.5px;color:var(--ink);cursor:pointer}
.rowscan:hover{border-color:var(--accent);color:var(--accent)}
.est{color:var(--mut);font-size:13.5px}
@media print{
  header,.actions,.bar,.filters,details,form{display:none!important}
  body{background:#fff}.card{border:0;padding:0;margin:0 0 14px}
  .ask{border:1px solid #999;background:#fff}
  a{color:#000;text-decoration:none}
}
.stale{color:var(--warn)}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0 0}
.ghost{background:#fff;color:var(--ink);border:1px solid var(--line)}
.mini{font-size:13px;padding:7px 13px}
details summary{cursor:pointer;font-size:14.5px;color:var(--accent)}
details[open] summary{margin-bottom:10px}
.count{color:var(--mut);font-size:13.5px}
.row{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.actions a{margin-left:14px;font-size:14px}
.demo{margin:12px 0 0;padding:8px 12px;background:#fdf7e6;border:1px solid #f0e2b8;border-radius:7px;font-size:13.5px;color:#6b5510}
.spin{display:inline-block;width:12px;height:12px;border:2px solid var(--line);
      border-top-color:var(--warn);border-radius:50%;animation:s .8s linear infinite;vertical-align:-1px}
@keyframes s{to{transform:rotate(360deg)}}
"""


def _identity_cell(c) -> str:
    """A missing or unconfirmed website is never shown as blank space."""
    warn = c.identity_warning
    if not warn:
        return f'<div class="hint">{html.escape(c.domain)}</div>'
    if c.domain_status == "suggested":
        return f"""<div class="unconfirmed">{html.escape(c.domain or '')} — unconfirmed
          <form method="post" action="/clients/{c.id}/confirm" style="display:inline">
            <button type="submit" class="linkish">that's right</button></form></div>"""
    if c.domain_status == "unresolved":
        return '<div class="noweb">No website found — add one on the client page</div>'
    return '<div class="hint">looking up website…</div>'


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

FILTERS = {
    "all": ("All", lambda c: True),
    "never": ("Never scanned", lambda c: c.never_scanned),
    "due": ("Due a re-scan", lambda c: c.is_stale),
    "identity": ("Website unconfirmed", lambda c: c.identity_warning is not None),
}
MINUTES_PER_SCAN = 2.5


@app.get("/", response_class=HTMLResponse)
async def book(filter: str = "all") -> str:
    """The client book, ordered by who needs attention rather than alphabetically."""
    roster = clients.all_clients()
    keep = FILTERS.get(filter, FILTERS["all"])[1]
    shown = [c for c in roster if keep(c)]
    running = [x for x in store_jobs.recent(20) if x.status in ("queued", "running")]

    rows = []
    for c in shown:
        if c.never_scanned:
            status = '<span class="never">Never scanned</span>'
        elif c.is_stale:
            status = f'<span class="stale">{html.escape(c.status())}</span>'
        else:
            status = html.escape(c.status())

        result = "—"
        if not c.never_scanned:
            bits = [f"{c.last_findings} system{'s' if c.last_findings != 1 else ''}"]
            if c.last_undetermined:
                bits.append(f"<b>{c.last_undetermined} undetermined</b>")
            bits.append(f"{c.last_questions} to ask")
            result = " · ".join(bits)
            if c.last_scan_id:
                result = f'<a href="/scan/{c.last_scan_id}">{result}</a>'

        rows.append(f"""<tr>
  <td><input type="checkbox" name="client" value="{c.id}" class="pick"></td>
  <td><a href="/client/{c.id}"><b>{html.escape(c.name)}</b></a>{_identity_cell(c)}</td>
  <td>{status}</td><td>{result}</td>
  <td><button type="submit" name="scan_one" value="{c.id}" class="rowscan"
      >{'Scan' if c.never_scanned else 'Re-scan'}</button></td></tr>""")

    chips = "".join(
        f'<a class="chip {"on" if filter == key else ""}" href="/?filter={key}">{label}'
        f'<span class="n">{sum(1 for c in roster if fn(c))}</span></a>'
        for key, (label, fn) in FILTERS.items())

    if not roster:
        body_book = f"""<p class='empty'>Your client book is empty.</p>
<p class="hint">Paste your client list below — one per line, website after a comma if you know it.</p>
<form method="post" action="/clients/load-samples" style="margin-top:14px">
  <button type="submit" class="mini ghost">Load {len(sample_clients.SAMPLES)} sample clients</button>
  <span class="hint">Real companies with published AI use, for trying the tool out. Roughly half
     produce findings and half correctly produce almost none.</span>
</form>"""
    elif not shown:
        body_book = f"<div class='filters'>{chips}</div><p class='empty'>No clients match that view.</p>"
    else:
        body_book = f"""<div class="filters">{chips}</div>
<form method="post" action="/scan-selected" id="bookform">
<table class="book"><tr>
  <th><input type="checkbox" id="pickall" title="Select all shown"></th>
  <th>Client</th><th>Status</th><th>Last result</th><th></th></tr>{''.join(rows)}</table>
<div class="bar">
  <button type="submit" id="scanbtn" disabled>Scan selected</button>
  <button type="submit" name="all" value="1" class="ghost mini" id="scanall"
    >Scan every client ({len(roster)})</button>
  <span class="est" id="est"></span>
</div></form>
<script>
 const picks=[...document.querySelectorAll('.pick')],btn=document.getElementById('scanbtn'),
       est=document.getElementById('est'),all=document.getElementById('pickall');
 function upd(){{
   const n=picks.filter(p=>p.checked).length;
   btn.disabled=!n;
   btn.textContent=n?`Scan ${{n}} selected`:'Scan selected';
   est.textContent=n?`about ${{Math.max(1,Math.round(n*{MINUTES_PER_SCAN}))}} minutes, running one at a time`:'';
 }}
 picks.forEach(p=>p.onchange=upd);
 if(all) all.onchange=()=>{{picks.forEach(p=>p.checked=all.checked);upd();}};
 document.getElementById('scanall').onclick=e=>{{
   const mins=Math.round({len(roster)}*{MINUTES_PER_SCAN});
   if(!confirm(`Scan all {len(roster)} clients?\n\nThey run one at a time and will take about ${{mins}} minutes. You can close the page and come back.`)) e.preventDefault();
 }};
 upd();
</script>"""

    queue = ""
    if running:
        items = " · ".join(f"{html.escape(x.company)} ({x.status})" for x in running[:6])
        queue = (f"<div class='card'><span class='spin'></span> <b>Scanning:</b> {items}"
                 f"<p class='hint'>This page updates itself. You can close it.</p></div>")

    # Adding clients sits above the book only when there is no book yet — otherwise the list she
    # came to read should be the first thing on the page.
    add_card = f"""<div class="card">
  <h2 style="margin:0 0 4px;font-size:17px">{'Add your clients' if not roster else 'Add clients'}</h2>
  <p class="hint" style="margin:0 0 12px">One per line, website after a comma when you know it.
     A single name works too.</p>
  <form method="post" action="/clients/import">
    <textarea name="lines" rows="{5 if not roster else 3}"
      placeholder="Fitzgerald Recruitment Ltd, fitzgeraldrecruitment.ie&#10;Colten Care, coltencare.co.uk&#10;Ballymaloe Foods"></textarea>
    <p style="margin:12px 0 0"><button type="submit" class="mini">Add to book</button>
      <span class="hint">Names already in the book are skipped.</span></p>
  </form></div>"""

    book_card = f"""<div class="card">
  <h2 style="margin:0 0 4px;font-size:17px">Client book</h2>
  <p class="hint" style="margin:0 0 14px">Ordered by who needs attention: never scanned first,
     then overdue, then most unresolved.</p>
  {body_book}</div>"""

    prospect = """<div class="card"><details>
    <summary>Scan a company that is not a client</summary>
    <form method="post" action="/scan" style="margin-top:8px">
      <p><input type="text" name="names" placeholder="Prospect Ltd, prospect.com"></p>
      <p><button type="submit" class="mini ghost">Scan once</button>
        <span class="hint">A one-off look. It is not added to your book.</span></p>
    </form></details></div>"""

    order = [queue, add_card, book_card] if not roster else [queue, book_card, add_card, prospect]
    return _page("Client book", "\n".join(x for x in order if x), refresh=bool(running))


@app.get("/client/{client_id}", response_class=HTMLResponse)
async def client_page(client_id: str) -> str:
    c = clients.get(client_id)
    if not c:
        return _page("Not found", "<div class='card'>That client is not in your book.</div>")
    history = [s for s in store_jobs.recent(200) if s.client_id == client_id]

    rows = "".join(
        f"<tr><td>{html.escape(s.started_at[:10])}</td>"
        f"<td>{'<a href=/scan/' + s.id + '>' + html.escape(s.summary_line()) + '</a>' if s.status == 'done' else html.escape(s.status)}</td>"
        f"<td>{s.elapsed}s</td></tr>" for s in history) or         "<tr><td colspan=3 class='empty'>No scans yet.</td></tr>"

    return _page(c.name, f"""
<div class="card">
  <div class="row">
    <div><b style="font-size:19px">{html.escape(c.name)}</b>
      <div class="hint">{html.escape(c.domain or 'no website recorded')} · {c.status()}</div></div>
    <div class="actions">
      <form method="post" action="/scan-selected" style="display:inline">
        <input type="hidden" name="client" value="{c.id}">
        <button type="submit" class="mini">{'Scan now' if c.never_scanned else 'Re-scan'}</button>
      </form>
    </div>
  </div>
</div>
{_identity_card(c)}
<div class="card">
  <h2 style="margin:0 0 12px;font-size:17px">Scan history</h2>
  <table><tr><th>Date</th><th>Result</th><th>Took</th></tr>{rows}</table>
  <p class="hint" style="margin-top:14px">Re-scanning is how a vendor quietly adding AI to a tool
     they already use gets caught — the client changes nothing, so nobody there is watching.</p>
</div>
<div class="card">
  <details><summary>Remove {html.escape(c.name)} from the book</summary>
    <form method="post" action="/clients/{c.id}/delete" style="margin-top:8px">
      <button type="submit" class="mini ghost">Remove</button>
      <span class="hint">Scan history is kept.</span></form></details>
</div>
<p><a href="/">Back to the client book</a></p>
""")


def _identity_card(c) -> str:
    warn = c.identity_warning
    if not warn:
        return ""
    return f"""<div class="ask">
  <h2>Which company is this?</h2>
  <p>{html.escape(warn)}</p>
  <p class="hint">A page on the client's own website is about that client by construction. Without
     one, findings rest on the name, and a report about the wrong company reads exactly like a
     right one.</p>
  <form method="post" action="/clients/{c.id}/confirm" style="margin-top:12px">
    <input type="text" name="domain" placeholder="acme.ie"
           value="{html.escape(c.domain or '')}" style="max-width:320px">
    <button type="submit" class="mini" style="margin-left:8px">Confirm website</button>
  </form></div>"""


@app.post("/clients/add")
async def add_client(name: str = Form(""), domain: str = Form("")) -> RedirectResponse:
    clients.add(name, domain)
    return RedirectResponse("/", status_code=303)


@app.post("/clients/load-samples")
async def load_samples() -> RedirectResponse:
    """Seed the book with real, findable companies.

    Domains are verified rather than resolved — see the note in sample_clients.py about "Clay"
    resolving to a country singer.
    """
    clients.import_lines(sample_clients.as_import_lines())
    return RedirectResponse("/", status_code=303)


@app.post("/clients/import")
async def import_clients(lines: str = Form("")) -> RedirectResponse:
    clients.import_lines(lines)
    return RedirectResponse("/", status_code=303)


@app.post("/clients/{client_id}/confirm")
async def confirm_domain(client_id: str, domain: str = Form("")) -> RedirectResponse:
    clients.confirm_domain(client_id, domain or None)
    return RedirectResponse(f"/client/{client_id}", status_code=303)


@app.post("/clients/{client_id}/delete")
async def delete_client(client_id: str) -> RedirectResponse:
    clients.remove(client_id)
    return RedirectResponse("/", status_code=303)


def parse_line(line: str) -> tuple[str, str | None]:
    """`Acme Ltd` or `Acme Ltd, acme.ie` — the domain is optional and always wins when given."""
    if "," in line:
        name, _, dom = line.partition(",")
        return name.strip(), clients.clean_domain(dom)
    return line.strip(), None


@app.post("/scan")
async def scan_once(names: str = Form("")) -> RedirectResponse:
    """A one-off look at a company that is not in the book — a prospect, or a name being checked.

    Deliberately does not add them: the book is Maria's client list, not a log of everything she
    has ever typed.
    """
    started = []
    for line in [n for n in names.splitlines() if n.strip()][:40]:
        company, domain = parse_line(line)
        if not company:
            continue
        scan = Scan(id=uuid.uuid4().hex[:10], company=company, domain=domain)
        store_jobs.save(scan)
        _work.put((scan, NOTIFY_URL))
        started.append(scan)
    if len(started) == 1:
        return RedirectResponse(f"/scan/{started[0].id}", status_code=303)
    return RedirectResponse("/", status_code=303)


@app.post("/scan-selected")
async def scan_selected(request: Request) -> RedirectResponse:
    """Scan ticked clients, or the whole book."""
    form = await request.form()
    one = form.get("scan_one")
    ids = [one] if one else form.getlist("client")
    chosen = clients.all_clients() if (form.get("all") and not one) else [
        c for c in (clients.get(i) for i in ids) if c
    ]
    started = []
    for c in chosen[:60]:
        scan = Scan(id=uuid.uuid4().hex[:10], company=c.name, domain=c.domain, client_id=c.id)
        store_jobs.save(scan)
        _work.put((scan, NOTIFY_URL))
        started.append(scan)
    if len(started) == 1:
        return RedirectResponse(f"/scan/{started[0].id}", status_code=303)
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
        if s.status == "failed":
            return _page(s.company, f"""<div class="card">
  <b style="font-size:19px">{html.escape(s.company)}</b>
  <p>{html.escape(s.error or 'The scan did not finish.')}</p>
  <p><a href="/">Back to all scans</a></p></div>""")
        waited = s.elapsed
        return _page(s.company, f"""<div class="card">
  <b style="font-size:19px">{html.escape(s.company)}</b>
  <p style="margin:10px 0 4px"><span class="spin"></span>
     Researching — {waited}s so far, usually two to three minutes.</p>
  <p class="hint">Reading the client's website, careers pages, named vendors and press coverage.
     This page updates itself; you can close it and find the scan under
     <a href="/">all scans</a>.</p></div>""", refresh=True)

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
