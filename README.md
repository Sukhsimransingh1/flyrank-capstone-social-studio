# FlyRank Capstone — Social Media Studio

A backend service that turns one stored blog post into platform-specific social variants, routes them through a human review workflow, schedules approved variants, and publishes through a common `SocialPublisher` adapter interface.

## Current stage

**Stage 1 — Design + backend foundation**

Implemented:
- FastAPI application
- PostgreSQL via Docker Compose
- SQLAlchemy database foundation
- Environment-based configuration
- Health endpoint
- Initial project architecture
- Design document
- Safe `.env.example`

Next stages will add ingestion, generation, constraint validation, review workflow, adapters, idempotent publishing, durable scheduling, publish history, tests, evidence, and final documentation.

## Run

```bash
docker compose up --build
```

API:
- http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Health check:

```bash
curl http://localhost:8000/health
```

## Project structure

```text
app/
├── api/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── services/
├── publishers/
└── main.py

tests/
scripts/
```

## Required FlyRank artifacts

- `DESIGN.md`
- `README.md`
- `EVIDENCE.md`
- `BUILDLOG.md`
- `.env.example`

## Non-goals

Image generation, analytics, engagement tracking, and real X/LinkedIn publishing are outside the core capstone scope.
