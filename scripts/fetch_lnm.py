#!/usr/bin/env python3
"""
fetch_lnm.py — Download current USCG D1 LNM PDF, extract Oyster Bay / Long Island Sound notices
using keyword filtering and regex parsing (no LLM or external API required).

Usage:
  python3 scripts/fetch_lnm.py

Requirements: requests, pdfplumber  (see scripts/requirements.txt)
"""

import json
import os
import re
import sys
import io
from datetime import datetime, timezone, date, timedelta

import requests
import pdfplumber

# ── Config ─────────────────────────────────────────────────────────────────────

OUTPUT_FILE       = os.path.join(os.path.dirname(__file__), "..", "lnm_current.json")
LNM_BASE          = "https://www.navcen.uscg.gov/sites/default/files/pdf/lnms/"
MAX_WEEKS_BACK    = 4
SUMMARY_MAX_CHARS = 400

# Section header terms that identify Oyster Bay / Long Island Sound relevant pages
NYC_SECTION_TERMS = [
    "oyster bay",
    "long island sound",
    "western long island sound",
    "cold spring harbor",
    "huntington bay",
    "manhasset bay",
    "hempstead harbor",
    "centre island",
    "lloyd neck",
    "cold spring",
    "port jefferson",
    "northport bay",
    "nissequogue",
    "stony brook",
    "smithtown bay",
    "sector long island sound",
    "sector new york",
    "east river",
    "throgs neck",
    "city island",
]

# Body text terms for secondary page check (kept narrow to reduce false positives)
NYC_BODY_TERMS = [
    "oyster bay harbor",
    "long island sound",
    "cold spring harbor",
    "huntington bay",
    "lloyd harbor",
    "centre island",
    "hempstead harbor",
    "manhasset bay",
    "throgs neck",
    "port jefferson harbor",
]

# Terms that identify clearly non-relevant locations to exclude after filtering
NON_NYC_EXCLUSIONS = [
    "boston", "cape ann", "eastern point yacht", "broad sound",
    "long ledge", "egg rock", "block island", "new england",
    "southeastern new england", "cape cod", "nantucket",
    "maine", "rhode island", "massachusetts",
    "vermont", "new hampshire", "gardiners bay",
    "buzzards bay", "vineyard sound", "narragansett",
    "apponaganset", "mount hope", "mount desert",
    "ambrose channel", "kill van kull", "arthur kill",
    "raritan bay", "sheepshead bay", "jamaica bay",
    "great kills", "buttermilk channel", "governors island",
    "verrazzano", "verrazano", "upper bay", "lower bay",
    "newark bay", "staten island",
]

# Lines/pages to strip as boilerplate
BOILERPLATE = [
    "maritime safety information",
    "navigation center",
    "local notice to mariners",
    "federal discrepancies",   # buoy status tables — not actionable notices
]

# Column-header lines that signal non-actionable table rows
TABLE_HEADERS = [
    "name llnr status",
    "title subcategory",
    "subcategory description",
    "llnr name",
    "light list",
]

# Regex patterns
STATUS_RE  = re.compile(r'\b(NEW|TEMPORAR\w*|CANCEL\w*|UPDATED?|PERMANENT)\b', re.IGNORECASE)
CHART_RE   = re.compile(r'\bCharts?\s*(?:No\.?\s*)?(\d{4,5})\b', re.IGNORECASE)
DATE_RE    = re.compile(
    r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}'
    r'|\d{4}-\d{2}-\d{2})\b',
    re.IGNORECASE,
)
TIMESTAMP_RE     = re.compile(r'^\d{1,2}/\d{1,2}/\d{2,4},?\s+\d+:\d+', re.MULTILINE)
FIELD_LABEL_RE   = re.compile(
    r'^(?:Title|Description|Subcategory|Action|Effective|Chart[s]?|Location|From|To):\s*\S*\s*',
    re.IGNORECASE | re.MULTILINE,
)
# Strip slash-delimited category paths like "Marine General/Marine Construction/..."
CATEGORY_PATH_RE = re.compile(r'[\w\s(),-]{3,}/[\w\s(),-]{3,}(?:/[\w\s(),-]{3,})*')
# ISO timestamps embedded in text
ISO_TIMESTAMP_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z')

# ── Helpers ────────────────────────────────────────────────────────────────────

def lnm_url(week, year):
    return f"{LNM_BASE}lnm01{week:02d}{year}.pdf"

