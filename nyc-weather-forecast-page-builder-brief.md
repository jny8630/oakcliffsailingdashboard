# Builder Brief: New York City Sailing Dashboard Weather Forecast Page

## Overview

This brief defines the requirements for adding **one additional HTML page** to an existing New York City sailing dashboard. The existing dashboard already includes current wind speed, wind direction, gusts, and related sailing-condition information on another page, so this new page should focus specifically on the **weather forecast outlook** rather than duplicating wind data.[cite:73]

The page should help a user answer practical questions such as: what will the weather feel like over the next few hours, is rain likely, is there meaningful thunderstorm risk, how cloudy will it be, and what does the recent radar show moving into the harbor area.[cite:73][cite:30][cite:59]

The phase-one build must use only **free, documented, no-account sources** and should be implemented as a stable standalone HTML page that plugs into the existing dashboard.[cite:78][cite:59]

## Product Context

This page is part of an existing **New York City sailing conditions dashboard** and should visually and structurally fit into that broader product. It is not a generic weather page and it is not a separate app concept; it is a focused extension of the current sailing dashboard experience.[cite:73]

The relevant sailing area is **New York City Harbor / New York Bay**, broadly spanning from the Brooklyn Bridge to the Verrazzano-Narrows Bridge, including the Statue of Liberty area, the New Jersey waterfront, and the Hudson River south of roughly 50th Street in Manhattan.[cite:73]

For phase one, the page should use **one fixed representative forecast point** for this harbor area rather than attempting multi-point averaging or zone blending, while the radar card can still show the broader harbor region visually.[cite:73][cite:59]

## Goal

Build one weather forecast page that emphasizes short-range forecast interpretation over the next **4, 8, or 12 hours** using a single forecast card with range selectors and a separate radar card.[cite:73][cite:143][cite:59]

This page should not emphasize sailing-performance metrics such as current wind because those already exist elsewhere. Instead, it should prioritize weather conditions that influence comfort and safety, including temperature, precipitation, thunderstorm risk, cloud cover, visibility, and overall condition summary.[cite:73][cite:30]

## Phase-One Data Sources

### Forecast Source

Use **Open-Meteo** as the only forecast source in phase one. Open-Meteo provides free forecast data without requiring an API key for standard use and supports hourly forecast variables, forecast-hour limits, and local timezone handling.[cite:78][cite:73]

### Radar Source

Use **Rain Viewer** as the only radar source in phase one. Rain Viewer’s documented weather maps API supports website/application integration and provides past radar frames for the previous 2 hours in 10-minute intervals.[cite:59][cite:58]

### Explicitly Out of Scope

Do **not** use Google Weather API, AccuWeather, scraped consumer weather pages, or undocumented future-radar sources in phase one.[cite:79][cite:131][cite:138]

## User Experience Requirements

The page should contain two primary UI modules:

1. **Forecast card** with a selector for Next 4 hours, Next 8 hours, and Next 12 hours.[cite:143][cite:73]
2. **Radar card** labeled as observed radar for the last 2 hours.[cite:59]

An optional compact source/status footer may also be included to show last refresh times and source labels if that improves clarity without cluttering the UI.[cite:118][cite:59]

## Forecast Card Specification

### Core Interaction

The forecast card should use one consistent layout and allow the user to switch between three time windows:

- Next 4 hours
- Next 8 hours
- Next 12 hours

These selector states must all be backed by a **single Open-Meteo forecast request covering 12 hours**, and the frontend should slice the already-fetched data client-side rather than making a separate network request for each selector state.[cite:73][cite:143]

### Resolution

In phase one, render the forecast at **hourly resolution only**. Although Open-Meteo supports sub-hourly forecasting in broader documentation, hourly rendering is the stable and simpler phase-one default for this page.[cite:76][cite:73]

### Required Forecast Fields

The forecast card must include the following fields from Open-Meteo:

- `temperature_2m`[cite:73]
- `precipitation`[cite:73]
- `precipitation_probability`[cite:73]
- `cloud_cover`[cite:73]
- `visibility`[cite:73]
- `weather_code`[cite:73]

### Optional Forecast Field

Include `thunderstorm_probability` **when available** for the selected model/data source. If it is not available, the layout must degrade gracefully by either hiding that row/metric or replacing it with a clear “not available” state rather than breaking the card design.[cite:30][cite:73]

### Information Hierarchy

Temperature should be visually prominent in every selector state because it was explicitly requested as a core forecast element.[cite:73]

The recommended visual priority order is:

1. Temperature.[cite:73]
2. Weather summary / icon derived from `weather_code`.[cite:73]
3. Precipitation probability.[cite:73]
4. Thunderstorm probability when available.[cite:30]
5. Cloud cover.[cite:73]
6. Visibility.[cite:73]
7. Precipitation amount as a secondary supporting value.[cite:73]

### Plain-Language Summary

The top of the forecast card should include a short deterministic summary generated from the forecast values, not from another model or API. Example summary states could include:

