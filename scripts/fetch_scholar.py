"""
Fetch Google Scholar profile metrics and publication list for Camillo Quattrocchi
and write them to scholar-data.json in the repository root.

Run by the GitHub Actions workflow .github/workflows/update-scholar.yml.
If Google Scholar can't be reached or returns no publications, the existing
scholar-data.json is left untouched so the site never shows an empty list.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

SCHOLAR_ID = "z1LNVfMAAAAJ"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "scholar-data.json")
CITATION_URL = "https://scholar.google.com/citations?view_op=view_citation&hl=en&citation_for_view={}"


def venue_from_citation(citation: str, year: str) -> str:
    """Scholar's short citation looks like 'European Conference on Computer Vision, 2024'.
    Drop the trailing year and volume/page details to keep just the venue name."""
    if not citation:
        return ""
    v = citation.strip()
    if "arxiv" in v.lower():
        return "arXiv preprint"
    v = re.sub(r",?\s*\b(19|20)\d{2}\b\s*$", "", v)          # trailing year
    v = re.sub(r"\s+\d+\s*\(\d+\)(,\s*[\d-]+)?$", "", v)    # "12 (3), 45-67"
    v = re.sub(r",\s*[\d-]+$", "", v)                         # trailing pages
    v = re.sub(r"\s*\(\d+\)$", "", v)                           # trailing "(5)"
    return v.strip(" ,")


def main():
    try:
        from scholarly import scholarly
    except ImportError as exc:
        print(f"ERROR: could not import scholarly: {exc!r}")
        sys.exit(1)

    print(f"Fetching Google Scholar profile for ID: {SCHOLAR_ID}")
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author = scholarly.fill(author, sections=["basics", "indices", "publications"])
    except Exception as exc:  # network errors, captchas, rate limits
        print(f"WARNING: Google Scholar not reachable ({exc!r}); keeping existing data.")
        return

    publications = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        year = str(bib.get("pub_year", "") or "")
        pub_id = pub.get("author_pub_id", "")
        publications.append({
            "title":       bib.get("title", ""),
            "year":        year,
            "venue":       bib.get("venue") or venue_from_citation(bib.get("citation", ""), year),
            "authors":     bib.get("author", ""),
            "cited_by":    pub.get("num_citations", 0),
            "scholar_url": pub.get("pub_url") or (CITATION_URL.format(pub_id) if pub_id else ""),
        })

    if not publications:
        print("WARNING: no publications returned; keeping existing data.")
        return

    # Newest first (publications without a year go last)
    publications.sort(key=lambda p: int(p["year"]) if p["year"].isdigit() else 0, reverse=True)

    data = {
        "fetched_at":   datetime.now(timezone.utc).isoformat(),
        "author":       author.get("name", ""),
        "citations":    author.get("citedby", 0),
        "hindex":       author.get("hindex", 0),
        "i10index":     author.get("i10index", 0),
        "publications": publications,
    }

    out_path = os.path.abspath(OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {len(publications)} publications to {out_path}")
    print(f"  citations={data['citations']}, h-index={data['hindex']}, i10-index={data['i10index']}")


if __name__ == "__main__":
    main()
