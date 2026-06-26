# from unittest.mock import Base
# import uuid
# from datetime import datetime
# from typing import List, Optional

# from pydantic import BaseModel, ConfigDict, Field

# class BorrowRequest(BaseModel):
#     book_id: uuid.UUID
#     model_config = ConfigDict(extra="forbid")

# class TransactionOut(BaseModel):
#     id: uuid.UUID
#     book_id: uuid.UUID
#     inventory_id: uuid.UUID
#     user_id: uuid.UUID
#     action: str
#     issued_at: datetime
#     due_date: datetime | None
#     returned_at: datetime | None
#     delivery_fee: float = 0.0  # ← Add this field with default
#     delivery_address: Optional[str] = None  # ← Add this field

#     model_config = ConfigDict(from_attributes=True)

# class ReturnRequest(BaseModel):
#     book_id: uuid.UUID
#     model_config = ConfigDict(extra="forbid")

# class UpdateRequest(BaseModel):
#     transaction_id: uuid.UUID
#     due_date: datetime | None = None
#     returned_at: datetime | None = None
#     delivery_fee: float | None = None
#     model_config = ConfigDict(extra="forbid")

# class BookAvailabilityOut(BaseModel):
#     book_id: uuid.UUID
#     total_copies: int
#     available_copies: int
#     borrowed_copies: int

# class OverdueSummaryOut(BaseModel):
#     total_overdue_books: int
#     total_users_with_overdues: int
#     longest_overdue_days: int

# class ReturnBorrowedBookUser(BaseModel):
#     has_active_book: bool
#     book_id: uuid.UUID | None = None

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BorrowRequest(BaseModel):
    book_id: uuid.UUID
    model_config = ConfigDict(extra="forbid")


class TransactionOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    inventory_id: uuid.UUID
    user_id: uuid.UUID
    action: str
    issued_at: datetime
    due_date: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    delivery_fee: float = 0.0
    delivery_address: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ReturnRequest(BaseModel):
    book_id: uuid.UUID
    model_config = ConfigDict(extra="forbid")


class UpdateRequest(BaseModel):
    transaction_id: uuid.UUID
    due_date: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    delivery_fee: Optional[float] = None
    model_config = ConfigDict(extra="forbid")


class BookAvailabilityOut(BaseModel):
    book_id: uuid.UUID
    total_copies: int
    available_copies: int
    borrowed_copies: int


class OverdueSummaryOut(BaseModel):
    total_overdue_books: int
    total_users_with_overdues: int
    longest_overdue_days: int


class ReturnBorrowedBookUser(BaseModel):
    has_active_book: bool
    book_id: Optional[uuid.UUID] = None