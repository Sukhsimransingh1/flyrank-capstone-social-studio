# FlyRank Capstone — Social Media Studio

A backend service that turns one stored blog post into platform-specific social variants, routes them through human review, schedules approved variants, and publishes them through a common SocialPublisher adapter interface.

## Current Stage

Stage 10 — Configuration hardening, observability, testing, and documentation.

## Architecture

The system currently implements:

Blog Post
    ↓
Variant Generation
    ↓
Constraint Validation
    ↓
Human Review
    ↓
Scheduling
    ↓
Background Scheduler Worker
    ↓
Publisher Registry
    ↓
Platform Publisher
    ↓
Publish Record

## Implemented Features

- FastAPI backend
- PostgreSQL persistence
- SQLAlchemy ORM
- Docker Compose development environment
- Environment-based configuration
- Health endpoint
- Platform-specific content variants
- Variant validation
- Human review workflow
- Publish workflow
- Idempotency protection
- Durable scheduled publishing
- Background scheduler worker
- Publisher adapter interface
- Mock publisher
- Scheduler observability
- Automated tests

## Scheduler

The scheduler runs as a dedicated Docker service.

It polls the database every 5 seconds for scheduled records whose slot is due.

Lifecycle:

scheduled → publishing → published

or:

scheduled → publishing → failed

The scheduler updates the existing PublishRecord rather than creating a new record, preserving idempotency.

## Running the Project

Start the complete stack:

```bash
docker compose up --build