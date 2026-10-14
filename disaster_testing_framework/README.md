# Performance and Reliability Testing Framework for a Disaster Management Portal

This is a complete, runnable academic Software Engineering Practice (SEP) project.

## Components
1. **Demo Disaster Management Portal**: A lightweight web application (FastAPI + Jinja2 + SQLite) simulating a disaster management system.
2. **Performance & Reliability Testing Framework**: An integrated asyncio-based load generation engine that tests the portal in real-time, displays live metrics on a professional dashboard, calculates reliability and performance scores, and generates history.

## Technologies
- Python 3.11+
- FastAPI, Uvicorn, Jinja2
- SQLAlchemy, SQLite
- httpx (for async load testing)
- psutil (for system monitoring)
- Bootstrap 5, Chart.js

## Setup Instructions
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Seed the database with demo data:
   ```bash
   python seed_database.py
   ```
5. Run the application:
   ```bash
   python run.py
   ```

## Architecture
- `app/models/`: SQLAlchemy ORM schemas.
- `app/routes/`: FastAPI routers for the portal UI, API, and the testing framework.
- `app/services/`: Core logic, including `testing_service.py` which runs the background asyncio load-generator.
- `app/templates/` & `app/static/`: Jinja2 UI templates and CSS/JS.
- `locust/`: Alternative Locust config for external heavy testing.

## Demo Workflow
1. Open http://127.0.0.1:8000
2. Go to **Performance Testing**.
3. Select "Load Test", configure users and duration.
4. Click **START TEST** and watch real-time graphs for Avg Response, Requests, CPU/Memory, and Error Rates.
5. After the test stops, view final **Performance Score** and **Reliability Score**.
6. Check **Test History** for past test logs.

> **Note**: Academic Demonstration System — Not for Real Emergency Operations.
