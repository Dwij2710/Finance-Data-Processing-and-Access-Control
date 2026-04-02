from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.dashboard import SummaryResponse, CategoryTotal, MonthlyTrend, RecentRecord
from app.services import dashboard_service
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="[Analyst / Admin] Get financial summary",
)
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.analyst, UserRole.admin)),
):
    """
    **Analyst / Admin only.** Return aggregated financial summary:

    - `total_income` — sum of all income records
    - `total_expenses` — sum of all expense records
    - `net_balance` — income minus expenses
    - `total_records` — total count of all records
    """
    return dashboard_service.get_summary(db)


@router.get(
    "/categories",
    response_model=List[CategoryTotal],
    summary="[Analyst / Admin] Get totals grouped by category",
)
def categories(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.analyst, UserRole.admin)),
):
    """
    **Analyst / Admin only.** Return each category's total amount and record count,
    broken down by type (income / expense). Useful for pie charts or category analysis.
    """
    return dashboard_service.get_category_totals(db)


@router.get(
    "/trends",
    response_model=List[MonthlyTrend],
    summary="[Analyst / Admin] Get monthly income and expense trends",
)
def trends(
    months: int = Query(12, ge=1, le=24, description="Number of recent months to return"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.analyst, UserRole.admin)),
):
    """
    **Analyst / Admin only.** Return monthly aggregated income, expenses, and net balance.
    Use `months` to control how many recent months are included (default: 12, max: 24).
    """
    return dashboard_service.get_monthly_trends(db, months)


@router.get(
    "/recent",
    response_model=List[RecentRecord],
    summary="[All Roles] Get most recent financial activity",
)
def recent(
    limit: int = Query(10, ge=1, le=50, description="Number of recent records to return"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    **All authenticated roles.** Return the most recently dated financial records.
    Use `limit` to control how many are returned (default: 10, max: 50).
    """
    return dashboard_service.get_recent_records(db, limit)
