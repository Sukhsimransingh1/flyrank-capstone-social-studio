# Design — Social Media Studio

## 1. Problem

The system accepts one blog post as a URL or pasted Markdown, stores it as the single source of truth, creates one platform-specific variant per configured platform, validates each variant against platform constraints, sends each variant through human review, schedules only approved variants, and publishes through one common adapter interface.

The central reliability requirement is that retries and worker restarts must not create duplicate posts.

## 2. Architecture

```text
Blog URL / Markdown
        |
        v
Post Ingestion
        |
        v
Stored Post (source of truth)
        |
        v
Variant Generator
        |
        v
Constraint Validator
        |
        v
Review Workflow
draft -> approved / rejected
        |
        v
Durable Scheduler
        |
        v
SocialPublisher interface
   |          |           |
   v          v           v
Telegram    Mock X    Mock LinkedIn
  real        mock        mock
   \           |           /
    \          |          /
       Publish History
```

## 3. Core domain objects

### Post

Stores the original source post.

Fields:
- id
- source_type
- source_url
- source_markdown
- title
- created_at
- updated_at

### Variant

One platform-specific version of a stored post.

Fields:
- id
- post_id
- platform
- content
- status
- validation_errors
- created_at
- updated_at

Statuses:
- draft
- approved
- rejected
- published

### Platform profile

Defines rules enforced by code:
- maximum length
- tone
- maximum hashtag count

### Schedule slot

Represents when an approved variant should be published.

### Publish attempt

Records every publishing attempt and its result. The idempotency key is unique per variant and scheduled slot.

## 4. Publisher interface

Business logic depends on a single abstraction:

```text
SocialPublisher
    publish(content, idempotency_key) -> PublishResult
```

Implementations:

```text
TelegramPublisher
MockXPublisher
MockLinkedInPublisher
```

Adding or replacing a platform should require an adapter/configuration change rather than a rewrite of business logic.

## 5. API surface

Planned endpoints:

```text
POST   /posts
GET    /posts/{post_id}

POST   /posts/{post_id}/generate

GET    /variants
GET    /variants/{variant_id}
PUT    /variants/{variant_id}
POST   /variants/{variant_id}/approve
POST   /variants/{variant_id}/reject

POST   /schedules
GET    /schedules

POST   /publish/{variant_id}

GET    /publish-history
GET    /publish-history/{attempt_id}

GET    /platforms
GET    /health
```

## 6. Constraint enforcement

Generation produces candidate text. Validation is a separate deterministic step.

A variant cannot enter review if it violates its platform profile.

Examples:
- content length exceeds the platform maximum
- hashtag count exceeds the configured maximum
- required tone rule is not satisfied

The validator is authoritative; prompts/templates do not replace validation.

## 7. Review invariants

```text
draft -> approved
draft -> rejected
approved -> scheduled
scheduled -> published
```

Invalid transitions are rejected.

An unapproved variant cannot be scheduled.

## 8. Idempotency

Every publish slot receives a deterministic idempotency key derived from:

```text
variant_id + scheduled_at
```

The database will enforce uniqueness for this key.

If a worker retries the same publish operation after a timeout or restart, the system will reuse the same key and prevent a second successful publish record for the same variant/slot.

## 9. Durable scheduling

Scheduled work must survive a worker restart.

The job store will be persistent rather than memory-only. The worker will:
1. load due jobs
2. attempt publication
3. record the attempt
4. rely on the idempotency key for safe retry

## 10. Security

- Secrets are environment variables.
- `.env` is ignored by Git.
- `.env.example` contains placeholders only.
- Tokens are never logged.
- Input is validated at the API boundary.

## 11. Explicit non-goal

Real publishing to Instagram, X, and LinkedIn is not part of this capstone. X and LinkedIn will use mock adapters. One owned Telegram target will be the real publishing target.

Image generation, analytics, and engagement tracking are also outside the core scope.
