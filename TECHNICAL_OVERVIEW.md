# Jiroshi Dashboard Server — Technical Overview

**API-First (Headless) LMS Backend**  
A Django REST Framework system for instructors and LMS developers to build and control custom learning platforms with full ownership and extensibility.

---

## 1. Product Context

- **Role:** Backend API server for a **headless LMS**.
- **Users:** Instructors (platform owners) and LMS developers integrating the API into their own UIs (web, mobile, custom domains).
- **Model:** Instructors authenticate via the **Dashboard API**; they create courses, manage API keys, and view KPIs. End learners use the **Headless (Public) API** with instructor-issued API keys and optional student JWT for enrollment-gated content.
- **Control:** Instructors own their data; the API is open to extensions (custom frontends, any origin via CORS). No built-in plugin registry; extensibility is via API design and CORS/credentials support.

---

## 2. Repository and Stack — Real Numbers

| Metric | Value |
|--------|--------|
| **Django** | 5.2.5 |
| **Django REST Framework** | 3.16.1 |
| **Python** | 3.11.7 (Docker) |
| **Database** | PostgreSQL (via `DATABASE_URL`) |
| **Cache / broker** | Redis 7 (django-redis 6.0.0, redis 6.4.0) |
| **Django apps (logical)** | 11 (`core` + 7 dashboard + 3 headless) |
| **Concrete models** | 11 (excl. abstract `TimeStampedModel`, `SoftDeleteMixin`) |
| **Migrations (total)** | 36 |
| **API base paths** | 2: `api/v1/dashboard`, `api/v1/public` |
| **Approx. API route count** | ~55 |
| **ViewSets** | 7 |
| **Other API view classes** | ~18 |
| **Python files under `apps/`** | ~159 (incl. migrations, tests, admin) |
| **Largest modules (by line count)** | `apps/core/middleware/common.py` (423), `apps/dashboard/courses/views.py` (389), `apps/dashboard/instructors/views.py` (298), `apps/headless/common/utilities/Exceptions.py` (232), `apps/headless/students/views.py` (202), `apps/headless/courses/views.py` (224) |

### Key Dependencies (excerpt)

- **Auth:** `djangorestframework_simplejwt` 5.5.1, `bcrypt` 5.0.0  
- **API docs:** `drf-yasg` 1.21.11  
- **Filtering:** `django-filter` 25.2, `drf-nested-routers` 0.95.0  
- **History:** `django-simple-history` 3.10.1 (middleware only in use; historical models present in migrations)  
- **Storage:** `boto3` 1.40.38 (S3-compatible presigned URLs)  
- **Tasks:** `celery` 5.5.3  
- **Logging:** `structlog` 25.4.0  
- **Server:** `gunicorn` 23.0.0  

---

## 3. Application Architecture

### 3.1 App Layout

```
config/                    # Project config (settings, urls, wsgi, celery)
apps/
├── core/                  # Shared: base models, health, presigned URL, throttles, middleware, permissions
├── dashboard/             # Instructor-facing dashboard API
│   ├── instructors/      # Auth user model, profile, sessions, login attempts, legacy keys
│   ├── audit/             # AuditLog model + Celery tasks (no mounted URLs)
│   ├── courses/           # Course, CourseLesson, LessonResource CRUD + enrollments list
│   ├── apikeys/           # ApiKeys CRUD (headless API keys)
│   ├── dashboard/         # Dashboard KPIs (no own models)
│   ├── students/          # Student list (uses headless Student model)
│   └── file_manager/      # Placeholder (no URLs, stub views)
└── headless/              # Public API for custom frontends
    ├── instructor/        # Instructor profile + KPIs (API-key auth)
    ├── students/          # Student signup, login, profile, account (student JWT)
    └── courses/           # Catalogue, lessons, resources, enrollments (Enrollments model)
```

### 3.2 URL Structure

| Base path | Purpose |
|-----------|---------|
| `api/v1/dashboard/internals/` | Health check, generate-upload-presigned-url |
| `api/v1/dashboard/` | Instructor auth (signup, login, me, profile, logout, token refresh, update-info, update-password) |
| `api/v1/dashboard/view/` | Dashboard KPIs |
| `api/v1/dashboard/apikeys/` | API keys CRUD |
| `api/v1/dashboard/courses/` | Courses, lessons, resources, enrollments list |
| `api/v1/dashboard/students/` | Student list |
| `api/v1/public/instructor/` | Instructor profile, KPIs (headless) |
| `api/v1/public/students/` | Student signup, login, refresh-token, lookup, profile, account/update, logout |
| `api/v1/public/courses/` | Catalogue, lessons, resources, enroll, enrolled |

