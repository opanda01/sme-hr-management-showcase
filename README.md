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

Kobik HR — SME HR Management System

Portfolio & live showcase: kobik.dev

A full-stack Human Resources platform for Small & Medium Enterprises (SMEs). One monorepo, three client applications, and a shared REST API—plus an OR-Tools scheduling worker for automated shift planning.

Overview

Managing people in a growing business should not require expensive enterprise software. Kobik HR gives owners, managers, and employees a unified toolkit on mobile and web, covering onboarding, scheduling, attendance, leave, feedback, and internal communications.

Architecture

monorepo/
├── apps/
│   ├── api/          # FastAPI backend (Python)
│   ├── mobile/       # React Native / Expo app (Kobik HR)
│   ├── dashboard/    # React web admin panel
│   └── scheduler/    # OR-Tools shift planning engine
└── docs/             # Architecture & setup (private dev repo)







Layer



Technology





Backend API



FastAPI · SQLAlchemy 2 · PostgreSQL · Redis





Mobile



React Native · Expo · Zustand · NativeWind





Web dashboard



React 19 · Vite 7 · Tailwind CSS 4 · Zustand





Infrastructure



Docker Compose · MinIO · GitHub Actions CI/CD · EAS



Screenshots

UI previews (mobile & web) are on the live showcase: kobik.dev





Mobile — Login · Employee dashboard · Shift schedule · QR attendance · Leave requests · Announcements



Web — Company overview · Employee management · Attendance & reports · Scheduler



Core features



Authentication & access control





Role-based access: Owner / Manager / Employee



Company registration with superadmin approval



Dynamic invite codes for employee onboarding



JWT auth with email and SMS OTP verification



Password reset: email → OTP → new password



Shift management





Create, bulk-create, update, and cancel shifts



Employee self-service schedule



Shift swap: employee → peer response → manager approval



Leave management





Types: Annual / Sick / Personal / Unpaid



Request → approve/reject with manager notifications



Per-employee leave balance



Turkish public holiday support



QR attendance





Manager starts a QR session (rotating token in Redis)



Employee scan via camera; check-in with cooldown



Live attendance summary for managers



Announcements & feedback





Pinnable announcements, unread badges, read receipts



Anonymous or identified feedback; manager reply and archive



Extended capabilities





Departments and org structure



Auto-scheduling via OR-Tools (dedicated scheduler service)



Notifications (email/SMS/push) and realtime updates



Documents & exports (MinIO storage, CSV/PDF reporting)



Legal & consent flows for registration compliance



Mobile application





Feature-Slice Design (FSD)



Dual tab layouts for Owner/Manager vs Employee (RBAC)



Manager hub: management vs personal view



Theming (multiple themes, persisted state)



Forms: react-hook-form + zod; strict email validation client & server



Web dashboard





Company statistics and date-range attendance reports



Employee CRUD, bulk import, role assignment



Invitation management and workforce tooling



API

The backend exposes 120+ REST endpoints across domains including:

auth · users · admin · companies · departments · employees · shifts · leaves · shift-swaps · qr · attendance · feedback · announcements · scheduler · dashboard · reports · notifications · files · legal

Interactive OpenAPI docs: /docs when the API runs locally (private development repository).

Quality & delivery





GitHub Actions: lint, type-check, API unit/integration tests, Docker image builds



Staging and production deploy workflows; mobile builds via EAS



Jest + React Testing Library on mobile



Docker Compose for local PostgreSQL, Redis, and MinIO



.env.example pattern—no secrets in version control



Status

This repository is a public showcase for portfolio and product marketing. Production source and ongoing development are maintained in a private repository.

For demos, architecture notes, and screenshots, visit kobik.dev.

License & contact

This showcase repository is provided for portfolio and demonstration purposes only. See LICENSE in this repository. Product inquiries: kobik.dev.



Built by kobik.dev

<div align="center">
<sub>FastAPI · React Native · React · PostgreSQL · Redis · MinIO · OR-Tools · Docker · Firebase</sub>
</div>
