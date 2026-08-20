# FlyRank Capstone — Social Media Studio

A reliable backend service that turns one stored blog post into platform-specific social variants, routes them through human review, schedules approved variants, and publishes them through a common `SocialPublisher` adapter interface.

## Current Stage

**Stage 11 — End-to-End Integration & Reliability**

The system now demonstrates the complete publishing lifecycle:

```text
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
    ↓
Publish History
    ↓
Telegram Notification