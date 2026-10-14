# Performance and Reliability Testing Framework for a Disaster Management Portal

Academic Software Engineering Practice (SEP) project.

**Academic Demonstration System — Not for Real Emergency Operations.**

This repository contains two integrated systems:

1. A lightweight **Demo Disaster Management Portal** (dummy data only).
2. A **Performance & Reliability Testing Framework** that sends real HTTP traffic at the portal, records metrics, scores the run with a *project-defined* algorithm, and writes HTML/JSON/CSV/PDF reports.

Scores are **calculated from collected samples**. They are not hard-coded and they are **not industry-standard SLOs**.

---

## Local URL

After starting the app, open:

**http://127.0.0.1:5000**

| Area | URL |
| --- | --- |
| Disaster portal dashboard | http://127.0.0.1:5000/ |
| Performance testing | http://127.0.0.1:5000/testing/ |
| Live monitor | http://127.0.0.1:5000/testing/live |
| Test history | http://127.0.0.1:5000/testing/history |
| System health | http://127.0.0.1:5000/testing/health |

---

## One-command-style setup

Use Python 3.11 or newer.

```bash
python -m venv venv
```

Windows (PowerShell):

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python seed_database.py
python run.py
```

Linux / macOS:

```bash
source venv/bin/activate
pip install -r requirements.txt
python seed_database.py
python run.py
```

`seed_database.py` recreates SQLite and loads dummy floods, earthquakes, cyclones, fires, landslides, shelters, rescue requests, and reports.

---

## Project structure

```
SEP_CIAP/
├── app/
│   ├── __init__.py              # Flask factory + demo failure simulation
│   ├── extensions.py
│   ├── logging_config.py
│   ├── models/                  # SQLite entities
│   ├── routes/                  # portal, REST API, testing UI
│   ├── services/                # testing engine, scoring, reports, psutil
│   ├── templates/
│   └── static/
├── locust/                      # Optional standalone Locust profiles
├── tests/                       # pytest unit / integration / performance helpers
├── reports/                     # Generated HTML/JSON/CSV/PDF
├── logs/                        # application.log, testing.log, errors.log
├── config.py                    # Thresholds and paths
├── seed_database.py
├── run.py
├── requirements.txt
└── README.md
```

---

## Architecture

| Layer | Role |
| --- | --- |
| Portal UI | Jinja2 + Bootstrap 5 emergency-operations theme |
| REST API | JSON endpoints used by the portal and by the load engine |
| SQLite | Dummy operational data + every test run and one-second samples |
| Testing engine | Background asyncio + httpx workers that hit `http://127.0.0.1:5000` |
| Metrics | Latency/error counters + psutil CPU, RAM, disk, network |
| Scoring | Project-defined performance score + reliability percentage |
| Reports | Written automatically at the end of each run |

The engine does **not** fake request counts. It issues HTTP GET (and smoke checks) against the live Flask process (`threaded=True`). High user counts are mapped onto a capped worker pool (`MAX_ENGINE_WORKERS`, default 250) so a student laptop remains usable; extra configured users increase request intensity per worker.

---

## REST API

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/health` | Portal + host health |
| GET | `/api/disasters` | Dummy disasters |
| GET | `/api/alerts` | Dummy alerts |
| GET | `/api/shelters` | Dummy shelters |
| GET | `/api/rescue-requests` | List |
| POST | `/api/rescue-requests` | JSON create (201 / 400) |
| GET | `/api/reports` | Citizen reports |
| POST | `/api/reports` | JSON create (201 / 400) |
| GET/POST | `/api/simulation` | DEMO failure controls |

---

## Test types

| Type | Behaviour |
| --- | --- |
| Smoke | Sequential PASS/FAIL of core APIs |
| Load | Concurrent users for the chosen duration |
| Stress | Stages 100 → 500 → 1000 → 2000 → 5000 (or up to the selected user cap); records an approximate breaking point |
| Spike | ~50-user baseline, then a sudden jump |
| Endurance | Sustained load for 1–30 minutes (preset seconds) |
| Reliability | Repeated calls; reliability = successes / total × 100 |

---

## Performance score (project-defined)

Not an industry standard. Documented so examiners can see the formula.

Weighted out of 100:

- Average response time — 40 points (full credit at ≤ 80 ms, none at ≥ 2000 ms)
- Error rate — 30 points (full credit at 0%, none at ≥ 15%)
- Throughput vs expected users — 15 points
- CPU — 10 points
- Memory — 5 points

Labels: EXCELLENT ≥ 90, GOOD ≥ 75, FAIR ≥ 60, otherwise POOR.

### Reliability score

```
Reliability = Successful Requests / Total Requests × 100
```

### Demonstration pass/fail (editable in Settings)

Default **PASS**: avg response < 500 ms, error rate < 2%, success rate > 98%.

**WARNING**: between pass and fail bands.

**FAIL**: avg response > 1000 ms or error rate > 5%.

These cutoffs live in `config.py` and can be changed in **Settings**. They are demonstration thresholds only.

---

## Failure simulation

**DEMO / TESTING MODE ONLY.** Applies extra delay or HTTP 500/503 to selected `/api/*` routes (not `/api/health`). It does not contact real emergency services.

---

## Logging

| File | Content |
| --- | --- |
| `logs/application.log` | App events |
| `logs/testing.log` | Test start/stop/completion/report generation |
| `logs/errors.log` | Exceptions |

No passwords are collected. Dummy names/phones in seed data are fictional.

---

## Automated tests

```bash
pytest
```

- Unit: reliability, error rate, performance score, report files
- Integration: REST API, portal forms, testing pages
- Performance helpers: endpoint lists and metric-to-score wiring

### Locust (optional, with the app already running)

Normal load:

```bash
locust -f locust/locustfile.py --host http://127.0.0.1:5000 --users 50 --spawn-rate 10 --run-time 1m --headless
```

Heavy load:

```bash
locust -f locust/heavy_load.py --host http://127.0.0.1:5000 --headless --users 1 --spawn-rate 1 --run-time 90s
```

(`heavy_load.py` includes a LoadTestShape; user flags are ignored while the shape is active.)

Spike:

```bash
locust -f locust/spike_shape.py --host http://127.0.0.1:5000 --headless --users 1 --spawn-rate 1 --run-time 70s
```

---

## Sample test scenario

1. `python seed_database.py && python run.py`
2. Browser: Performance Testing → Load → 100 users → 60 s → START
3. Live Monitor shows increasing request counts and response-time series
4. History row `T001` (or next id) with calculated averages and scores
5. Download `reports/T00x_load_*.html`

---

## Technologies

Python 3.11+, Flask, SQLAlchemy, SQLite, Jinja2, Bootstrap 5, Chart.js, httpx, psutil, Locust, pytest, ReportLab.