Docs: `swagger/`, `redoc/`, `swagger.json`, `swagger.yaml`.

---

## 4. Features (Technical)

### 4.1 Authentication and Identity

- **Dashboard (instructors)**  
  - **Model:** `AUTH_USER_MODEL = 'instructors.Instructor'` (extends AbstractUser + `TimeStampedModel` + `SoftDeleteMixin`).  
  - **Auth:** JWT only (`rest_framework_simplejwt.authentication.JWTAuthentication`).  
  - **Refresh:** Cookie `instructor_refresh_token` + `CustomTokenRefreshView`; rotation and blacklist enabled.  
  - **Config:** Access token lifetime from `INSTRUCTOR_ACCESS_TOKEN_EXP` (default 60 min), refresh from `INSTRUCTOR_REFRESH_TOKEN_EXP` (default 7 days).  

- **Headless (instructor context)**  
  - **Auth:** Custom `InstructorAPIKeyAuthentication`; header `x-api-key`, format `type:id:secret`, validated with bcrypt; result cached in Redis.  

- **Headless (students)**  
  - **Model:** `Student` (identifier, hashed password, FK to `Instructor`); unique per `(identifier, instructor)`.  
  - **Auth:** Custom `StudentJWTAuthentication`; JWT carries `student_id` and `instructor_id`; tenant boundary enforced (instructor must match request).  

### 4.2 Authorization and Multi-Tenancy

- **Dashboard:** `IsAuthenticated`; object-level `IsOwner` (e.g. `created_by` / `owner_field` on courses, lessons, resources).  
- **Headless:** `IsAuthenticatedStudent`; enrollment-gated content via `IsEnrolled` (object-level).  
- **Tenancy:** Students and enrollments are scoped by instructor; API key and student JWT both carry instructor context.

### 4.3 Course and Content Model

- **Course:** `Course` — title, description, thumbnail, duration, `access_status` (active/inactive/draft), `created_by` (Instructor).  
- **Lesson:** `CourseLesson` — course FK, title, description, duration, `access_status`, `media_key`, `media_size`, notes, `related_links` (JSON), `created_by`.  
- **Resource:** `LessonResource` — lesson FK, title, file_name, file_size, file_type, file_key, optional `created_by`.  
- **Enrollment:** `Enrollments` (headless) — unique (student, course); used to gate lesson/resource access on the public API.  

All of the above use `TimeStampedModel` (uuid, created_at, updated_at) and most use `SoftDeleteMixin` (soft delete/restore).

### 4.4 Media and Storage

- **Uploads:** `GET/POST api/v1/dashboard/internals/generate-upload-presigned-url/` — returns presigned S3-compatible URL (env: e.g. `S3_STATIC_BUCKET`, `S3_BUCKET`).  
- **Tracking:** ToDo mentions dedicated table for instructor storage usage and S3 object keys/status (not yet implemented).  
- **Media library:** Planned (MVP 2); `file_manager` app is a stub.

### 4.5 API Keys (Headless)

- **Model:** `ApiKeys` — instructor FK, key_name, key_hash, key_type (public/private), expires_at; unique (instructor, key_name, key_type).  
- **Dashboard:** Full CRUD under `api/v1/dashboard/apikeys/views/`.  
- **Usage:** Headless endpoints use `x-api-key`; validation cached in Redis.

### 4.6 Observability and Security

- **Throttling (global):**  
  - `anon`: 100/min  
  - `user`: 1000/min  
  - `instructor`: 1000/min  
  - `student`: 300/min  
  - `instructor_auth` / `student_auth`: 10/min  
  - `student_public`: 200/min  

- **Custom throttle classes:**  
  - Dashboard: `InstructorAuthBurstThrottle`, `InstructorRateThrottle`.  
  - Headless: `StudentAuthBurstThrottle`, `StudentRateThrottle`, `StudentOpenRateThrottle`.  

- **Middleware (production, when `DEBUG` is False):**  
  - `APILoggingMiddleware` — request/response logging, sanitization.  
  - `SecurityHeadersMiddleware` — security headers and IP handling.  
  - `RateLimitMiddleware` — commented out in settings.  

