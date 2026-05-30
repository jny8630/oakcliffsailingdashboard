# ⛵ NYC Harbor Sailing Conditions

A mobile-first PWA for real-time sailing and current conditions in NYC Harbor — designed to check while walking to the dock.

**[Live Demo →](https://jny8630.github.io/nycharborsailingdashboard/)**

![Dark nautical theme](https://img.shields.io/badge/theme-dark_nautical-0a1420) ![No API key](https://img.shields.io/badge/API_key-none_required-48bb78) ![Zero build step](https://img.shields.io/badge/build-zero_config-4fd1c5)

---

## Pages

### `index.html` — Wind & Tide Dashboard
Real-time sailing conditions: wind, tides, barometric pressure, weather, and forecast.

### `nyhops.html` — NYHOPS Images
Five consecutive hourly surface current forecast images for Manhattan Waters from Stevens NYHOPS, starting from the current hour.

### `nyhops-overlay.html` — NYHOPS Chart Overlay
Interactive Leaflet map with OSM + OpenSeaMap nautical chart as the base layer and the NYHOPS current forecast georeferenced on top. Includes 13 USCG buoy markers (G1, G5, G7, G9, G11, 31, 33, Y-A, Y-C, R26, R28, R30, R32) at verified coordinates.

### `weather.html` — Weather Forecast
Short-range weather outlook for NYC Harbor over the next 4, 8, or 12 hours.

- **Hourly forecast** from Open-Meteo HRRR: temperature (°C/°F), condition, precipitation probability, cloud cover, visibility in nautical miles, and thunderstorm probability when available. Rule-based plain-language summary (e.g. "Rain likely", "Thunderstorm caution"). Model freshness metadata with estimated next update.
- **NWS Marine Zone Forecast (ANZ338 — New York Harbor)**: official USCG/NWS coastal waters forecast with wind in knots, wave heights, and visibility in nm. Today & Tomorrow always shown; Extended Outlook (Wed–Thu) in a collapsible card. High-wind periods highlighted.
- **Observed radar**: RainViewer past-2h animated radar on a Leaflet map, 10-minute steps, play/pause/prev/next controls. Clearly labeled as observed — not a future forecast.

Forecast coordinate: G1 buoy (40.6797°N, 74.0288°W), central Upper Bay.

### `lnm.html` — Local Notice to Mariners Digest
Weekly USCG District 1 LNM filtered to NYC Harbor. Shows active notices (shoaling, bridge work, marine events, buoys off-station) relevant to the immediate sailing area: Ambrose Channel, Verrazzano Narrows, Upper/Lower Bay, Governors Island, Buttermilk Channel, Kill Van Kull, Great Kills, Sheepshead Bay, Hudson River south of W42nd St. Also provides direct links to the current and recent weekly PDFs with honest availability status (not yet posted / scanned PDF unavailable).

---

## Wind & Tide Dashboard — What It Shows

### At a Glance
Wind speed, temperature, and tide status in a quick-read banner strip.

### Wind — Robbins Reef (NOAA Station 8530973)
- Current sustained speed, gusts, and direction (cardinal + degrees)
- **2-hour horizontal wind speed chart** — sustained (green), gusts (orange), rolling average (dashed), 12-knot reference line
- Toggle to view full NOAA station page in-app

### B&G WindPlot — 2 Hours
Inspired by the B&G Advanced WindPlot display on Zeus/Vulcan chartplotters:
- **Vertical time axis** — current time at top, 2 hours ago at bottom
- **TWD panel** (left) — wind direction with rolling average and shaded deviation from mean
- **TWS panel** (right) — wind speed with gusts overlay and rolling average
- Time markers at NOW, -30m, -60m, -90m, -120m
- Reveals wind shift patterns and trends at a glance

### Barometric Pressure — Robbins Reef
- Current pressure in mbar
- Trend indicator (Rising/Falling/Steady with rate)
- **3-hour and 6-hour pressure change** with color coding
- **6-hour pressure chart** from NOAA 6-minute data

### Tides — The Battery (NOAA Station 8518750)
- Current status: Flooding / Ebbing / Slack with color coding
- Visual progress bar with Rule of Twelfths current strength indicator
- Countdown timer to next tide, 6-event lookahead
- Sunset time and tide phase at sunset

### Weather & Temperature
- Current temp in °C and °F with feels-like
- Weather description with icon
- Thunderstorm risk indicator (CAPE-based)
- Water temperature

### Wind Forecast — HRRR (3km resolution)
- 18-hour forecast from NOAA HRRR via Open-Meteo
- Columns: Time, Wind, Gust, Dir (cardinal), Dir (degrees), Temp, Rain
- Current hour highlighted with color-coded wind speeds

### Radar
- Interactive Windy radar embed (lazy-loaded on tap)
- Quick links to Windy and AccuWeather

---

## Data Sources

| Data | Source | Resolution | Update |
|------|--------|-----------|--------|
| Wind (current + history) | [NOAA CO-OPS](https://tidesandcurrents.noaa.gov/stationhome.html?id=8530973) — Robbins Reef | 6-minute | 6 min |
| Barometric pressure | NOAA CO-OPS — Robbins Reef | 6-minute | 6 min |
| Tides | [NOAA CO-OPS](https://tidesandcurrents.noaa.gov/stationhome.html?id=8518750) — The Battery | High/Low events | Daily |
| Water temp | NOAA CO-OPS — The Battery | Point reading | 6 min |
| Forecast | [Open-Meteo](https://open-meteo.com/en/docs/gfs-api) — HRRR model | 3 km / 15-min | Hourly |
| Radar | [Windy](https://www.windy.com) embed | — | Real-time |
| Surface currents | [Stevens NYHOPS](https://hudson.dl.stevens-tech.edu/maritimeforecast/) — Manhattan Waters | ~500m / hourly | Daily |
| Marine zone forecast | [NWS OKX](https://www.weather.gov) — ANZ338 New York Harbor CWF | Text product | Twice daily |
| Observed radar | [RainViewer](https://www.rainviewer.com) | 10-min frames | Real-time |
| Nautical chart tiles | [OpenStreetMap](https://www.openstreetmap.org) + [OpenSeaMap](https://www.openseamap.org) | — | Continuous |

All dashboard APIs are free, require no API key, and support CORS.

The LNM digest uses the USCG NAVCEN PDF (public) and GitHub Models (GPT-4o-mini via built-in `GITHUB_TOKEN`) — no external API key required.

---

## Deployment

### GitHub Pages (recommended)

1. Fork or clone this repo
2. **Settings → Pages → Source**: select `main` branch, root folder (`/`)
3. Live at `https://yourusername.github.io/repo-name/`

### Install as PWA

1. Open the URL on your phone (Chrome or Safari)
2. Tap **"Add to Home Screen"**
3. Opens like a native app — no browser chrome

---

## Technical Notes

### NYHOPS Current Overlay
NYHOPS forecast images are RGBA PNG files — only the current velocity arrows are opaque pixels; all other areas are fully transparent. This allows them to be georeferenced directly over any Leaflet tile layer using `L.imageOverlay` with the Manhattan Waters bounding box `[[40.632, -74.102], [40.785, -73.943]]`. Frame numbers map as: `frame = 25 + ET_hour`.

### High-DPI Canvas Rendering
All charts use `devicePixelRatio`-aware canvas setup for crisp rendering on Retina/high-DPI mobile screens.

### B&G-Style Vertical Wind Plots
The vertical plots mirror the B&G Advanced WindPlot paradigm where time flows top-to-bottom. A rolling average line provides the reference — deviation from the average is shown as a shaded area, making wind shifts immediately visible.

### Timezone Handling
NOAA returns timestamps in local time without timezone info. The app dynamically detects the current Eastern Time UTC offset using `Intl.DateTimeFormat` and appends it before parsing.

### HRRR vs GFS
The forecast uses Open-Meteo's `minutely_15` endpoint sourced from NOAA HRRR (3km, hourly refresh) rather than GFS (22km). HRRR is far more useful for local harbor conditions.

---

## File Structure

```
├── index.html                        # Wind & tide dashboard
├── weather.html                      # Weather forecast (Open-Meteo · NWS ANZ338 · RainViewer radar)
├── nyhops.html                       # NYHOPS surface current forecast images
├── nyhops-overlay.html               # NYHOPS currents on interactive Leaflet chart
├── lnm.html                          # Local Notice to Mariners digest
├── lnm_current.json                  # Auto-generated weekly notices (committed by CI)
├── manifest.json                     # PWA manifest
├── scripts/
│   ├── fetch_lnm.py                  # PDF download + GitHub Models extraction
│   └── requirements.txt
└── .github/workflows/
    └── lnm-update.yml                # Runs every Friday noon ET
```

No server, no build step, no node_modules. The LNM update is the only automated step (GitHub Actions).

---

## License

MIT — use it, modify it, sail with it.

*For planning only — not for navigation.*