- Generally fair conditions.[cite:73]
- Rain likely.[cite:73]
- Reduced visibility.[cite:73]
- Thunderstorm caution.[cite:30]
- Mostly cloudy but likely dry.[cite:73]

This summary should be rule-based and implemented in client-side logic.[cite:73]

### Weather Code Mapping

Implement a local mapping table from Open-Meteo `weather_code` values to:

- short condition label,
- icon or inline SVG,
- severity styling if helpful.[cite:73][cite:30]

This avoids reliance on an extra account, remote weather icon dependency, or undocumented translation layer.[cite:73]

## Forecast API Requirements

Use one Open-Meteo forecast request with parameters conceptually equivalent to:

- `latitude=<fixed harbor representative point>`
- `longitude=<fixed harbor representative point>`
- `timezone=auto`
- `hourly=temperature_2m,precipitation,precipitation_probability,thunderstorm_probability,cloud_cover,visibility,weather_code`
- `forecast_hours=12`[cite:73][cite:143][cite:30]

The implementation should ensure that all timestamps are rendered in **local New York time**, not UTC. Open-Meteo documents that `timezone=auto` resolves timestamps to the local timezone based on coordinates rather than returning GMT/UTC time by default.[cite:73][cite:90]

During sailing season this will generally mean Eastern Daylight Time, while outside that period it will resolve to Eastern Standard Time as applicable.[cite:73]

## Forecast Freshness Metadata

The forecast card must display forecast freshness information once per card, not once per selector state, because all selector views derive from the same forecast payload and model context.[cite:118][cite:73]

Open-Meteo documents model-update metadata including:

- `last_run_initialisation_time`
- `last_run_modification_time`
- `last_run_availability_time`
- `update_interval_seconds`
- `temporal_resolution_seconds`[cite:118]

The page should display values such as:

- Model run time.[cite:118]
- Available on API time.[cite:118]
- Typical update interval.[cite:118]
- Estimated next update time.[cite:118]

The “next update” value must be explicitly labeled as an **estimate**, because Open-Meteo documents update cadence but does not guarantee an exact future publish time in the sense of an SLA.[cite:118]

Open-Meteo also advises waiting about 10 minutes after `last_run_availability_time` to ensure the latest run is consistently available across servers, so any refresh logic should account for that recommendation.[cite:118]

## Radar Card Specification

Use Rain Viewer’s documented weather maps API for the radar card.[cite:59]

The radar card should include:

- an interactive map centered on the New York Harbor area,[cite:59]
- animated radar playback,[cite:59]
- clear timestamp for the active frame,[cite:59]
- optional play/pause control,[cite:59]
- optional previous/next frame controls if desired.[cite:59]

The radar card must be labeled clearly as something equivalent to:

- “Observed radar — last 2 hours” or
- “Observed radar, past 2 hours, 10-minute steps.”[cite:59]

The implementation must use only Rain Viewer’s **documented past radar frames** in phase one. The builder must not assume that forward nowcast frames are available just because older examples or related tools reference broader capabilities.[cite:59][cite:60][cite:95]

The card should also state clearly that it is **not a future precipitation forecast**.[cite:59]

## Future Radar / MinuteCast-Style Forecasting

Forward-looking 90-minute precipitation nowcast is **out of scope for phase one**. AccuWeather’s MinuteCast exists as a proprietary minute-by-minute precipitation forecast product, but it is part of AccuWeather’s own API ecosystem and is not the free, no-account, phase-one path for this page.[cite:131][cite:138]

The implementing model should not try to replicate or scrape AccuWeather behavior and should not build against undocumented sources for future radar or minute-level nowcast.[cite:131][cite:138]

## Technical Constraints

- Build as **one additional HTML page** within the existing dashboard.[cite:73]
- Keep it compatible with a static frontend architecture.[cite:73]
- No new vendor accounts for phase one.[cite:78][cite:59]
- No scraping.[cite:138]
- No server-side proxy required unless the existing dashboard already has one and the builder independently decides it is beneficial.[cite:73]
- Selector changes should not trigger new forecast fetches if the initial 12-hour payload is already loaded.[cite:143]
- Forecast and radar should fail independently so one data-source outage does not blank the whole page.[cite:73][cite:59]

## Design Freedom for the Builder

The builder should have freedom to make sensible design and implementation choices so long as the functional scope remains unchanged. In particular, the builder may choose:

- exact card layout,[cite:73]
- visual styling and palette,[cite:73]
- icon system or inline SVG strategy,[cite:73]
- responsive arrangement for mobile vs desktop,[cite:73]
- map library for rendering the radar card, provided it is lightweight and compatible with Rain Viewer tiles.[cite:59][cite:95]

The brief is intentionally specific about **what the page must do**, but not overly prescriptive about **how the page must look** or the exact component arrangement, as long as the information hierarchy remains clear and the final result fits the existing sailing dashboard aesthetically.[cite:73]

## Recommended Representative Forecast Point

For phase one, the implementation should select **one representative forecast coordinate** within the New York Harbor sailing area rather than trying to average a wide operating area.[cite:73]

A sensible default would be a central harbor point near the Statue of Liberty / Governors Island area so that the forecast remains relevant to most club users across Upper and Lower Bay.[cite:73]

