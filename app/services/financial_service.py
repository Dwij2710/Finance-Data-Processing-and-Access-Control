from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import or_, func
from typing import List

from app.models.financial import FinancialRecord
from app.schemas.financial import RecordCreate, RecordUpdate, RecordFilter


def create_record(db: Session, data: RecordCreate, user_id: int) -> FinancialRecord:
    """Create and persist a new financial record."""
    record = FinancialRecord(
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date,
        description=data.description,
        created_by=user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record_by_id(db: Session, record_id: int) -> FinancialRecord:
    """Fetch a single financial record by ID (ignores soft-deleted). Raises 404 if not found."""
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.deleted_at.is_(None)
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial record with ID {record_id} not found.",
        )
    return record


def get_all_records(
    db: Session,
    filters: RecordFilter,
    skip: int = 0,
    limit: int = 50,
) -> List[FinancialRecord]:
    """
    Return a paginated, filtered list of financial records.
    Supports filtering by type, category (partial match), date range, and general search (q).
    """
    query = db.query(FinancialRecord).filter(FinancialRecord.deleted_at.is_(None))

    if filters.q:
        q_term = f"%{filters.q}%"
        query = query.filter(
            or_(
                FinancialRecord.category.ilike(q_term),
                FinancialRecord.description.ilike(q_term)
            )
        )
    if filters.type:
        query = query.filter(FinancialRecord.type == filters.type)
    if filters.category:
        query = query.filter(FinancialRecord.category.ilike(f"%{filters.category}%"))
    if filters.from_date:
        query = query.filter(FinancialRecord.date >= filters.from_date)
    if filters.to_date:
        query = query.filter(FinancialRecord.date <= filters.to_date)

    return (
        query.order_by(FinancialRecord.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_record(db: Session, record_id: int, data: RecordUpdate) -> FinancialRecord:
    """
    Partially update a financial record.
    Only fields explicitly provided in the request body are updated.
    """
    record = get_record_by_id(db, record_id)
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int) -> None:
    """Soft-delete a financial record by ID."""
    record = get_record_by_id(db, record_id)
    record.deleted_at = func.now()
    db.commit()