- **Audit:** `AuditLog` model (action, resource_type, resource_id, description, changes JSON, etc.); Celery tasks in `dashboard.audit.tasks` (e.g. cleanup); no HTTP API exposed.  

- **Sessions:** `InstructorSession` (session_key, IP, user_agent, geo, device, status, last_activity); `LoginAttempt` (attempt_type, IP, etc.).  

- **Logging:** Structlog (JSON, ISO timestamps); Django `LOGGING` points to console; optional queue-based handler commented out.

### 4.7 CORS and Cookies

- **CORS:** Applied only to `^/api/.*$`; `CORS_ALLOW_CREDENTIALS = True`; `CORS_ALLOWED_ORIGIN_REGEXES = [r"^.*$"]` to reflect any origin (documented in `CORS_SETUP.md`).  
- **Cookies:** SameSite=None; Secure when not DEBUG.  
- **Headers:** Custom headers allowed include `x-api-key`, `X-Client-Type`, `x-csrftoken`.

### 4.8 Background Jobs

- **Celery:** App name `jiroshi`; broker/result from env; autodiscover tasks; timezone UTC.  
- **Usage:** Audit-related tasks present; beat schedule (e.g. session/audit cleanup) commented out.  
- **Production:** Docker Compose runs Celery worker (concurrency 2) alongside Django (gunicorn, 3 workers, 2 threads).

---

## 5. Data Model Summary (Concrete)

| App | Model | Table / Purpose |
|-----|--------|------------------|
| core | (abstract) TimeStampedModel, SoftDeleteMixin | uuid, created_at, updated_at; soft delete manager and mixin |
| dashboard.instructors | Instructor | instructors — auth user |
| dashboard.instructors | InstructorProfile | instructor_profiles — 1:1 profile |
| dashboard.instructors | InstructorSession | session tracking |
| dashboard.instructors | LoginAttempt | login attempts |
| dashboard.instructors | InstructorKeys | legacy/internal keys (scope, expires_at) |
| dashboard.audit | AuditLog | audit_log — action/resource/changes |
| dashboard.courses | Course | courses |
| dashboard.courses | CourseLesson | course_lessons |
| dashboard.courses | LessonResource | course_lesson_resources |
| dashboard.apikeys | ApiKeys | instructors_apikeys |
| headless.students | Student | students |
| headless.courses | Enrollments | course_enrollments |

**Total: 11 concrete models + 2 abstract base models.**

---

## 6. Components (Technical)

- **Core:** Base models, health check, presigned URL view, throttles (dashboard + headless), middleware (API logging, security headers), permissions, decorators, helpers, constants, logging queue.  
- **Dashboard:** Instructor lifecycle, sessions, login attempts, API keys (dashboard.apikeys), courses/lessons/resources CRUD, enrollments list, student list, KPI aggregation; shared `dashboard.common.utilities` (Response, Paginator).  
- **Headless:** Shared `headless.common` (permissions, BaseView, Response, Errors, constants, pagination, request helpers); instructor profile/KPIs; student auth and profile; course catalogue, lessons, resources, enrollment and enrolled-courses.  
- **Infrastructure:** PostgreSQL, Redis (cache + Celery), S3-compatible storage (presigned URLs), optional Celery worker; Docker Compose for prod (server + redis + celery).  
- **Docs:** OpenAPI via drf-yasg; Swagger UI and ReDoc; Bearer in docs (no session auth).

---

## 7. Review and Assessment

### Strengths

- **Clear API split:** Dashboard vs headless with separate bases (`api/v1/dashboard`, `api/v1/public`) and auth (JWT vs API key + optional student JWT).  
- **Multi-tenant:** Instructor-scoped students and enrollments; tenant enforced in headless auth.  
- **Security:** JWT rotation and blacklist; API key hashing and Redis cache; role-specific throttles; CORS and cookie settings documented.  
- **Data safety:** Soft delete mixin and timestamped UUID base; audit model and session/attempt tracking (audit not yet exposed via API).  
- **Operational:** Health check used in Docker healthcheck; structured logging; production middleware for logging and headers; Celery wired for async work.  
- **Headless-friendly:** Any-origin CORS with credentials; API-key and student JWT support; enrollment-gated content.

### Weaknesses

