# Showcase — shift swap API layer (sanitized): multi-step approval (target employee → manager).
# Production lives under `apps/api/src/features/workforce/swaps/` with CRUD, notification dispatcher, and tenant DB sessions.
# RBAC via FastAPI Depends; tenant isolation via company_id + verify_company_access.

from __future__ import annotations

import enum
from typing import Annotated, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session, declarative_base

# Production: from src.core.dependencies.auth import get_current_user
# Production: from src.core.database.tenant_session import get_tenant_db


Base = declarative_base()


# =============================================================================
# RBAC (abbreviated — production: src/core/dependencies/rbac.py)
# =============================================================================


class UserRole(str, enum.Enum):
    owner = "owner"
    manager = "manager"
    employee = "employee"


class UserStub:
    """User injected into the request context after auth (showcase stub)."""

    def __init__(self, id: UUID, company_id: UUID, role: UserRole):
        self.id = id
        self.company_id = company_id
        self.user_role = role
        self.email = "ayse.demir@example-acme.test"


def get_current_user() -> UserStub:
    # JWT / session — real values come from .env (e.g. JWT_SECRET); stub here.
    return UserStub(
        id=UUID("00000000-0000-4000-8000-000000000301"),
        company_id=UUID("00000000-0000-4000-8000-000000000101"),
        role=UserRole.employee,
    )


def _require_roles(*allowed: UserRole):
    def dependency(current_user: Annotated[UserStub, Depends(get_current_user)]) -> UserStub:
        if current_user.user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu işlem için gerekli yetkiniz yok.",
            )
        return current_user

    return dependency


get_current_employee = _require_roles(UserRole.employee, UserRole.manager)
get_current_manager_or_owner = _require_roles(UserRole.manager, UserRole.owner)


def verify_company_access(current_user: UserStub, company_id: UUID) -> None:
    if current_user.user_role == UserRole.owner:
        return
    if current_user.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Şirket bulunamadı.")


def get_db() -> Session:
    raise NotImplementedError("Showcase — use get_tenant_db() in production.")


# =============================================================================
# SQLAlchemy model (abbreviated — production: swaps/models.py)
# =============================================================================


class SwapStatus(str, enum.Enum):
    pending = "pending"
    accepted_by_target = "accepted_by_target"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class ShiftSwapRequest(Base):
    __tablename__ = "shift_swap_requests"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    company_id = Column(PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    requester_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    requester_shift_id = Column(PG_UUID(as_uuid=True), ForeignKey("shifts.id"), nullable=False)

    target_employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_shift_id = Column(PG_UUID(as_uuid=True), ForeignKey("shifts.id"), nullable=True)

    status = Column(Enum(SwapStatus), default=SwapStatus.pending, nullable=False)
    reason = Column(String(500), nullable=True)
    rejection_note = Column(String(500), nullable=True)

    reviewed_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("requester_id != target_employee_id", name="ck_swap_no_self"),
        Index("ix_swap_company_status", "company_id", "status"),
    )


# =============================================================================
# Pydantic schemas (abbreviated — production: swaps/schemas.py)
# =============================================================================


class ShiftSwapRequestCreate(BaseModel):
    requester_shift_id: UUID
    target_employee_id: UUID
    target_shift_id: Optional[UUID] = None
    reason: Optional[str] = Field(default=None, max_length=500)

    requester_id: Optional[UUID] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def no_self_swap(self) -> "ShiftSwapRequestCreate":
        if self.requester_id and self.requester_id == self.target_employee_id:
            raise ValueError("Kendinizle vardiya takası yapamazsınız.")
        return self


class SwapRespondRequest(BaseModel):
    action: Literal["accept", "reject"]
    rejection_note: Optional[str] = Field(default=None, max_length=500)


class ShiftSwapRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    requester_id: UUID
    target_employee_id: UUID
    status: SwapStatus
    reason: Optional[str] = None


# =============================================================================
# Router — critical endpoints in the approval flow
# =============================================================================

router = APIRouter(
    prefix="/companies/{company_id}/shift-swaps",
    tags=["Shift Swaps"],
)


@router.post("", response_model=ShiftSwapRequestResponse, status_code=status.HTTP_201_CREATED)
def create_swap(
    company_id: UUID,
    swap_in: ShiftSwapRequestCreate,
    current_user: Annotated[UserStub, Depends(get_current_employee)],
    db: Annotated[Session, Depends(get_db)],
):
    if current_user.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu şirkete erişim yetkiniz yok.")

    swap_in.requester_id = current_user.id
    swap_in.model_validate(swap_in.model_dump())

    # crud.create_swap(db, company_id=..., requester_id=current_user.id, ...)
    raise NotImplementedError("Showcase — CRUD lives in the production module.")


@router.patch("/{swap_id}/respond", response_model=ShiftSwapRequestResponse)
def respond_to_swap(
    company_id: UUID,
    swap_id: UUID,
    respond_in: SwapRespondRequest,
    current_user: Annotated[UserStub, Depends(get_current_employee)],
    db: Annotated[Session, Depends(get_db)],
):
    """Target employee (e.g. fake UUID for Ahmet Yilmaz) accepts or rejects."""
    if current_user.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu şirkete erişim yetkiniz yok.")

    # crud.respond_to_swap → status: pending → accepted_by_target | rejected
    # On accept: notify requester + managers (NotificationDispatcher, idempotency_key)
    raise NotImplementedError("Showcase — CRUD lives in the production module.")


@router.patch("/{swap_id}/approve", response_model=ShiftSwapRequestResponse)
def approve_swap(
    company_id: UUID,
    swap_id: UUID,
    current_user: Annotated[UserStub, Depends(get_current_manager_or_owner)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Manager approval: shift ownership is swapped in an atomic transaction (with_for_update).
    Production: crud.approve_swap + EventType.SWAP_COMPLETED notification.
    """
    verify_company_access(current_user, company_id)

    # swap = crud.approve_swap(db, swap_id=swap_id, company_id=company_id, reviewed_by=current_user.id)
    raise NotImplementedError("Showcase — CRUD lives in the production module.")
