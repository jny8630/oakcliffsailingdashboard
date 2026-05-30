# ⛵ Oyster Bay Sailing Conditions

A mobile-first PWA for real-time sailing and current conditions in Oyster Bay / Long Island Sound — designed to check while walking to the dock.

![Dark nautical theme](https://img.shields.io/badge/theme-dark_nautical-0a1420) ![No API key](https://img.shields.io/badge/API_key-none_required-48bb78) ![Zero build step](https://img.shields.io/badge/build-zero_config-4fd1c5)

---

## Pages

### `index.html` — Wind & Pressure Dashboard
Real-time sailing conditions: wind, barometric pressure, weather, and forecast.

### `nyhops.html` — NYHOPS Images
Consecutive hourly surface current forecast images for Long Island Sound from Stevens NYHOPS.
> Note: NYHOPS LIS coverage and frame numbers are pending verification.

### `nyhops-overlay.html` — NYHOPS Chart Overlay
Interactive Leaflet map with OSM + OpenSeaMap nautical chart and NYHOPS current forecast overlay.
> Note: bounding box and buoy markers are placeholders pending LIS verification.

### `weather.html` — Weather Forecast
Short-range weather outlook for Oyster Bay / Long Island Sound.

- **Hourly forecast** from Open-Meteo HRRR: temperature, condition, precipitation probability, cloud cover, visibility, thunderstorm probability.
- **NWS Marine Zone Forecast (ANZ335 — Long Island Sound West)**: official CWF with wind in knots, wave heights, visibility. High-wind periods highlighted.
- **Observed radar**: RainViewer past-2h animated radar on a Leaflet map.

Forecast coordinate: Kings Point area (40.8732°N, 73.5332°W).

### `lnm.html` — Local Notice to Mariners Digest
Weekly USCG District 1 LNM filtered to Oyster Bay / Long Island Sound. Shows active notices relevant to Oyster Bay Harbor, Cold Spring Harbor, Huntington Bay, Hempstead Harbor, and western LIS approaches.

---

## Wind & Pressure Dashboard — What It Shows

### Wind — Kings Point (NOAA Station 8516945)
- Current sustained speed, gusts, and direction (cardinal + degrees)
- 2-hour horizontal wind speed chart
- B&G-style vertical WindPlot (TWD + TWS panels)

### Barometric Pressure — Kings Point
- Current pressure in mbar with trend (Rising/Falling/Steady)
- 3-hour and 6-hour pressure change with color coding
- 6-hour pressure chart

### Weather & Temperature
- Current temp °C/°F with feels-like
- Thunderstorm risk (CAPE-based)
- Water temperature

### Wind Forecast — HRRR (3km)
- 18-hour forecast from NOAA HRRR via Open-Meteo
- Columns: Time, Wind, Gust, Dir, Deg, Temp, Rain

---

## Data Sources

| Data | Source | Resolution | Update |
|------|--------|-----------|--------|
| Wind (current + history) | [NOAA CO-OPS](https://tidesandcurrents.noaa.gov/stationhome.html?id=8516945) — Kings Point | 6-minute | 6 min |
| Barometric pressure | NOAA CO-OPS — Kings Point | 6-minute | 6 min |
| Tides | [NOAA CO-OPS](https://tidesandcurrents.noaa.gov/stationhome.html?id=8516201) — Oyster Bay Harbor | High/Low events | Daily |
| Water temp | NOAA CO-OPS — Oyster Bay Harbor | Point reading | 6 min |
| Forecast | [Open-Meteo](https://open-meteo.com/en/docs/gfs-api) — HRRR model | 3 km / 15-min | Hourly |
| Radar | [Windy](https://www.windy.com) embed | — | Real-time |
| Surface currents | [Stevens NYHOPS](https://hudson.dl.stevens-tech.edu/maritimeforecast/) — LIS (coverage TBC) | ~500m / hourly | Daily |
| Marine zone forecast | [NWS OKX](https://marine.weather.gov/MapClick.php?zoneid=ANZ335) — ANZ335 LIS West | Text product | Twice daily |
| Observed radar | [RainViewer](https://www.rainviewer.com) | 10-min frames | Real-time |
| Nautical chart tiles | [OpenStreetMap](https://www.openstreetmap.org) + [OpenSeaMap](https://www.openseamap.org) | — | Continuous |

All dashboard APIs are free, require no API key, and support CORS.

---

## Deployment

### GitHub Pages

1. Fork or clone this repo
2. **Settings → Pages → Source**: select `main` branch, root folder (`/`)
3. Live at `https://yourusername.github.io/oakcliffsailingdashboard/`

### Install as PWA

1. Open the URL on your phone (Chrome or Safari)
2. Tap **"Add to Home Screen"**

---

## Open Items

- [ ] Verify NYHOPS LIS coverage bounds and correct frame numbers
- [ ] Add verified Oyster Bay / LIS USCG buoy coordinates to chart overlay
- [ ] Investigate MARACOOS HF-Radar for real-time LIS surface currents
- [ ] Sea breeze visualization (pressure gradient, inland vs coastal temp differential)

---

## License

MIT — use it, modify it, sail with it.

*For planning only — not for navigation.*
