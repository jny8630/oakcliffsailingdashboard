# LNM Digest — Automated Filtering via GitHub Actions + Claude API

DRAFT — requires human review

## Current State

`lnm.html` is built and wired into the dashboard navigation. It provides:
- Smart weekly PDF link (auto-calculates ISO week number, handles Thu publishing lag)
- NYC Harbor chart number filter guide (NOAA charts 12327, 12334, 12335, 12339, 12348, 12366, 12369)
- Geographic keyword list for scanning the PDF manually
- Links to NAVCEN, Light List, Coast Pilot

**The gap:** The "Active Notices" card currently has hardcoded example data (Great Kills, Gowanus).
It needs to be replaced with real, filtered, current data.

`eval_lnm.py` — existing QA script that validates HTML structure, JS logic, and USCG PDF URL reachability.
Run from project root: `python3 eval_lnm.py`

---

## The Problem

USCG District 1 LNM covers Maine to New Jersey. The weekly PDF runs 30-60+ pages with
dozens of geographic entries. Only ~5-10% is relevant to our sailing area.
The PDF has no public API. It must be fetched and parsed.

---

## Our Sailing Area (Geographic Filter Boundaries)

Include notices for:
- **Upper and Lower New York Bay** — Verrazzano Bridge north to Brooklyn Bridge
- **The Anchorage / The Flats** — south of Governors Island
- **Governors Island** and the surrounding waters
- **Hudson River** — Battery north to approximately W 60th St
- **East River** — south of Brooklyn Bridge only (Buttermilk Channel, Red Hook)
- **Kill Van Kull / Arthur Kill** — Bayonne and NJ approaches, used for circumnavigation
- **Gravesend Bay / Coney Island** — Lower Bay approaches
- **Ambrose Channel** — main shipping channel, Lower Bay
- **Erie Basin / Red Hook** — Brooklyn waterfront south of BK Bridge
- **Great Kills Harbor** — Staten Island, frequently visited

Exclude (not our waters):
- East River north of Brooklyn Bridge (Hell Gate, Harlem River, etc.)
- Hudson River north of W 60th St
- Long Island Sound
- Connecticut, Rhode Island, Maine waters

NOAA chart numbers for our area: 12327, 12334, 12335, 12339, 12348

---

## Proposed Solution: GitHub Actions + Claude API

### Architecture

```
GitHub Actions (scheduled: Friday 10am ET)
  → Download current week's LNM PDF from NAVCEN
  → Send PDF text to Claude API (Haiku — ~$0.01/run)
  → Claude extracts and filters NYC Harbor notices as structured JSON
  → Commit lnm_current.json to repo
  → lnm.html reads lnm_current.json on load and renders Active Notices card
```

The frontend stays zero-build and zero-server. GitHub Actions is the only "build" step.

### Files to Create

1. `.github/workflows/lnm-update.yml` — scheduled workflow
2. `scripts/fetch_lnm.py` — downloads PDF, extracts text, calls Claude API, writes JSON
3. `lnm_current.json` — output file read by lnm.html (committed to repo)
4. `scripts/eval_lnm_action.py` — tests the workflow end-to-end

### JSON Output Schema

```json
{
  "week": 19,
  "year": 2026,
  "generated_utc": "2026-05-08T15:23:00Z",
  "pdf_url": "https://www.navcen.uscg.gov/sites/default/files/pdf/lnms/lnm01192026.pdf",
  "notices": [
    {
      "id": "2026-19-001",
      "location": "Buttermilk Channel",
      "chart": "12334",
      "summary": "Shoaling reported on eastern edge of channel near Governors Island ferry terminal",
      "status": "ACTIVE",
      "since": "2026-04",
      "relevant_area": "East River / Governors Island"
    }
  ],
  "areas_checked": ["Upper Bay", "Lower Bay", "Governors Island", "Hudson River", "..."],
  "disclaimer": "AI-extracted from USCG D1 LNM. Verify against source PDF before underway."
}
```

### Claude API Prompt (sketch)

```
You are processing a USCG District 1 Local Notice to Mariners PDF.
Extract all notices relevant to the following area: [geographic boundaries above].
For each relevant notice return: location, NOAA chart number, one-sentence summary,
status (ACTIVE/TEMP/CANCELLED), and effective date.
Return as JSON array. If no relevant notices, return empty array.
Exclude anything north of Brooklyn Bridge on East River, north of W 60th St on Hudson,
or in Long Island Sound / Connecticut waters.
```

### Workflow Schedule

```yaml
on:
  schedule:
    - cron: '0 15 * * 5'  # Friday 3pm UTC = 11am ET (after Thursday publication)
  workflow_dispatch:       # allow manual trigger
```

### Required GitHub Secret

`ANTHROPIC_API_KEY` — add in repo Settings → Secrets and variables → Actions

---

## Testing Plan

### Unit tests (extend eval_lnm.py or new file)
- [ ] PDF download succeeds for current week URL
- [ ] PDF text extraction produces non-empty output
- [ ] Claude API returns valid JSON matching schema
- [ ] Empty array returned for clearly out-of-area content
- [ ] lnm.html correctly renders lnm_current.json (check DOM after load)
- [ ] lnm.html gracefully handles missing/stale lnm_current.json

### Integration test (eval_lnm_action.py)
- [ ] Run full fetch_lnm.py end-to-end against real current PDF
- [ ] Validate JSON output schema
- [ ] Spot-check: known active notice appears in output
- [ ] HEAD-check PDF URL before calling Claude (avoid wasted API call)

### Regression guard
- [ ] If lnm_current.json is more than 10 days old, show staleness warning in UI
- [ ] If JSON is missing, fall back to "smart link only" mode (no fake data)

---

## What lnm.html Needs to Change

1. Remove hardcoded "Active Notices" table (Great Kills / Gowanus examples)
2. Add JS fetch of `lnm_current.json` on page load
3. Render notices dynamically into the Active Notices card
4. Show "Last updated: Week X · AI-extracted" + link to source PDF
5. Graceful fallback if JSON missing: show "PDF link only" message

---

## Resume Instructions

Branch: `feature/lnm-digest`

To pick this up in a new session:
1. Read this file
2. Read `lnm.html` (the page to be updated)
3. Read `eval_lnm.py` (existing QA script)
4. Build `scripts/fetch_lnm.py` first — get it working locally with a real PDF
5. Then wire up `.github/workflows/lnm-update.yml`
6. Then update `lnm.html` to consume `lnm_current.json`
7. Run the full test suite before opening a PR to main

The user's geographic filter boundaries are defined above — use them precisely in the Claude prompt.
Always link to the source PDF. Always show a disclaimer. Never display stale data silently.