def week_year_for_offset(days_back=0):
    d = date.today() - timedelta(days=days_back)
    iso = d.isocalendar()
    return iso[1], iso[0]

def download_pdf(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; LNM-fetcher/1.0)"}
    r = requests.get(url, headers=headers, timeout=60)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.content

def extract_pages(pdf_bytes):
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return [p.extract_text() or "" for p in pdf.pages]

def clean_page(page_text):
    lines = page_text.split("\n")
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            out.append("")
            continue
        if TIMESTAMP_RE.match(s):
            continue
        if any(b in s.lower() for b in BOILERPLATE):
            continue
        out.append(line)
    return "\n".join(out).strip()

def get_section_header(page_text):
    table_skip = set(TABLE_HEADERS)
    for line in page_text.split("\n"):
        s = line.strip()
        if not s:
            continue
        sl = s.lower()
        if any(b in sl for b in BOILERPLATE):
            continue
        if TIMESTAMP_RE.match(s):
            continue
        if any(t in sl for t in table_skip):
            continue
        return s
    return ""

def is_ob_relevant(header):
    h = header.lower()
    return any(term in h for term in NYC_SECTION_TERMS)

def page_contains_ob_content(page_text):
    body = page_text.lower()
    return any(t in body for t in NYC_BODY_TERMS)

def is_non_ob_location(location):
    ll = location.lower()
    return any(t in ll for t in NON_NYC_EXCLUSIONS)

# ── Notice parsing ─────────────────────────────────────────────────────────────

def map_status(raw):
    r = raw.upper()
    if r.startswith("CANCEL"):
        return "CANCELLED"
    if r.startswith("TEMPORAR"):
        return "TEMPORARY"
    return "ACTIVE"

def clean_summary(text):
    """Strip field labels, category paths, ISO timestamps, then truncate."""
    t = FIELD_LABEL_RE.sub("", text)
    t = ISO_TIMESTAMP_RE.sub("", t)
    t = CATEGORY_PATH_RE.sub("", t)
    # Strip table column-header lines embedded in notice text
    for hdr in TABLE_HEADERS + ["additional msi categories"]:
        t = re.sub(r'(?im)^.*' + re.escape(hdr) + r'.*$\n?', '', t)
    # Decode HTML entities
    t = t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Strip coordinate fragments (decimal and DMS formats, with or without leading digit)
    t = re.sub(r'[\d.]+[\-\d.]*[°\'"]\s*[NSEW]?[\s/,;]*', '', t)
    # Strip leading orphaned punctuation/date fragments left by field removals
    t = re.sub(r'^[\s:;,\.]+', '', t)
    # Collapse excess whitespace left by removals
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    t = t.strip()
    if len(t) > SUMMARY_MAX_CHARS:
        cut = t[:SUMMARY_MAX_CHARS]
        last_space = cut.rfind(" ")
        t = (cut[:last_space] if last_space > 0 else cut) + "…"
    return t

_CATPATH_SEP = re.compile(r'\s+\w{3,}/\w{3,}')   # space + word/word = category path start
_DESC_VERB   = re.compile(
    r'\b(?:Construction|Dredging|Survey|Repair|Demolition|Mariners|Will|Has|Have|Is|Are)\b',
    re.IGNORECASE,
)
_LOC_SUFFIX  = re.compile(
    r'\s+(?:Main|General|Marine|Additional|Hazards|To|Submerged|Lands|LAA|RNA|Reported)\s*$',
    re.IGNORECASE,
)

def extract_location(header_line):
    """
    Return the geographic part of a section header.
    'Main Channel - East River Main Marine General/Marine Construction...' -> 'Main Channel - East River'
    'Kill Van Kull - Newark Bridges Construction will commence...'         -> 'Kill Van Kull - Newark Bridges'
    """
    loc = header_line
    # Trim at date range marker "From:" or "From "
    loc = re.split(r'\s+From[:\s]', loc, flags=re.IGNORECASE)[0]
    # Trim at first word/word category path separator
    m = _CATPATH_SEP.search(loc)
    if m:
        loc = loc[:m.start()]
    # Trim at description verbs (indicates notice body, not location name)
    m2 = _DESC_VERB.search(loc)
    if m2:
        loc = loc[:m2.start()]
    # Iteratively strip trailing structural modifier words
    for _ in range(6):
        trimmed = _LOC_SUFFIX.sub('', loc).strip(' -,')
        if trimmed == loc:
            break
        loc = trimmed
    loc = loc.strip(' -,')
    return loc[:60] if loc else header_line[:60]