- **No automated tests:** Test modules exist under each app but contain no real test cases; regression and refactoring safety rely entirely on manual checks. CI cannot enforce correctness or coverage.
- **Audit not consumable:** `AuditLog` is written (e.g. via middleware/tasks) but has no exposed API; instructors cannot query or export audit trails from the product. Session/login-attempt data is similarly not exposed for self-service review.
- **CORS allows any origin:** `CORS_ALLOWED_ORIGIN_REGEXES = [r"^.*$"]` enables any domain to call the API with credentials. This maximizes flexibility but increases abuse surface (e.g. token theft from malicious sites); no allowlist or per-instructor origin restriction.
- **Dual API-key systems:** `dashboard.apikeys.ApiKeys` (hashed, CRUD, used for headless) and `dashboard.instructors.InstructorKeys` (legacy, different schema) coexist; unclear migration path and possible confusion for developers.
- **Simple History unused:** `simple_history` middleware is enabled and historical tables exist in migrations, but `HistoricalRecords` is commented out on current models—no row-level history is being recorded despite the dependency and migration overhead.
- **Rate-limit middleware disabled:** Application-level `RateLimitMiddleware` is commented out in settings; only DRF throttle classes apply. A determined client could still stress the stack before throttles apply (e.g. connection exhaustion, expensive queries).
- **No formal API versioning:** Single version prefix (`v1`); no strategy documented or implemented for backward-incompatible changes (e.g. deprecation, second version prefix).
- **Stub/placeholder apps:** `file_manager` and partially `audit` have no HTTP surface; they add to INSTALLED_APPS and mental overhead without delivering user-facing behaviour. `dashboard.students` has no own models (relies on headless `Student`), which can blur ownership of student data between dashboard and headless.
- **Sensitive config in settings:** Email host/user and some mail config are hardcoded; `SECRET_KEY` and similar come from env (good) but not all secrets are consistently externalized.
- **Celery beat not configured:** Beat schedule is commented out; no built-in cron for session cleanup, audit retention, or token blacklist pruning—periodic tasks require external scheduler or manual enablement.
- **Logging handler choice:** Production logging uses console only; queue-based handler (e.g. for async or structured aggregation) is commented out. At scale, log aggregation may depend on process stdout capture only.

### Gaps and To-Dos (from repo)

- **Storage and media:** No central media library or S3 key/usage tracking yet; `file_manager` and Media/Storage Management Library are MVP 2.  
- **Permissions:** Per-course/per-lesson permissions planned, not implemented.  
- **Product:** Instructor payment module, course tags, trailers, featured courses — not in codebase.  
- **API key format:** ToDo to change API key separator.  
- **Tests:** No `test_` functions found under the project; test modules exist but are stubs.  
- **History:** `simple_history` middleware is on; historical models exist in migrations but `HistoricalRecords` is commented out on current models.  
- **Rate limit:** `RateLimitMiddleware` is disabled in settings.

### Suitability for “API-First Headless LMS”

- **Instructor control:** Instructors manage courses, lessons, resources, API keys, and see KPIs; students are per-instructor.  
- **Developer control:** Public API is RESTful, documented (Swagger/ReDoc), and callable from any origin with API key + optional student auth.  
- **Extensibility:** No formal plugin system; extension is by consuming the API and building custom frontends; CORS and credentials support multi-domain UIs.  

**Conclusion:** The codebase is a focused Django DRF backend for an API-first headless LMS: dual API surface (dashboard + public), multi-tenant students and enrollments, JWT and API-key auth, throttling, soft delete, audit/session tracking, and S3 presigned uploads. Pending work is mainly around media/library, granular permissions, payments/tags/trailers, and automated tests.

---

## 8. References in Repo

- **README.md** — Polyglot monorepo vision (Django/Node/Go); Phase 1 features; architecture and tech stack.  
- **ToDo.md** — MVP 1/2 checklist; S3 cleanup; media library; permissions; payment; tags/trailers; rate limiting and API key caching status.  
- **CORS_SETUP.md** — CORS and cookie-based auth for headless usage.  
- **config/settings.py** — Single source for INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT, CACHES, CORS, Celery, logging.  
- **config/urls.py** — All API and doc routes.  
- **docker/docker-compose.prod.yml** — Redis, jiroshi_server (gunicorn), celery worker; healthcheck to `api/v1/dashboard/internals/health/`.

---

*Generated from repository scan. Numbers and structure reflect the codebase as of the scan.*
