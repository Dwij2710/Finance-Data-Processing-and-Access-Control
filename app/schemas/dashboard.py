from pydantic import BaseModel
from typing import Optional
import datetime


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_records: int


class CategoryTotal(BaseModel):
    category: str
    type: str
    total: float
    count: int


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: float
    expenses: float
    net: float


class RecentRecord(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: datetime.date
    description: Optional[str]