def extract_notice_fields(block_text):
    """
    Extract status, chart, since, and summary from a single notice block.
    Returns a dict or None if the block has no usable content.
    """
    text = block_text.strip()
    if len(text) < 40:
        return None

    # Skip blocks that are purely table column headers
    first_line = text.split("\n")[0].lower()
    if any(t in first_line for t in TABLE_HEADERS):
        return None

    summary = clean_summary(text)
    if len(summary) < 20:
        return None

    # Status — prefer explicit Action: field, fall back to keyword scan
    status = "ACTIVE"
    action_m = re.search(r'(?:^|\b)Action:\s*(\w+)', text, re.IGNORECASE | re.MULTILINE)
    if action_m:
        status = map_status(action_m.group(1))
    else:
        m = STATUS_RE.search(text)
        if m:
            status = map_status(m.group(1))

    # Chart number
    chart = None
    cm = CHART_RE.search(text)
    if cm:
        chart = cm.group(1)

    # Effective date — prefer explicit Effective: label, then first ISO/natural date
    since = None
    eff_m = re.search(r'From:\s*(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
    if eff_m:
        since = eff_m.group(1)
    else:
        dm = DATE_RE.search(text)
        if dm:
            since = dm.group(1)

    return {"chart": chart, "summary": summary, "status": status, "since": since}

def parse_page_notices(page_text):
    """
    Parse one filtered page into notice dicts, each with a location field.
    """
    raw_header = get_section_header(page_text)
    location   = extract_location(raw_header) if raw_header else "Oyster Bay"

    # Drop pages whose resolved location is clearly outside Oyster Bay / LIS area
    if is_non_ob_location(location):
        return []

    cleaned = clean_page(page_text)
    blocks  = re.split(r'\n\s*\n', cleaned)

    notices = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        sl = block.lower()
        if any(b in sl for b in BOILERPLATE):
            continue
        # Skip blocks that are short and consist only of table column headers
        first_line = block.split("\n")[0].lower()
        if len(block) < 120 and any(t in first_line for t in TABLE_HEADERS):
            continue

        fields = extract_notice_fields(block)
        if fields:
            fields["location"] = location
            notices.append(fields)

    # Deduplicate on summary prefix (can occur on continuation pages)
    seen, unique = set(), []
    for n in notices:
        key = n["summary"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(n)

    # Drop notices whose summary references clearly non-relevant locations
    unique = [
        n for n in unique
        if not any(t in n["summary"].lower() for t in NON_NYC_EXCLUSIONS)
    ]

    return unique

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # Find latest text-based LNM
    pages = week = year = url = None
    skipped = []
    for weeks_back in range(0, MAX_WEEKS_BACK * 7 + 1, 7):
        w, y = week_year_for_offset(days_back=weeks_back)
        u = lnm_url(w, y)
        print(f"Trying week {w}/{y}: {u}")
        data = download_pdf(u)
        if data is None:
            print("  404 — skipping")
            skipped.append({"week": w, "year": y, "reason": "not_posted"})
            continue
        pg = extract_pages(data)
        text_pages = [p for p in pg if p.strip()]
        if not text_pages:
            print("  Scanned PDF — skipping")
            skipped.append({"week": w, "year": y, "reason": "scanned_pdf"})
            continue
        print(f"  OK — {len(data):,} bytes, {len(text_pages)} text pages")
        pages, week, year, url = pg, w, y, u
        break

    if not pages:
        print("ERROR: No text-based LNM found in the last 4 weeks.", file=sys.stderr)
        sys.exit(1)

    # Filter and parse
    all_notices   = []
    relevant_count = 0
    for page in pages:
        header = get_section_header(page)
        if not is_ob_relevant(header) and not page_contains_ob_content(page):
            continue
        relevant_count += 1
        all_notices.extend(parse_page_notices(page))

    print(f"Parsed {relevant_count} candidate pages → {len(all_notices)} notice(s)")

    output = {
        "week":          week,
        "year":          year,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pdf_url":       url,
        "model":         "text-parser",
        "skipped":       skipped,
        "notices":       all_notices,
        "disclaimer":    (
            "Extracted from USCG D1 LNM via keyword filtering. "
            "Verify against source PDF before underway."
        ),
    }

    out_path = os.path.abspath(OUTPUT_FILE)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Written: {out_path}")

if __name__ == "__main__":
    main()
