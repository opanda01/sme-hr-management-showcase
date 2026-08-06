# Code examples (showcase)

Sanitized excerpts from the production monorepo: no real secrets, customer data, or internal infrastructure references. Intended as contextual reference for portfolios and technical reviews—not necessarily runnable as-is.

| File | Summary |
|------|---------|
| [`scheduler/shift_optimizer.py`](scheduler/shift_optimizer.py) | OR-Tools CP-SAT shift assignment: variables, hard constraints, solver invocation. |
| [`api/shift_swap_router.py`](api/shift_swap_router.py) | Shift swap REST flow; SQLAlchemy model, Pydantic schemas, RBAC `Depends`, approval endpoint. |
| [`mobile/QRScanner.tsx`](mobile/QRScanner.tsx) | Expo camera QR attendance; permissions, token parsing, check-in/out UI state machine. |

**Production sources:** `apps/scheduler/engine/`, `apps/api/src/features/workforce/swaps/`, `apps/mobile/app/(employee-tabs)/scan.tsx`

**Note:** Import paths and some modules are simplified for the showcase; the full system runs in the `apps/` monorepo.

See [LICENSE](../LICENSE.md) — evaluation and learning only; not a license to use this code in production without permission.
