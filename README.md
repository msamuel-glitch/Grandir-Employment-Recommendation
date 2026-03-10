# BloomPath — AI Recruitment Intelligence Platform (Backend)

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey) ![SQLite](https://img.shields.io/badge/SQLite-Database-green) ![Deployed](https://img.shields.io/badge/Deployed-Render-purple)

## Overview

BloomPath is an end-to-end automated recruitment intelligence system built for **Grandir**, one of France's largest childcare networks operating **150+ nurseries** across the country.

Before BloomPath, Grandir's recruitment team was manually matching candidates to nursery locations — a process that took up to **30 days** per cycle and was bottlenecked by geography, role availability, and candidate profile fragmentation. BloomPath eliminated that bottleneck entirely.

**This repository contains the Flask backend.** The React frontend is available at [Grandir-Employment-Recommendation-Front-end](https://github.com/msamuel-glitch/Grandir-Employment-Recommendation-Front-end).

---

## The Problem

- 42,681 candidate records across fragmented data sources
- Manual matching process: ~30 days per recruitment cycle
- No real-time visibility into nursery vacancies vs. candidate availability
- Geographic mismatch between candidates and open positions

## The Solution

A Python/Flask backend that:
- Ingests and cleans candidate + job data from Excel sources
- Stores structured data in a SQLite database (`grandir_system.db`)
- Runs geospatial matching via KML nursery location data (`nurseries.kml`)
- Serves a REST API consumed by the React frontend
- Deploys to Render for live access

---

## Architecture

```
candidate data (candidates.xls)
        ↓
migrate_data.py → database.py (SQLite)
        ↓
screening.py → geospatial match via nurseries.kml
        ↓
server.py (Flask API)
        ↓
React Frontend (Vercel)
```

---

## Key Files

| File | Role |
|------|------|
| `server.py` | Main Flask application & API routes |
| `database.py` | Database connection & schema management |
| `screening.py` | Candidate screening & matching logic |
| `data_retriever.py` | Data ingestion from Excel sources |
| `migrate_data.py` | Data migration pipeline |
| `nurseries.py` | Nursery location data handling |
| `map_fixer.py` | Geospatial coordinate processing |
| `urgency.py` | Urgency scoring for open positions |
| `candidates.xls` | Source candidate dataset |
| `jobs.xls` | Source job listings dataset |
| `nurseries.kml` | Geospatial nursery location data |
| `requirements.txt` | Python dependencies |

---

## Results

- Processed **42,681 candidate records**
- Reduced matching cycle from **30 days → real-time**
- Deployed and live: backend on Render, frontend on Vercel
- Received direct interest from Grandir leadership team

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Data Processing:** Pandas
- **Geospatial:** KML parsing
- **Deployment:** Render
- **Frontend:** React (separate repo)

---

## How to Run Locally

```bash
# Clone the repo
git clone https://github.com/msamuel-glitch/Grandir-Employment-Recommendation.git
cd Grandir-Employment-Recommendation

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

API will be available at `http://localhost:5000`

---

## Context

Built as part of the **Business Deep Dive** module at **Albert School × Mines Paris PSL** — a hands-on program where students work directly on real operational problems with partner companies.
