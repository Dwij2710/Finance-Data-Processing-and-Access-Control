from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from typing import List

from app.models.financial import FinancialRecord, RecordType
from app.schemas.dashboard import SummaryResponse, CategoryTotal, MonthlyTrend, RecentRecord


def get_summary(db: Session) -> SummaryResponse:
    """
    Aggregate total income, total expenses, and compute net balance.
    Uses COALESCE to safely return 0 when no records exist.
    """
    total_income = (
        db.query(func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .filter(
            FinancialRecord.type == RecordType.income,
            FinancialRecord.deleted_at.is_(None)
        )
        .scalar()
    )

    total_expenses = (
        db.query(func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .filter(
            FinancialRecord.type == RecordType.expense,
            FinancialRecord.deleted_at.is_(None)
        )
        .scalar()
    )

    total_records = db.query(func.count(FinancialRecord.id)).filter(
        FinancialRecord.deleted_at.is_(None)
    ).scalar()

    return SummaryResponse(
        total_income=float(total_income),
        total_expenses=float(total_expenses),
        net_balance=float(total_income) - float(total_expenses),
        total_records=int(total_records),
    )


def get_category_totals(db: Session) -> List[CategoryTotal]:
    """
    Return total amounts and record counts grouped by category and type.
    Useful for category-wise breakdown on the dashboard.
    """
    results = (
        db.query(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.id).label("count"),
        )
        .filter(FinancialRecord.deleted_at.is_(None))
        .group_by(FinancialRecord.category, FinancialRecord.type)
        .order_by(FinancialRecord.type, func.sum(FinancialRecord.amount).desc())
        .all()
    )

    return [
        CategoryTotal(
            category=row.category,
            type=row.type.value,
            total=round(float(row.total), 2),
            count=row.count,
        )
        for row in results
    ]


def get_monthly_trends(db: Session, months: int = 12) -> List[MonthlyTrend]:
    """
    Return month-by-month income and expense totals.
    Results are aggregated by year+month, sorted chronologically.
    """
    results = (
        db.query(
            extract("year", FinancialRecord.date).label("year"),
            extract("month", FinancialRecord.date).label("month"),
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .filter(FinancialRecord.deleted_at.is_(None))
        .group_by("year", "month", FinancialRecord.type)
        .order_by("year", "month")
        .all()
    )

    # Merge income/expense rows into single MonthlyTrend objects keyed by (year, month)
    trends: dict = {}
    for row in results:
        key = (int(row.year), int(row.month))
        if key not in trends:
            trends[key] = {"year": int(row.year), "month": int(row.month), "income": 0.0, "expenses": 0.0}
        if row.type == RecordType.income:
            trends[key]["income"] = round(float(row.total), 2)
        else:
            trends[key]["expenses"] = round(float(row.total), 2)

    sorted_trends = sorted(trends.values(), key=lambda x: (x["year"], x["month"]))

    # Apply months limit after merging
    sorted_trends = sorted_trends[-months:]

    return [
        MonthlyTrend(
            year=v["year"],
            month=v["month"],
            income=v["income"],
            expenses=v["expenses"],
            net=round(v["income"] - v["expenses"], 2),
        )
        for v in sorted_trends
    ]


def get_recent_records(db: Session, limit: int = 10) -> List[RecentRecord]:
    """Return the most recent financial records ordered by date then creation time."""
    records = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.deleted_at.is_(None))
        .order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        RecentRecord(
            id=r.id,
            amount=r.amount,
            type=r.type.value,
            category=r.category,
            date=r.date,
            description=r.description,
        )
        for r in records
    ]
