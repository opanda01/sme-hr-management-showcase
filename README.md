<div align="center">

<h1>SME HR Management System</h1>
<p><em>A full-stack Human Resources platform built for Small & Medium Enterprises</em></p>

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React Native](https://img.shields.io/badge/React_Native-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://reactnative.dev)
[![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_15-316192?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis_7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)

</div>

---

## Overview

Managing people in a small business should not require expensive enterprise software. This platform gives owners, managers, and employees a unified toolset — accessible on both mobile and web — covering the full HR lifecycle: from onboarding to automated shift scheduling to payroll-ready attendance reports.

Built as a graduation project, the system is a monorepo containing three applications that share a single REST API backend.

```
monorepo/
├── apps/
│   ├── api/        # FastAPI backend (Python)
│   ├── mobile/     # React Native / Expo application
│   └── dashboard/  # React web admin panel
└── packages/
    ├── types/      # Shared TypeScript type definitions
    └── ui-kit/     # Shared component library
```

## Architecture

```
Clients                  Backend                    Infrastructure
───────                  ───────                    ──────────────
Mobile (RN)  ──┐
               ├──→  FastAPI REST API  ──→  PostgreSQL 15
Web (React)  ──┘     + WebSocket       ──→  Redis 7
                      + OR-Tools        ──→  MinIO (object storage)
                      + APScheduler
```

| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI · SQLAlchemy 2 · PostgreSQL · Redis · OR-Tools · APScheduler |
| **Mobile** | React Native 0.81 · Expo 54 · Zustand · NativeWind · Firebase FCM |
| **Web Dashboard** | React 19 · Vite 7 · Tailwind CSS 4 · Zustand · recharts |
| **Infrastructure** | Docker Compose · MinIO · GitHub Actions · EAS Build |

The backend exposes **120+ REST endpoints** across 19 domains, auto-registered via `registry.py`, plus a WebSocket endpoint for real-time notifications.

## Screenshots

### Mobile Application

| Login | Owner Dashboard | Shift Schedule |
|-------|----------------|----------------|
| ![Login](docs/screenshots/login.png) | ![Owner Dashboard](docs/screenshots/owner-dashboard.png) | *(coming soon)* |

### Web Dashboard

| Company Overview |
|-----------------|
| ![Dashboard](docs/screenshots/dashboard.png) |

> This repository is a **public showcase**. The full source is maintained in a private repository.

## Core Features

### Authentication & Access Control

- Role-based access control: **Owner / Manager / Employee / Superadmin**
- Company registration with superadmin approval workflow
- Dynamic invite-code system (8-character, single-use) for employee onboarding
- JWT authentication (30-day tokens) · email verification · SMS OTP
- 3-step password reset: email → OTP → new password
- ASCII email validation enforced on both client and server

### Shift Management

- Create, bulk-create, update, and cancel shifts
- Employee self-service view for personal weekly schedule
- **Shift swap workflow:** employee initiates → target employee responds → manager approves
- Atomic swap approval with `SELECT FOR UPDATE` to prevent race conditions

### Automated Shift Scheduling (OR-Tools)

- **CP-SAT constraint solver** generates optimized weekly plans
- Employee preference request flow: employee submits → manager approves → preferences applied
- Constraints: unavailable days, preferred hours, max weekly hours, minimum rest between shifts, night shift rules
- Draft review workflow: generated plan stays in `pending_review` until manager explicitly approves

### Leave Management

- Four leave types: Annual / Sick / Personal / Unpaid
- Request → Approve / Reject workflow with manager notifications
- Leave balance cards per employee
- Turkish public holiday support

### QR Attendance

- Manager starts a QR session — rotating token stored in Redis (30-second refresh)
- Employee scans QR via device camera — check-in recorded with **15-second cooldown**
- DB-level unique constraint prevents duplicate check-ins on the same day
- Real-time attendance summary widget on the manager dashboard
- Date-range attendance reports with CSV export

### Notifications (Multi-channel)

- **4 channels:** in-app · WebSocket (real-time) · Expo Push / Firebase FCM · email
- Per-user, per-channel notification preferences
- `notification-navigator` maps push tap → role-aware screen redirect
- APScheduler workers for retry and cleanup

### Feedback & Announcements

- Anonymous or identified feedback submission (Suggestion / Complaint / General)
- Manager reply and archive workflow
- Pinnable announcements with per-user read-receipt tracking and unread badge counter

### File & Document Management

- MinIO-backed storage for avatars, company documents, and exported reports
- Tenant-isolated access: `StoredFile.company_id` enforced on every download
- Soft delete with `deleted_at` timestamp; presigned URL expiry for private files
- Supported types: PDF, Word, Excel, images, CSV

### Legal Compliance

- KVKK / İSG / İK (Turkish data protection, workplace safety, labor law) compliance checklist
- Owner acknowledgement per compliance item

## Mobile Application

Built with **Feature-Slice Design (FSD)** — 16 feature modules:

`auth` · `personnel` · `invitations` · `approvals` · `dashboard` · `shifts` · `leaves` · `attendance` · `qr` · `feedback` · `announcements` · `scheduler` · `files` · `notifications` · `profile` · `company`

**5+5 Tab Layout** driven by RBAC:

| Owner / Manager Tabs | Employee Tabs |
|----------------------|---------------|
| Dashboard (stats + attendance widget) | Today (shift card + countdown + announcements) |
| Personnel (search, filter, quick-add) | My Shifts (weekly calendar + swap request) |
| Approvals (leaves / swaps segmented) | Leave Requests (form + balance + history) |
| QR Attendance (session control + render) | QR Scan (camera + check-in / check-out) |
| Settings | Settings |

**Manager Hub** — dual-panel switcher between the management view and the manager's personal employee view.

**Dynamic theme system** — 4 built-in themes, persisted via Zustand + SecureStore.

**Auth resilience** — `hydrate()` continues with a cached user on network errors; clears token only on 401/403. Global auth guard in `_layout.tsx` prevents unauthenticated access to protected routes.

## Web Dashboard

Two user groups: superadmins (company approval, system overview) and Owner/Manager (day-to-day operations).

| Page | Description |
|------|-------------|
| Dashboard | Trend charts, shift coverage, approval queue, workforce health (recharts) |
| Personnel | Search, filter, CRUD modals, bulk CSV import with import result report |
| Shifts | Weekly grid, per-employee shift view |
| Scheduler | OR-Tools plan generation, template and preference management, draft approval |
| Attendance | Day-filter attendance report, present / absent / late chip filters |
| Leaves | Leave request list, approve/reject, detail view |
| Reports | CSV + Excel + jsPDF export, server-side presigned URL download |
| Legal Compliance | KVKK / İSG / İK item tracking |
| Documents | File upload and listing via MinIO |
| Notifications | Real-time notification list and management |

## Security

| Concern | Implementation |
|---------|---------------|
| Passwords | bcrypt via passlib |
| Tokens | JWT HS256, 30-day expiry |
| Authorization | RBAC dependency injection (`get_current_owner`, `get_current_manager`, etc.) |
| Tenant isolation | `company_id` ownership check on every endpoint |
| Brute-force protection | Redis-backed rate limiting |
| Concurrent writes | `begin_nested()` + `with_for_update()` on swap approval |
| QR tokens | Redis TTL + lazy regeneration + 15s check-in cooldown |
| File access | Tenant-isolated `StoredFile`, presigned URLs for private buckets |
| WebSocket auth | `?token=<JWT>` query param; invalid token closes connection immediately |
| Soft delete | Personnel: `is_active=False` · Files: `deleted_at` timestamp |

## Testing

**355 tests** — developed with a strict TDD (Red → Green → Refactor) cycle.

```
tests/
├── integration/          # 275 tests — HTTP layer against a real test database
│   ├── features/         # identity · organization · workforce · announcements
│   └── infrastructure/   # Redis rate limiting
└── unit/                 # 48 tests — schemas, DI, security, invite-code generation
```

Mobile unit tests (Jest + React Testing Library) cover hooks, auth components, and screen renders.

```bash
# Run all backend tests
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

## Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d db redis minio minio-init

# 2. Configure environment
cp .env.example .env

# 3. Run database migrations (37 migrations)
cd apps/api && alembic upgrade head

# 4. Create a superadmin account
python create_superadmin.py

# 5. Start services
uvicorn src.main:app --reload    # API       → http://localhost:8000
cd apps/dashboard && npm run dev  # Web       → http://localhost:5173
cd apps/mobile && npx expo start  # Mobile    → Expo Go
```

Interactive API docs: [`http://localhost:8000/docs`](http://localhost:8000/docs)

See [`docs/DOCKER_QUICKSTART.md`](docs/DOCKER_QUICKSTART.md) for a full walkthrough.

## CI/CD

8 GitHub Actions pipelines:

| Pipeline | Trigger |
|----------|---------|
| `backend-ci` | Lint + pytest on every push |
| `dashboard-ci` | ESLint + Vite build check |
| `mobile-ci` | ESLint + `tsc --noEmit` |
| `mobile-eas-build` | EAS dev build |
| `mobile-eas-staging` | EAS staging APK |
| `mobile-eas-prod` | EAS production APK |
| `backend-deploy-staging` | Deploy to staging server |
| `backend-deploy-prod` | Deploy to production server |

## Project Structure

```
.
├── apps/
│   ├── api/            # FastAPI (37 migrations, 41 test files)
│   ├── mobile/         # React Native / Expo (Feature-Slice Design, 16 modules)
│   └── dashboard/      # Vite + React 19
├── docs/               # Architecture notes, guides, 44+ change reports (Mar–Jun 2026)
├── .github/workflows/  # 8 CI/CD pipelines
├── docker-compose.yml
└── .env.example
```

## Status

This repository is a **public showcase**. The complete source code is maintained in a private repository.

- **Development period:** January 2026 — June 2026 (14 phases)
- **Graduation project** — Computer Programming, 2026

---

<div align="center">
<sub>FastAPI · React Native · React · PostgreSQL · Redis · MinIO · OR-Tools · Docker · Firebase</sub>
</div>