## Error Handling and Fallbacks

### Forecast Errors

If Open-Meteo is unavailable, display a clear forecast-card fallback state such as “Forecast temporarily unavailable” while leaving the radar card functional.[cite:73]

### Radar Errors

If Rain Viewer is unavailable, display a radar-card fallback state such as “Radar temporarily unavailable” while leaving the forecast card functional.[cite:59]

### Missing Optional Metrics

If `thunderstorm_probability` is not present for the chosen data source/model, do not fail the layout; instead hide the metric or show a subtle unavailable state.[cite:30][cite:73]

### Missing Metadata

If forecast freshness metadata cannot be resolved, show a compact fallback such as “Model update information unavailable” rather than removing the metadata area entirely.[cite:118]

## Refresh Strategy

Recommended phase-one refresh behavior:

- Forecast data refresh every 30–60 minutes.[cite:118][cite:149]
- Radar metadata/frame list refresh about every 10 minutes to align with available radar-frame cadence.[cite:59]

Selector changes should be instant UI updates using already-loaded forecast data.[cite:143]

## Deliverables Expected from the Builder

The implementing LLM should produce:

1. A concise implementation plan for the page architecture.[cite:73]
2. Exact Open-Meteo endpoint and query structure.[cite:73]
3. Exact Rain Viewer metadata and tile integration approach.[cite:59]
4. A data model for forecast steps, selector state, and radar frames.[cite:73][cite:59]
5. UI modules for:
   - Forecast selector,[cite:73]
   - Forecast summary band,[cite:73]
   - Forecast timeline/grid,[cite:73]
   - Freshness metadata strip,[cite:118]
   - Radar card.[cite:59]
6. Error, loading, and refresh behavior.[cite:118][cite:59]
7. Final HTML implementation integrated into the existing sailing dashboard style direction.[cite:73]

## Acceptance Criteria

The page is successful if it meets all of the following:

| Requirement | Acceptance Standard |
|---|---|
| Dashboard integration | Implemented as one additional HTML page inside the existing New York City sailing dashboard.[cite:73] |
| Forecast source | Uses Open-Meteo only in phase one.[cite:78][cite:73] |
| Radar source | Uses Rain Viewer only in phase one.[cite:59] |
| Selector behavior | One forecast card with Next 4 / 8 / 12 hour selectors driven by one 12-hour forecast request.[cite:143][cite:73] |
| Time handling | Forecast timestamps shown in local New York time, not UTC.[cite:73][cite:90] |
| Required data | Temperature, precipitation, precipitation probability, cloud cover, visibility, weather condition summary included.[cite:73] |
| Optional data handling | Thunderstorm probability shown when available and gracefully handled when unavailable.[cite:30][cite:73] |
| Metadata | Forecast card shows last model/update freshness metadata and estimated next update.[cite:118] |
| Radar labeling | Radar clearly labeled as observed past 2 hours, not future forecast.[cite:59] |
| Scope discipline | No Google Weather API, no AccuWeather, no scraping, no undocumented future-radar source in phase one.[cite:79][cite:131][cite:138] |
| Stability | Forecast and radar degrade independently if one source fails.[cite:73][cite:59] |

## Copy-Paste Builder Prompt

Build one additional static HTML page for an existing New York City sailing dashboard. This new page is a weather forecast outlook page for a fixed sailing area in New York City Harbor / New York Bay, broadly spanning from the Brooklyn Bridge to the Verrazzano-Narrows Bridge and including the Statue of Liberty, the New Jersey waterfront, and the Hudson River south of roughly 50th Street. The page should fit the existing dashboard rather than behaving like a standalone new app. The existing dashboard already shows current wind speed, wind direction, and gusts on another page, so do not duplicate that information here. In phase one, use only free, documented, no-account sources. Use Open-Meteo as the only forecast source and Rain Viewer as the only radar source. Build one main forecast card with selector controls for Next 4 hours, Next 8 hours, and Next 12 hours. Back all selector states with a single 12-hour Open-Meteo forecast request and slice that data client-side instead of fetching separately per selector. Render hourly data only in phase one. Include temperature prominently plus precipitation amount, precipitation probability, thunderstorm probability when available, cloud cover, visibility, and a weather summary derived from weather_code. Add a small deterministic summary line such as generally fair, rain likely, reduced visibility, or thunderstorm caution. Display forecast freshness metadata once per forecast card using Open-Meteo model update metadata such as last_run_initialisation_time, last_run_availability_time, and update_interval_seconds, and label the next-update time as an estimate. All forecast timestamps must be shown in local New York time using timezone-aware handling such as timezone=auto. Add a separate radar card using Rain Viewer’s documented past radar frames only, clearly labeled as observed radar for the last 2 hours in 10-minute steps, not a future precipitation forecast. Do not use Google Weather API, AccuWeather, scraping, or undocumented future-radar sources in phase one. The builder may choose the exact visual design, layout, icons, and map library as long as the final page is clean, readable, stable, and fits into the existing dashboard.
