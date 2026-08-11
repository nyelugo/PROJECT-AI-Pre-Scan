"""Entry point.

    python -m ai_prescan "Fitzgerald Recruitment Ltd"          # fixture run, no network, no keys
    python -m ai_prescan "Company" --live                      # Phase 2
"""

from __future__ import annotations

import argparse
import sys

from . import browser, config, notify, render
from .graph import scan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ai-prescan", description=__doc__)
    ap.add_argument("company")
    ap.add_argument("--live", action="store_true", help="use live tools (Phase 2)")
    ap.add_argument("--out", help="write the report here instead of stdout")
    ap.add_argument("--notify", metavar="WEBHOOK_URL",
                    help="also POST the finished report to an n8n webhook for filing")
    args = ap.parse_args(argv)

    if args.live:
        browser.install()   # blocked hosts get a real browser rather than vanishing

    for status in config.preflight(require_live=args.live):
        print(status, file=sys.stderr)

    report = scan(args.company, use_fixtures=not args.live)
    text = render.to_markdown(report)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text)

    if args.notify:
        result = notify.deliver(report, text, args.notify)
        # Delivery failure is reported, not swallowed and not fatal — the report exists either way,
        # and a filing step that fails quietly is how a client never receives one.
        print(f"n8n delivery: {'ok' if result.ok else 'FAILED — ' + (result.reason or '')}",
              file=sys.stderr)
        return 0 if result.ok else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
