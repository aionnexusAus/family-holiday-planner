#!/usr/bin/env python3
"""Merge the research JSON and write a single offline HTML planner."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "destinations"
OUT_JSON = ROOT / "destinations.json"
OUT_DIR = ROOT.parent
OUT_HTML = OUT_DIR / "family_holiday_planner.html"
OUT_INDEX = OUT_DIR / "index.html"
TEMPLATE = ROOT / "planner_template.html"

REQUIRED = [
    "id", "pool", "name", "regionLabel", "regions", "summary", "why",
    "scores", "labels", "days", "sources", "image", "visaAu", "visaIn",
]


def load():
    trip = json.loads((ROOT / "trip.json").read_text())
    timing = json.loads((ROOT / "timing.json").read_text())
    method = json.loads((ROOT / "method.json").read_text())
    places = []
    for path in sorted(DEST.glob("*.json")):
        item = json.loads(path.read_text())
        missing = [key for key in REQUIRED if key not in item]
        if missing:
            raise SystemExit(f"{path.name} missing {missing}")
        places.append(item)
    ids = [item["id"] for item in places]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate destination ids")
    return {
        "trip": trip,
        "timing": timing,
        "method": method,
        "destinations": places,
    }


def main():
    data = load()
    OUT_JSON.write_text(json.dumps(data["destinations"], ensure_ascii=False, indent=2) + "\n")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    html = TEMPLATE.read_text()
    if "/*__DATA__*/ null" not in html:
        raise SystemExit("Template placeholder missing")
    html = html.replace("/*__DATA__*/ null", blob)
    OUT_HTML.write_text(html)
    OUT_INDEX.write_text(html)
    print(f"Wrote {OUT_JSON} ({len(data['destinations'])} places)")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size} bytes)")
    print(f"Wrote {OUT_INDEX}")


if __name__ == "__main__":
    main()
