#!/usr/bin/env python3
"""
Eval script for lnm.html — checks structure, JS logic, URL reachability, and content.
Run from the project root. Exits 0 if all checks pass, 1 if any fail.
"""
import sys
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser
from datetime import date, timedelta

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
WARN = "\033[33mWARN\033[0m"

failures = []
warnings = []

def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS}  {label}")
    else:
        print(f"  {FAIL}  {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)

def warn(label, detail=""):
    print(f"  {WARN}  {label}" + (f" — {detail}" if detail else ""))
    warnings.append(label)

# ──────────────────────────────────────────────
# Load HTML
# ──────────────────────────────────────────────
with open("lnm.html", "r") as f:
    html = f.read()

print("\n=== 1. STRUCTURE CHECKS ===")

# Basic page skeleton
check("DOCTYPE html present",      "<!DOCTYPE html>" in html)
check("charset UTF-8",             'charset="UTF-8"' in html or "charset=UTF-8" in html)
check("viewport meta",             'name="viewport"' in html)
check("theme-color meta",          'name="theme-color"' in html)
check("page title",                "<title>" in html and "LNM" in html)
check("manifest not linked",       'rel="manifest"' not in html,
      "lnm.html should not need manifest (only index.html does)")

# Header content
check("hdr-label contains USCG",   "USCG District 1" in html)
check("hdr-title Notice to Mariners", "Notice to Mariners" in html)
check("LNM Digest subtitle",       "LNM Digest" in html)

# Nav buttons
check("nav: ← Dashboard",         'href="index.html"' in html and "← Dashboard" in html)
check("nav: NYHOPS Images",        'href="nyhops.html"' in html and "NYHOPS Images" in html)
check("nav: NYHOPS Chart",         'href="nyhops-overlay.html"' in html and "NYHOPS Chart" in html)

# JS element IDs
check("id=lnm-week exists",        'id="lnm-week"' in html)
check("id=lnm-year exists",        'id="lnm-year"' in html)
check("id=lnm-cur exists",         'id="lnm-cur"' in html)
check("id=lnm-prev exists",        'id="lnm-prev"' in html)

print("\n=== 2. CARD STRUCTURE & INITIAL STATES ===")

# Extract card sections by parsing
card_pattern = re.compile(
    r'<div class="card-hdr"[^>]*>.*?<div class="card-t">.*?</div>\s*<span class="caret">(.*?)</span>.*?</div>\s*<div class="card-body(.*?)"',
    re.DOTALL
)

cards = card_pattern.findall(html)

# Also grab card titles
title_pattern = re.compile(r'<div class="card-t">.*?</div>', re.DOTALL)
raw_titles = title_pattern.findall(html)
titles = [re.sub(r'<[^>]+>', '', t).strip() for t in raw_titles]

expected_titles_fragments = [
    "This Week's LNM",
    "Active Notices",
    "NYC Harbor Filter",
    "NAVCEN Interactive Map",
    "Resources",
]
for frag in expected_titles_fragments:
    check(f"card title '{frag}' present",
          any(frag in t for t in titles))

# Check initial open/collapsed states via caret + class
# "This Week's LNM" and "Active Notices Digest" should be open (caret ▼, no collapsed)
# Others should be collapsed (caret ▲, has collapsed)

def card_state(card_title_frag):
    """Return ('open'|'collapsed'|'unknown', caret) for the card containing title fragment."""
    # Find the card block containing this title
    idx = html.find(card_title_frag)
    if idx == -1:
        return 'unknown', '?'
    # Look for the next card-body class after this title
    body_idx = html.find('class="card-body', idx)
    if body_idx == -1:
        return 'unknown', '?'
    body_decl = html[body_idx:body_idx+40]
    collapsed = 'collapsed' in body_decl
    # Find caret before body_idx
    caret_idx = html.rfind('<span class="caret">', idx, body_idx)
    caret_char = '?'
    if caret_idx != -1:
        m = re.search(r'<span class="caret">(.*?)</span>', html[caret_idx:caret_idx+40])
        if m:
            caret_char = m.group(1).strip()
    return ('collapsed' if collapsed else 'open'), caret_char

open_cards   = ["This Week's LNM", "Active Notices"]
closed_cards = ["NYC Harbor Filter", "NAVCEN Interactive Map", "Resources"]

for frag in open_cards:
    state, caret = card_state(frag)
    check(f"'{frag}' starts OPEN (no collapsed class)", state == 'open',
          f"got state={state}")
    check(f"'{frag}' caret is ▼", caret == '▼', f"got '{caret}'")

for frag in closed_cards:
    state, caret = card_state(frag)
    check(f"'{frag}' starts COLLAPSED", state == 'collapsed',
          f"got state={state}")
    check(f"'{frag}' caret is ▲", caret == '▲', f"got '{caret}'")

print("\n=== 3. CONTENT CHECKS ===")

# Callout about cumulative nature
check("cumulative LNM callout present",
      "self-contained" in html or "cumulative" in html.lower() or
      "repeat" in html.lower())

# Published Thursdays note
check("Published Thursdays note",  "Thursday" in html)

# NAVCEN fallback link
check("NAVCEN LNM index fallback link",
      "navcen.uscg.gov/local-notices-to-mariners-by-cg-district" in html)

# Chart numbers
expected_charts = ["12327", "12334", "12335", "12339", "12348", "12366", "12369"]
for cn in expected_charts:
    check(f"chart number {cn} present", cn in html)

# Geographic keywords
expected_kws = [
    "Upper Bay", "Lower Bay", "Kill Van Kull", "East River",
    "Hudson River", "Sandy Hook", "Jamaica Bay", "Gowanus", "Great Kills",
]
for kw in expected_kws:
    check(f"keyword '{kw}' present", kw in html)

# Active notices table
check("Great Kills Harbor in notices",  "Great Kills" in html)
check("Gowanus Canal in notices",       "Gowanus" in html)
check("ACTIVE badge present",           'badge-active' in html)

# Disclaimer in notices
check("notices disclaimer present",
      "Verify against" in html or "verify" in html.lower() or
      "authoritative" in html.lower())

# Footer
check("footer: USCG NAVCEN attribution", "USCG NAVCEN" in html or "navcen.uscg.gov" in html)
check("footer: not for navigation",
      "not for navigation" in html.lower() or "not for navigation" in html)

print("\n=== 4. JS LOGIC CHECK ===")

# Extract JS from the file
js_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not js_match:
    check("script block found", False)
else:
    js = js_match.group(1)
    check("script block found", True)
    check("getISOWeekData function defined", "getISOWeekData" in js)
    check("lnmUrl function defined",         "lnmUrl" in js)
    check("toggle function defined",         "toggle" in js)
    check("lnm-week updated in JS",          "lnm-week" in js)
    check("lnm-cur href set in JS",          "lnm-cur" in js)
    check("lnm-prev href set in JS",         "lnm-prev" in js)
    check("prior week computed (Date.now - 7)",
          "7 * 86400000" in js or "7*86400000" in js)

# Verify Python ISO week matches expected for today
today = date.today()
iso_year, iso_week, _ = today.isocalendar()
prior = today - timedelta(days=7)
p_year, p_week, _ = prior.isocalendar()

expected_cur_url  = f"https://www.navcen.uscg.gov/sites/default/files/pdf/lnms/lnm01{iso_week:02d}{iso_year}.pdf"
expected_prev_url = f"https://www.navcen.uscg.gov/sites/default/files/pdf/lnms/lnm01{p_week:02d}{p_year}.pdf"

print(f"\n  Today: {today}  →  ISO Week {iso_week} of {iso_year}")
print(f"  Expected current LNM URL:  {expected_cur_url}")
print(f"  Expected prior   LNM URL:  {expected_prev_url}")

check("lnmUrl pattern in JS matches expected format",
      "lnm01" in js and "pdf" in js)

print("\n=== 5. URL REACHABILITY (HEAD requests) ===")

def head_status(url):
    try:
        req = urllib.request.Request(url, method='HEAD',
            headers={'User-Agent': 'Mozilla/5.0 (compatible; LNM-eval/1.0)'})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR:{e}"

navcen_idx = "https://www.navcen.uscg.gov/local-notices-to-mariners-by-cg-district"
navcen_home = "https://www.navcen.uscg.gov/"

print(f"  Checking NAVCEN index page…")
status = head_status(navcen_idx)
if isinstance(status, int) and status < 400:
    check(f"NAVCEN LNM index reachable (HTTP {status})", True)
elif status == 403:
    warn(f"NAVCEN LNM index returned 403 (blocked by server, URL likely valid)")
else:
    check(f"NAVCEN LNM index reachable", False, f"HTTP {status}")

print(f"  Checking current LNM PDF (week {iso_week}/{iso_year})…")
status = head_status(expected_cur_url)
if isinstance(status, int) and status < 400:
    check(f"Current LNM PDF (week {iso_week}) reachable (HTTP {status})", True)
elif status == 403:
    warn(f"Current LNM PDF returned 403 (server blocks HEAD — URL likely valid, try in browser)")
elif status == 404:
    warn(f"Current LNM PDF returned 404 — may not be posted yet (today is {today.strftime('%A')})")
else:
    check(f"Current LNM PDF reachable", False, f"HTTP {status}")

print(f"  Checking prior LNM PDF (week {p_week}/{p_year})…")
status = head_status(expected_prev_url)
if isinstance(status, int) and status < 400:
    check(f"Prior LNM PDF (week {p_week}) reachable (HTTP {status})", True)
elif status == 403:
    warn(f"Prior LNM PDF returned 403 (server blocks HEAD — URL likely valid)")
elif status == 404:
    check(f"Prior LNM PDF (week {p_week}) reachable", False,
          f"404 — prior week should always be available")
else:
    check(f"Prior LNM PDF reachable", False, f"HTTP {status}")

print("\n=== 6. LOCAL SERVER RESPONSE ===")
try:
    with urllib.request.urlopen("http://localhost:8742/lnm.html", timeout=3) as r:
        body = r.read().decode()
        check("lnm.html served (HTTP 200)", r.status == 200)
        check("served content contains hdr-title", "hdr-title" in body)
        check("served content contains lnm-week", "lnm-week" in body)
except Exception as e:
    check("lnm.html served via local server", False, str(e))

print("\n=== 7. CROSS-PAGE NAV CHECKS ===")
for page, fname in [("index.html", "index.html"),
                    ("nyhops.html", "nyhops.html"),
                    ("nyhops-overlay.html", "nyhops-overlay.html")]:
    with open(fname) as f:
        pg = f.read()
    check(f"{page}: links to lnm.html", 'href="lnm.html"' in pg)

check("lnm.html: links back to index.html",    'href="index.html"' in html)
check("lnm.html: links to nyhops.html",        'href="nyhops.html"' in html)
check("lnm.html: links to nyhops-overlay.html",'href="nyhops-overlay.html"' in html)

# ──────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────
print("\n" + "="*50)
total_checks = len(failures) + sum(1 for _ in html.split("PASS")) - 1
print(f"FAILURES : {len(failures)}")
print(f"WARNINGS : {len(warnings)}")
if failures:
    print("\nFailed checks:")
    for f in failures:
        print(f"  ✗  {f}")
if warnings:
    print("\nWarnings (non-fatal):")
    for w in warnings:
        print(f"  △  {w}")
print()
sys.exit(0 if not failures else 1)
