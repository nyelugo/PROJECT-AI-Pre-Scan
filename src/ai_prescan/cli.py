"""Entry point.

    python -m ai_prescan "Fitzgerald Recruitment Ltd"          # fixture run, no network, no keys
    python -m ai_prescan "Company" --live                      # Phase 2
"""

from __future__ import annotations

import argparse
import sys

from . import browser, config, render
from .graph import scan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ai-prescan", description=__doc__)
    ap.add_argument("company")
    ap.add_argument("--live", action="store_true", help="use live tools (Phase 2)")
    ap.add_argument("--out", help="write the report here instead of stdout")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
