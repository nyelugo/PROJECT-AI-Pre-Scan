"""A sample client book with real, findable companies.

An empty tool demos badly, and a book of invented names demos worse — every scan returns nothing and
the tool looks broken rather than careful. These are real companies whose AI use is publicly
documented, drawn from the evaluation ground truth, so a scan produces something a reviewer can
check against the source.

**Every domain here was verified by fetching it**, not by asking the resolver. That matters: asked
for "Clay", identity resolution returned `claywalker.com` — a country singer — which is precisely the
name-collision failure this system exists to catch, and it would have shipped inside the sample data
meant to demonstrate the system working.

The mix is deliberate. Roughly half these companies produce findings and half correctly produce
almost none. A demo that only shows the tool finding things does not show the harder and more
valuable behaviour, which is refusing to invent them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SampleClient:
    name: str
    domain: str
    note: str


SAMPLES: tuple[SampleClient, ...] = (
    # Rich footprint — publish their own AI, and deploy other people's. Good for showing a full
    # report, and for the provider/deployer distinction the compliance checker asks about first.
    SampleClient("Personio", "personio.de",
                 "HR software for European SMEs. Ships its own AI assistant and deploys others'."),
    SampleClient("WHOOP", "whoop.com",
                 "Wearables. WHOOP Coach is a dated, on-the-record GPT-4 launch."),
    SampleClient("Matterport", "matterport.com",
                 "Digital twins. Several named AI features on one product page."),

    # One clear published system each — tests precision rather than breadth.
    SampleClient("Gamma", "gamma.app",
                 "AI presentation tool. Also the case where a bare name resolves badly."),
    SampleClient("Clay", "clay.com",
                 "Go-to-market platform. Bare name resolves to a country singer — pin the domain."),
    SampleClient("Rocket Money", "rocketmoney.com",
                 "Personal finance. Support AI handling billing and account access."),

    # Vendor ships opt-in AI; whether these customers switched it on is published nowhere. The
    # correct output is undetermined plus a question — not a finding.
    SampleClient("Colten Care", "coltencare.co.uk",
                 "UK care homes. Uses an ATS whose vendor ships opt-in AI."),
    SampleClient("Liseberg", "liseberg.com",
                 "Swedish amusement park. Sector coverage is loud; the company itself is quiet."),
    SampleClient("RebelDot", "rebeldot.com",
                 "Romanian software house. Builds AI for clients — not the same as deploying it."),

    # Thin footprint. The correct result is close to nothing, and getting that right is the point.
    SampleClient("Keogh's Crisps", "keoghs.ie",
                 "Irish food producer. CEO on record that AI is not adding value at their level."),
    SampleClient("Barry's Tea", "barrystea.ie",
                 "Irish tea. Searching the name surfaces an AI chatbot built for a different firm."),
    SampleClient("Ballymaloe Foods", "ballymaloefoods.ie",
                 "Irish food producer. Sector AI commentary everywhere, company mentions nowhere."),
)


def as_import_lines() -> str:
    """The format the book's import box accepts."""
    return "\n".join(f"{s.name}, {s.domain}" for s in SAMPLES)
