# SME HR Management System

A graduation project — a full-stack Human Resources Management platform designed for Small & Medium Enterprises (SMEs). Built as a monorepo, three client applications share a single REST API backend.

---

## Overview

Managing people in a small business should not require expensive enterprise software. This platform provides owners, managers, and employees with a unified toolset — accessible on both mobile and web — covering the full HR lifecycle from onboarding to attendance reporting.

---

## Architecture

```
monorepo/
├── apps/
│   ├── api/          # FastAPI backend (Python)
│   ├── mobile/       # React Native / Expo application
│   └── dashboard/    # React web admin panel
└── packages/
    ├── types/        # Shared TypeScript type definitions
    └── ui-kit/       # Shared component library
```

| Layer | Technology |
|---|---|
| Backend API | FastAPI · SQLAlchemy 2 · PostgreSQL · Redis |
| Mobile Application | React Native 0.81 · Expo 54 · Zustand |
| Web Dashboard | React 19 · Vite 7 · Tailwind CSS 4 · Zustand |
| Infrastructure | Docker Compose · MinIO · GitHub Actions CI/CD |

---

## Screenshots

### Mobile Application

| Login | Employee Dashboard | Shift Schedule |
|---|---|---|
<img width="220" alt="karsılama-ekranı" src="https://github.com/user-attachments/assets/0b435bff-2207-45d2-8b44-a0bae6106551" />
<img width="220" alt="owner-dashboard" src="https://github.com/user-attachments/assets/9c6dbda5-03ba-4373-926b-4737003499bf" />



| QR Attendance | Leave Request | Announcements |
|---|---|---|
| *(coming soon)* | *(coming soon)* | *(coming soon)* |

### Web Dashboard

| Company Overview | Employee Management | Attendance Report |
|---|---|---|
<img width="300" alt="image" src="https://github.com/user-attachments/assets/2fcd4fb9-a44b-4c4d-abc4-7a9696ea9dbf" />


---

## Core Features

### Authentication & Access Control
- Role-based access control: **Owner / Manager / Employee**
- Company registration with superadmin approval workflow
- Dynamic invite-code system for employee onboarding
- JWT authentication with email and SMS OTP verification
- 3-step password reset flow (email → OTP → new password)

### Shift Management
- Create, bulk-create, update, and cancel shifts
- Employee self-service view for personal schedule
- Shift swap workflow: employee initiates → target responds → manager approves

### Leave Management
- Leave types: Annual / Sick / Personal / Unpaid
- Request → Approve / Reject workflow with manager notifications
- Leave balance cards per employee
- Turkish public holiday support

### QR Attendance
- Manager starts a QR session — rotating token is stored in Redis
- Employee scans QR via device camera — check-in recorded with 15-second cooldown
- Real-time attendance summary widget on the manager dashboard

### Announcements
- Pinnable announcements visible to all roles
- Unread badge counter per user
- Per-announcement read-receipt tracking

### Feedback
- Anonymous or identified feedback submission by employees
- Categories: Suggestion / Complaint / General
- Manager reply and archive workflow

---

## Mobile Application

- Feature-Slice Design (FSD) architecture
- 5+5 tab layout: Owner/Manager tabs and Employee tabs, driven by RBAC
- Manager Hub: dual-panel switcher between Management view and Personal view
- Dynamic theme system — 4 built-in themes, persisted via Zustand
- Form validation with `react-hook-form` and `zod`
- ASCII email validation enforced on both client and server
- Managed SplashScreen lifecycle

## Web Dashboard

- React 19 with Vite 7 and Tailwind CSS 4
- Company statistics and date-range attendance reports
- Full employee management: create, update, bulk import, role assignment
- Invitation management panel

---

## API

The backend exposes **76 REST endpoints** across the following domains:

`auth` · `users` · `admin` · `companies` · `shifts` · `leaves` · `shift-swaps` · `qr` · `attendance` · `feedback` · `announcements`

Interactive API documentation is available via Swagger UI at `/docs` when running locally.

---

## Quality & CI/CD

- GitHub Actions pipeline: lint and TypeScript type-check on every push
- Jest and React Testing Library for mobile component tests
- Docker Compose for a reproducible local environment (PostgreSQL, Redis, MinIO)
- `.env.example` provided — no secrets committed to the repository

---

## Status

This repository is a **public showcase**. The full source code is maintained in a private repository.

**Development timeline:** January 2026 — May 2026 (6 phases)

---

## Author

Graduation project — Computer Programming, 2026.
