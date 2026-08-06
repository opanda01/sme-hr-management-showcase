# Showcase — OR-Tools CP-SAT shift optimization core (sanitized).
# In production this runs in a dedicated Celery worker (`apps/scheduler/`) so long solves do not block the API.
# Design: employee×slot boolean vars x[e,s], hard constraints (leave, overlap, min rest, min staffing), soft penalties in the objective.

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from ortools.sat.python import cp_model


# --- Showcase domain types (production uses SQLAlchemy + separate modules) ---


@dataclass(frozen=True)
class ShiftSlot:
    """A single schedulable shift slot (generated from a template)."""

    date: date
    weekday: int
    start_utc: datetime
    end_utc: datetime


@dataclass
class EmployeeContext:
    """Per-employee input to the solver: leave days, existing shifts, preferences."""

    id: UUID
    leave_dates: set[date] = field(default_factory=set)
    existing_shift_intervals: list[tuple[datetime, datetime]] = field(default_factory=list)
    unavailable_weekdays: set[int] = field(default_factory=set)
    min_rest_hours: float = 11.0


@dataclass
class TemplateRules:
    """Sample Acme Corp template — minimum headcount per slot."""

    min_staff_per_slot: int = 1


class SolverStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class EngineResult:
    assignments: list[tuple[UUID, int]]  # (employee_id, slot_index)
    solver_status: str
    solve_time_ms: int
    warnings: list[str] = field(default_factory=list)


def _map_cp_status(status_code: int) -> str:
    mapping = {
        cp_model.OPTIMAL: SolverStatus.OPTIMAL.value,
        cp_model.FEASIBLE: SolverStatus.FEASIBLE.value,
        cp_model.INFEASIBLE: SolverStatus.INFEASIBLE.value,
    }
    return mapping.get(status_code, SolverStatus.UNKNOWN.value)


def apply_hard_constraints(
    model: cp_model.CpModel,
    x: dict[int, dict[int, cp_model.IntVar]],
    slots: list[ShiftSlot],
    employees: list[EmployeeContext],
    template: TemplateRules,
    slot_conflicts: dict[int, set[int]],
) -> None:
    """Hard constraints: any violation makes the schedule invalid (production: `constraint_builder.py`)."""

    for e_idx, emp in enumerate(employees):
        for s_idx, slot in enumerate(slots):
            if slot.date in emp.leave_dates:
                model.add(x[e_idx][s_idx] == 0)
            if slot.weekday in emp.unavailable_weekdays:
                model.add(x[e_idx][s_idx] == 0)
        for s_idx in slot_conflicts.get(e_idx, ()):
            model.add(x[e_idx][s_idx] == 0)

    max_duration = max((s.end_utc - s.start_utc for s in slots), default=timedelta(hours=12))
    for e_idx in range(len(employees)):
        min_rest = timedelta(hours=employees[e_idx].min_rest_hours)
        window = min_rest + max_duration
        for s1_idx, s1 in enumerate(slots):
            for s2_idx in range(s1_idx + 1, len(slots)):
                s2 = slots[s2_idx]
                if s2.start_utc >= s1.end_utc + window:
                    break
                if s1.end_utc > s2.start_utc and s1.start_utc < s2.end_utc:
                    model.add(x[e_idx][s1_idx] + x[e_idx][s2_idx] <= 1)
                gap = s2.start_utc - s1.end_utc
                if timedelta(0) <= gap < min_rest:
                    model.add(x[e_idx][s1_idx] + x[e_idx][s2_idx] <= 1)

    for s_idx in range(len(slots)):
        model.add(
            sum(x[e_idx][s_idx] for e_idx in range(len(employees)))
            >= template.min_staff_per_slot
        )


def run_shift_optimizer(
    *,
    company_id: UUID,
    period_start: date,
    period_end: date,
    slots: list[ShiftSlot],
    employees: list[EmployeeContext],
    template: TemplateRules,
    solver_timeout_seconds: float = 30.0,
) -> EngineResult:
    """
    Main pipeline: build model → add constraints → solve with CP-SAT → read assignments.
    `company_id` is used for tenant isolation and audit (not logged in this showcase).
    """
    _ = company_id  # tenant context — mapped to DB RLS in production

    if not slots:
        return EngineResult([], SolverStatus.UNKNOWN.value, 0, ["Dönemde planlanabilir slot yok."])
    if not employees:
        return EngineResult([], SolverStatus.INFEASIBLE.value, 0, ["Aktif personel yok."])

    t0 = time.monotonic()
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = solver_timeout_seconds
    solver.parameters.num_search_workers = min(8, max(2, os.cpu_count() or 4))

    x: dict[int, dict[int, cp_model.IntVar]] = {}
    for e_idx in range(len(employees)):
        x[e_idx] = {
            s_idx: model.new_bool_var(f"x_e{e_idx}_s{s_idx}") for s_idx in range(len(slots))
        }

    slot_conflicts: dict[int, set[int]] = {}
    for e_idx, emp in enumerate(employees):
        conflicts: set[int] = set()
        for s_idx, slot in enumerate(slots):
            for ex_start, ex_end in emp.existing_shift_intervals:
                if ex_end > slot.start_utc and ex_start < slot.end_utc:
                    conflicts.add(s_idx)
                    break
        slot_conflicts[e_idx] = conflicts

    apply_hard_constraints(model, x, slots, employees, template, slot_conflicts)

    # Soft preferences (e.g. preferred_days) are added to a penalties list and minimized in production.
    # Showcase: feasibility-only — no extra objective terms.

    status_code = solver.solve(model)
    solve_ms = int((time.monotonic() - t0) * 1000)
    status = _map_cp_status(status_code)

    assignments: list[tuple[UUID, int]] = []
    if status in (SolverStatus.OPTIMAL.value, SolverStatus.FEASIBLE.value):
        for e_idx, emp in enumerate(employees):
            for s_idx in range(len(slots)):
                if solver.value(x[e_idx][s_idx]) == 1:
                    assignments.append((emp.id, s_idx))

    warnings: list[str] = []
    if len(employees) * len(slots) > 10_000:
        warnings.append("Büyük model — timeout veya FEASIBLE sonuç olası.")

    return EngineResult(assignments, status, solve_ms, warnings)


# --- Minimal demo (fake data) ---

if __name__ == "__main__":
    ACME_COMPANY_ID = UUID("00000000-0000-4000-8000-000000000101")
    day = date(2026, 8, 4)
    start = datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc)
    end = datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc)
    demo_slots = [
        ShiftSlot(date=day, weekday=day.weekday(), start_utc=start, end_utc=end),
    ]
    demo_employees = [
        EmployeeContext(id=UUID("00000000-0000-4000-8000-000000000201")),
        EmployeeContext(id=UUID("00000000-0000-4000-8000-000000000202")),
    ]
    result = run_shift_optimizer(
        company_id=ACME_COMPANY_ID,
        period_start=day,
        period_end=day,
        slots=demo_slots,
        employees=demo_employees,
        template=TemplateRules(min_staff_per_slot=1),
        solver_timeout_seconds=5.0,
    )
    print(result.solver_status, result.assignments, f"{result.solve_time_ms}ms")
