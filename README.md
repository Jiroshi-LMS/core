# Jiroshi — Headless LMS Backend (Django/DRF)

Jiroshi is a **headless Learning Management System backend** that you can embed into any product via APIs.

It ships two API surfaces in a single Django project:

- **Dashboard APIs**: “Instructor/admin” APIs for creating content (courses, lessons, resources), managing API keys, and viewing KPI metrics.
- **Headless (Public) APIs**: “Student + storefront” APIs designed to be consumed by any frontend (any domain) using an **API Key** + optional **Student JWT**.

---

## Quick links

- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`
- **Dashboard base path**: `/api/v1/dashboard/`
- **Headless base path**: `/api/v1/public/`
- **Health**: `/api/v1/dashboard/internals/health/`

---

## Why this exists (product case study)

Traditional LMS products are either:

- **Monolithic** (UI + backend tightly coupled), which makes it hard to integrate into an existing app, or
- **“API-first” but opinionated**, which still pushes you into their frontend flows.

Jiroshi is built as a **backend-first, multi-tenant LMS**:

- You keep your own app + UI.
- Jiroshi provides the LMS primitives (catalogue, enrollment, lessons, resources, auth).
- Tenancy is enforced through **Instructor-scoped API keys** for all “public/headless” access.

The platform model:

- **Instructor**: the tenant owner (creates courses/lessons, issues API keys).
- **Student**: belongs to exactly one Instructor (tenant boundary).
- **API Keys**: issued by an Instructor and used by any client to call headless endpoints.

---

## Repository structure (high level)

The project is a Django + DRF codebase split by “audience”:

- `config/`
  - `settings.py`: Django/DRF/JWT/CORS/throttling configuration
  - `urls.py`: API entrypoint + route mounting + Swagger
- `apps/`
  - `core/`: shared internals (health, presigned upload URL, utilities, throttles)
  - `dashboard/`: **Dashboard API surface**
    - `instructors/`: instructor auth + profile (“tenant owner”)
    - `courses/`: course/lesson/resource CRUD + enrollments list
    - `students/`: instructor-facing student listing
    - `apikeys/`: API key issuance/rotation/deletion
    - `dashboard/`: KPI endpoints
    - `audit/`: audit/history-related models (via `django-simple-history`)
  - `headless/`: **Headless/Public API surface**
    - `students/`: student auth + profile lifecycle
    - `courses/`: catalogue, lessons, resources, enrollment flows
    - `instructor/`: instructor profile + KPI for public consumption
    - `common/`: shared headless response format, auth, pagination, errors
- `docker/`: production compose + Dockerfile
- `tests/`: test suite entrypoint (plus per-app tests)

---

## Runtime and dependencies

- **Python**: 3.11 (see `Dockerfile`)
- **Django**: 5.2.x
- **DRF**: 3.16.x
- **Auth**: `djangorestframework-simplejwt` (+ blacklist)
- **Docs**: `drf-yasg`
- **Caching/ratelimit backing**: Redis (`django-redis`)
- **Async tasks**: Celery (worker included)

Install:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run:

```bash
make run
```

---

## API entrypoints and routing

All API routing is mounted from `config/urls.py`.

### Dashboard APIs

Base path: **`/api/v1/dashboard/`**

Mounted modules:

- `.../internals/` → `apps.core.urls`
- `.../` → `apps.dashboard.instructors.urls`
- `.../view/` → `apps.dashboard.dashboard.urls`
- `.../apikeys/` → `apps.dashboard.apikeys.urls`
- `.../courses/` → `apps.dashboard.courses.urls`
- `.../students/` → `apps.dashboard.students.urls`

### Headless/Public APIs

Base path: **`/api/v1/public/`**

Mounted modules:

- `.../instructor/` → `apps.headless.instructor.urls`
- `.../students/` → `apps.headless.students.urls`
- `.../courses/` → `apps.headless.courses.urls`

---

## Authentication model

### Dashboard auth (Instructor JWT)

Dashboard endpoints use DRF JWT auth:

- **Access token**: returned in JSON, used as `Authorization: Bearer <access_token>`
- **Refresh token**: set as an **HttpOnly cookie** named `instructor_refresh_token`

Important flows:

- Signup/Login set refresh cookie + return access token
- Refresh reads refresh token from cookie (rotation enabled)
- Logout blacklists refresh and deletes cookie

### Headless auth (API key + optional Student JWT)

All headless endpoints are tenant-scoped using an API key:

- Header: **`x-api-key`**
- Format: **`pk:<key_uuid>:<key_secret>`**
  - The `pk` prefix indicates a “public” key type (enforced server-side).

Student-specific endpoints additionally accept a Student JWT:

- Header: `Authorization: Bearer <student_access_token>`
- The server enforces a **hard tenant boundary**: the student token’s instructor must match the instructor resolved from the API key.

#### Refresh token transport (Headless)

Student refresh tokens can be returned via:

- **Cookie mode (browser)**: refresh token stored in `student_refresh_token` HttpOnly cookie
- **JSON mode (non-browser / dev tooling)**: refresh token returned in JSON

The server auto-selects transport mode; you can force JSON mode by sending:

- Header: `X-Client-Type: non-browser` (or `dev`)

---

## Response formats

Jiroshi intentionally uses **two response envelopes**, one per API surface.

### Dashboard response envelope

From `apps/dashboard/common/utilities/Response.py`:

```json
{
  "status": true,
  "status_code": 200,
  "response": { "..." : "..." },
  "msg": "..."
}
```

### Headless response envelope

From `apps/headless/common/utilities/Response.py`:

```json
{
  "status": true,
  "results": true,
  "message": "Success",
  "data": { "..." : "..." },
  "error_code": null
}
```

---

## Throttling (rate limits)

Configured in `config/settings.py`:

- **Instructor (dashboard)**: `instructor`, `instructor_auth`
- **Student (headless)**: `student`, `student_auth`, `student_public`

Implemented in:

- `apps/core/throttles/dashboard_throttle.py`
- `apps/core/throttles/headless_throttle.py`

---

## Dashboard API surface (by module)

Prefix: **`/api/v1/dashboard`**

### Internals (`apps.core`)

- `GET /api/v1/dashboard/internals/health/`
- `POST /api/v1/dashboard/internals/generate-upload-presigned-url/` (S3 presigned upload URL)

### Instructors (`apps.dashboard.instructors`)

Router prefix: `/api/v1/dashboard/instructor/`

- `POST /api/v1/dashboard/instructor/` (signup)
- `POST /api/v1/dashboard/instructor/login/`
- `POST /api/v1/dashboard/instructor/logout/`
- `GET /api/v1/dashboard/instructor/me/`
- `POST /api/v1/dashboard/instructor/profile/` (create/update profile)
- `PUT /api/v1/dashboard/instructor/update-info/`
- `PATCH /api/v1/dashboard/instructor/update-password/`
- `POST /api/v1/dashboard/instructor/token/refresh/` (refresh access token via cookie refresh)

### Dashboard KPIs (`apps.dashboard.dashboard`)

- `GET /api/v1/dashboard/view/kpi/`

### API Keys (`apps.dashboard.apikeys`)

Router prefix: `/api/v1/dashboard/apikeys/views/`

- `GET /api/v1/dashboard/apikeys/views/` (list)
- `POST /api/v1/dashboard/apikeys/views/` (create: returns `public` + `private` once)
- `DELETE /api/v1/dashboard/apikeys/views/<uuid>/` (hard delete)

### Courses + Lessons + Resources (`apps.dashboard.courses`)

Router prefixes:

- `/api/v1/dashboard/courses/views/` (courses)
- `/api/v1/dashboard/courses/lessons/` (lessons)
- `/api/v1/dashboard/courses/resources/` (resources)

Additional endpoints:

- `GET /api/v1/dashboard/courses/enrollments/` (list enrollments)

Notable actions:

- `PATCH /api/v1/dashboard/courses/views/<uuid>/toggle-status/`
- `PATCH /api/v1/dashboard/courses/lessons/<uuid>/update-lesson-media/`
- `PATCH /api/v1/dashboard/courses/resources/update-text-resources/`

### Students (instructor-facing) (`apps.dashboard.students`)

- `GET /api/v1/dashboard/students/list/`

---

## Headless/Public API surface (by module)

Prefix: **`/api/v1/public`**

All endpoints require **`x-api-key`**.

### Instructor public info (`apps.headless.instructor`)

- `GET /api/v1/public/instructor/profile/`
- `GET /api/v1/public/instructor/kpi/`

### Student auth + profile (`apps.headless.students`)

- `POST /api/v1/public/students/signup/` (API key required)
- `POST /api/v1/public/students/login/` (API key required)
- `POST /api/v1/public/students/refresh-token/` (refresh token cookie or JSON)
- `POST /api/v1/public/students/lookup/` (check identifier availability)
- `GET /api/v1/public/students/profile/` (API key + Student JWT)
- `PUT /api/v1/public/students/account/update/` (API key + Student JWT)
- `POST /api/v1/public/students/logout/` (API key + Student JWT)

### Catalogue + lessons + enrollment (`apps.headless.courses`)

Catalogue:

- `GET /api/v1/public/courses/` (list, filter/search/order; optional Student JWT enriches enrollment status)
- `GET /api/v1/public/courses/<uuid>/` (retrieve)

Lessons:

- `GET /api/v1/public/courses/<course_uuid>/lessons/`
- `GET /api/v1/public/courses/<course_uuid>/lessons/<lesson_uuid>/`

Lesson resources:

- `GET /api/v1/public/courses/<course_uuid>/lessons/<lesson_uuid>/resources/`

Enrollment:

- `POST /api/v1/public/courses/enroll/` (API key + Student JWT)
- `GET /api/v1/public/courses/enrolled/` (API key + Student JWT)