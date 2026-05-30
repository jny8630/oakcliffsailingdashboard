# Builder Brief: Wind Tactics Analysis Page

## Context

This page is an extension of the NYC Harbor Sailing Dashboard, built for a racing team that sails Wednesday and Thursday evenings, 6–8 PM, in NYC Harbor. The racing window is a classic dying thermal / evening sea breeze scenario. The page should help answer one practical pre-race question: **what kind of breeze are we sailing in tonight, and which way do the lifts come?**

The existing dashboard already shows current wind speed, direction, gusts, and a 2-hour B&G-style WindPlot. This new page goes deeper: 12 hours of wind history, speed-direction correlation, and a gradient vs. thermal context indicator.

---

## File to Create

`wind-tactics.html` — one additional static HTML page, same design system as all existing pages (dark nautical theme, CSS vars, zero build step, no API keys).

---

## Data Sources

### Surface Wind — Robbins Reef (NOAA CO-OPS Station 8530973)
- Already used on `index.html`
- Fetch last 12 hours of 6-minute wind observations
- API: `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?station=8530973&product=wind&datum=MLLW&time_zone=lst/ldt&units=english&format=json&range=12`
- Returns: `t` (timestamp), `s` (speed kt), `d` (direction degrees), `g` (gust kt)
- 120 data points at 6-minute intervals

### 850 hPa Gradient Wind — Open-Meteo (HRRR)
- Already used on `index.html` for surface forecast
- Add `windspeed_850hPa` and `winddirection_850hPa` to the hourly variables
- 850 hPa is the standard proxy for gradient (synoptic) wind — above the thermal boundary layer
- Same coordinate as weather page: G1 buoy (40.6797°N, 74.0288°W)
- No API key required

---

## Page Structure: Three Cards

### Card 1 — 12-Hour Wind History Chart
- Dual-panel canvas chart (same B&G-inspired vertical-time layout as `index.html`, extended to 12h)
  - Left panel: wind direction with rolling mean and shaded deviation
  - Right panel: wind speed with gust overlay and rolling mean
- Time axis: current time at top, 12 hours ago at bottom
- Time markers at NOW, −2h, −4h, −6h, −8h, −10h, −12h
- Current-hour highlighted
- Retina/HiDPI canvas rendering (same `devicePixelRatio` pattern as existing charts)

### Card 2 — Shift Correlation Analysis
This is the core card. Using the 120 data points from Robbins Reef:

**Pearson correlation coefficient** between wind speed and wind direction change:
- Compute direction deltas (°/interval), handle 0/360 wraparound
- Compute Pearson r between speed series and direction-delta series
- Display r value prominently with color coding and plain-English interpretation:

| r value | Interpretation |
|---|---|
| r > +0.4 | Lifts arrive with puffs — oscillating breeze, tack on headers |
| r < −0.4 | Headers arrive with puffs — puff = bad news, hold on lifts |
| −0.2 to +0.2 | Speed and shift uncorrelated — gradient-dominated or dying |
| Any \|r\| with low speed std dev | Dying breeze — shifts becoming random |

**Shift regime classification** — derived from the 12h data:
- **Oscillating**: direction std dev > 10°, moderate r signal, speed variance present
- **Persistent**: direction trending consistently one way (sea breeze clock)
- **Dying thermal**: speed declining trend over last 3h, direction variance increasing
- **Gradient-dominated**: surface wind tracks 850 hPa closely (see Card 3)

**Oscillation statistics**:
- Mean direction (last 12h)
- Direction std dev (total scatter)
- Estimated oscillation period (time between direction reversals relative to mean)
- Port vs. starboard lift frequency (how often wind is left vs. right of mean)

**Note on statistical confidence**: Display sample size (n=120) and flag when correlation is below significance threshold. At n=120, |r| > 0.18 is significant at p < 0.05.

### Card 3 — Gradient vs. Thermal Context
This answers: *is the gradient wind in charge tonight, or are we in a pure thermal?*

**Surface vs. 850 hPa comparison**:
- Fetch current 850 hPa wind from Open-Meteo
- Show surface wind (Robbins Reef current) vs. gradient wind (850 hPa) side by side
- Compute directional difference and speed ratio
- Classification:

| Condition | Indicator |
|---|---|
| Surface ≈ 850 hPa direction (±20°) and speed ratio > 0.6 | Gradient-dominated — stronger, more consistent, shifts follow pressure systems |
| Surface diverges from 850 hPa by >40° | Thermal active — local heating driving the breeze |
| Surface speed < 40% of 850 hPa speed | Thermal suppressed or calm — gradient not reaching surface |
| Surface speed declining over last 3h + diverging from 850 hPa | Classic dying thermal / evening sea breeze collapse |

**Practical sailing interpretation** for each regime:
- Gradient-dominated → treat as oscillating gradient breeze, shifts track synoptic pattern, Dellenbaugh-style "percentage sailing" applies
- Thermal active → sea breeze will persist until sunset, direction clocks predictably, speed builds then dies
- Dying thermal → racing in the last 2h of sea breeze; direction becoming variable, favor inside of shifts, expect holes near shore
- Evening collapse → classic NYC Harbor 6–8 PM condition; gradient wind may reassert after thermal dies

---

## Racing Context

- **Race nights**: Wednesday and Thursday evenings
- **Racing window**: 6:00 PM – 8:00 PM
- **Expected regime**: Dying thermal / evening sea breeze in summer, gradient may reassert
- **Harbor**: NYC Upper Bay — influenced by Hudson River valley channeling, urban heat island, and proximity to the Narrows
- **Key question at race start**: Are we in an oscillating dying thermal (tack on shifts) or is the gradient taking over (sail the lifted tack, less shift-hunting)?

---

## Design Notes

- Match existing dashboard design system exactly: same CSS vars, card structure, collapse toggles, monospace font for numbers
- Mobile-first, max-width 440px
- All three data modules fail independently
- Auto-refresh: wind history every 10 minutes, gradient context every 30 minutes
- Nav links to/from all existing pages

---

## What This Page Is NOT

- Not a general weather page (that's `weather.html`)
- Not a current wind display (that's `index.html`)
- Not a tide or current page
- Focused entirely on shift pattern analysis for tactical racing decisions

---

## Resources / Conceptual Framework

The shift classification and correlation approach is grounded in:
- **Dave Dellenbaugh, Speed & Smarts** — oscillating vs. persistent shift framework, percentage sailing, when to tack on shifts
- **Chelsea Freers, C Tactics** — thermal vs. gradient wind identification, sea breeze lifecycle
- Standard meteorological practice: 850 hPa as gradient wind proxy, Pearson r for speed-direction correlation

The implementing LLM does not need these documents — the concepts are well-established and described in sufficient detail above.

---

## Instructions for the Builder

1. Read this brief fully before entering plan mode
2. Read `index.html` to extract the existing canvas chart patterns, CSS vars, and NOAA data-fetch functions — reuse them
3. Read `weather.html` to understand the page structure and three-card layout pattern
4. Verify the Open-Meteo 850 hPa wind variables are available for the G1 buoy coordinate before building
5. Verify NOAA CO-OPS 12h wind history returns expected fields
6. Build `wind-tactics.html` as a single self-contained HTML file
7. Add nav links to/from all existing pages
