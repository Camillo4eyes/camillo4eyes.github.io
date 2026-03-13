"""
Fetch Google Scholar profile metrics and publication list for Camillo Quattrocchi
and write them to scholar-data.json in the repository root.

Run by the GitHub Actions workflow .github/workflows/update-scholar.yml.
"""

import json
import os
import sys
from datetime import datetime, timezone

SCHOLAR_ID = "z1LNVfMAAAAJ"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "scholar-data.json")


def main():
    try:
        from scholarly import scholarly
    except ImportError:
        print("ERROR: 'scholarly' package not installed. Run: pip install scholarly")
        sys.exit(1)

    print(f"Fetching Google Scholar profile for ID: {SCHOLAR_ID}")
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])

    citations  = author.get("citedby", 0)
    hindex     = author.get("hindex", 0)
    i10index   = author.get("i10index", 0)
    name       = author.get("name", "")

    publications = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        pub_entry = {
            "title":    bib.get("title", ""),
            "year":     bib.get("pub_year", ""),
            "venue":    bib.get("venue", ""),
            "authors":  bib.get("author", ""),
            "cited_by": pub.get("num_citations", 0),
            "scholar_url": pub.get("pub_url", ""),
        }
        publications.append(pub_entry)

    # Sort newest first (publications without year go last)
    publications.sort(
        key=lambda p: int(p["year"]) if p.get("year") and str(p["year"]).isdigit() else 0,
        reverse=True,
    )

    data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "author":     name,
        "citations":  citations,
        "hindex":     hindex,
        "i10index":   i10index,
        "publications": publications,
    }

    out_path = os.path.abspath(OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(publications)} publications to {out_path}")
    print(f"  citations={citations}, h-index={hindex}, i10-index={i10index}")


if __name__ == "__main__":
    main()
