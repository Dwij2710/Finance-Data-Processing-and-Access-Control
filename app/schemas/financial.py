from pydantic import BaseModel, Field
from typing import Optional
import datetime
from app.models.financial import RecordType


class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be a positive number", examples=[2500.00])
    type: RecordType = Field(..., examples=["income"])
    category: str = Field(..., min_length=1, max_length=100, examples=["Salary"])
    date: datetime.date = Field(..., examples=["2025-06-15"])
    description: Optional[str] = Field(None, max_length=500, examples=["Monthly salary deposit"])


class RecordUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[RecordType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[datetime.date] = None
    description: Optional[str] = Field(None, max_length=500)


class RecordResponse(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: str
    date: datetime.date
    description: Optional[str]
    created_by: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class RecordFilter(BaseModel):
    q: Optional[str] = Field(None, description="Search term for category or description")
    type: Optional[RecordType] = None
    category: Optional[str] = None
    from_date: Optional[datetime.date] = None
    to_date: Optional[datetime.date] = None
