from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app.database import get_db
from app.schemas.financial import RecordCreate, RecordUpdate, RecordResponse, RecordFilter
from app.services import financial_service
from app.models.user import User, UserRole
from app.models.financial import RecordType
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post(
    "/",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Analyst / Admin] Create a new financial record",
)
def create_record(
    data: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.analyst, UserRole.admin)),
):
    """
    **Analyst / Admin only.** Create a new income or expense record.

    - `amount` must be a positive number.
    - `type` must be `income` or `expense`.
    - `date` is the actual transaction date (not today's date automatically).
    """
    return financial_service.create_record(db, data, current_user.id)


@router.get(
    "/",
    response_model=List[RecordResponse],
    summary="[All Roles] List financial records with optional filters",
)
def list_records(
    q: Optional[str] = Query(None, description="Search term for category or description"),
    type: Optional[RecordType] = Query(None, description="Filter by type: income or expense"),
    category: Optional[str] = Query(None, description="Filter by category (partial match)"),
    from_date: Optional[datetime.date] = Query(None, description="Filter records on or after this date (YYYY-MM-DD)"),
    to_date: Optional[datetime.date] = Query(None, description="Filter records on or before this date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination offset)"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return (1-200)"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    **All authenticated roles.** Retrieve a paginated, filtered list of financial records.

    Supports filtering by:
    - `type` — income or expense
    - `category` — partial text match (e.g., "rent" matches "Monthly Rent")
    - `from_date` / `to_date` — date range filter
    Filters out softly deleted records automatically.
    """
    filters = RecordFilter(q=q, type=type, category=category, from_date=from_date, to_date=to_date)
    return financial_service.get_all_records(db, filters, skip, limit)


@router.get(
    "/{record_id}",
    response_model=RecordResponse,
    summary="[All Roles] Get a single financial record",
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """**All authenticated roles.** Retrieve the full details of a specific record."""
    return financial_service.get_record_by_id(db, record_id)


@router.put(
    "/{record_id}",
    response_model=RecordResponse,
    summary="[Admin] Update an existing financial record",
)
def update_record(
    record_id: int,
    data: RecordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """
    **Admin only.** Partially update a financial record.

    Only fields included in the request body are updated — omitted fields remain unchanged.
    """
    return financial_service.update_record(db, record_id, data)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a financial record",
)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    """**Admin only.** Permanently delete a financial record."""
    financial_service.delete_record(db, record_id)
