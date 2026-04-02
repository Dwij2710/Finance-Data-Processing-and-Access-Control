"""
seed.py — Populate the database with sample data for testing.

Creates 3 users (one per role) and 60 randomized financial records
spread across the year 2025.

Usage:
    python seed.py

Run this AFTER the server has been started at least once (so tables exist),
OR it will create the tables itself via Base.metadata.create_all.
"""

import random
from datetime import date, timedelta

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.financial import FinancialRecord, RecordType
from app.core.security import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # Guard: skip if already seeded
    if db.query(User).count() > 0:
        print("⚠️  Database already has data. Skipping seed to avoid duplicates.")
        print("    Delete finance.db and re-run to start fresh.\n")
        db.close()
        return

    print("🌱 Seeding database...\n")

    # ── Users ──────────────────────────────────────────────────────────────────
    users = [
        User(
            name="Alice Admin",
            email="admin@finance.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.admin,
            is_active=True,
        ),
        User(
            name="Bob Analyst",
            email="analyst@finance.com",
            hashed_password=hash_password("analyst123"),
            role=UserRole.analyst,
            is_active=True,
        ),
        User(
            name="Carol Viewer",
            email="viewer@finance.com",
            hashed_password=hash_password("viewer123"),
            role=UserRole.viewer,
            is_active=True,
        ),
    ]

    for u in users:
        db.add(u)
    db.commit()
    for u in users:
        db.refresh(u)

    admin_user = users[0]
    analyst_user = users[1]

    # ── Financial Records ──────────────────────────────────────────────────────
    income_categories = ["Salary", "Freelance", "Investment Returns", "Bonus", "Rental Income", "Consulting"]
    expense_categories = ["Rent", "Utilities", "Marketing", "Staff Salaries", "Office Supplies", "Travel", "Software & Subscriptions", "Equipment"]

    records = []
    base_date = date(2025, 1, 1)

    for i in range(60):
        is_income = random.random() > 0.42  # ~58% income, 42% expense
        record_date = base_date + timedelta(days=random.randint(0, 364))
        creator = random.choice([admin_user, analyst_user])

        if is_income:
            record = FinancialRecord(
                amount=round(random.uniform(1000.0, 50000.0), 2),
                type=RecordType.income,
                category=random.choice(income_categories),
                date=record_date,
                description=f"Income entry #{i + 1} — auto-seeded",
                created_by=creator.id,
            )
        else:
            record = FinancialRecord(
                amount=round(random.uniform(100.0, 15000.0), 2),
                type=RecordType.expense,
                category=random.choice(expense_categories),
                date=record_date,
                description=f"Expense entry #{i + 1} — auto-seeded",
                created_by=creator.id,
            )
        records.append(record)

    for r in records:
        db.add(r)
    db.commit()

    print(f"✅ Created {len(users)} users")
    print(f"✅ Created {len(records)} financial records")
    print()
    print("━" * 45)
    print("  Test Credentials")
    print("━" * 45)
    print(f"  Admin   →  admin@finance.com   / admin123")
    print(f"  Analyst →  analyst@finance.com / analyst123")
    print(f"  Viewer  →  viewer@finance.com  / viewer123")
    print("━" * 45)
    print()
    print("  Interactive API Docs: http://localhost:8000/docs")
    print()

    db.close()


if __name__ == "__main__":
    seed()
