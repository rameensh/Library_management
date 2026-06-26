import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class BookInventoryCreate(BaseModel):
    book_id: uuid.UUID

    model_config = ConfigDict(extra="forbid")


class BookInventoryUpdate(BaseModel):
    condition: Optional[str] = Field(
        None,
        description="Updated condition of the book copy"
    )

    is_available: Optional[bool] = Field(
        None,
        description="Availability status of the book copy"
    )

    model_config = ConfigDict(extra="forbid")

class InventoryBookInfo(BaseModel):
    title: str
    author: str

    model_config = ConfigDict(from_attributes=True)


class BookInventoryOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID

    book: InventoryBookInfo

    copy_number: int
    condition: str
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookInventoryListResponse(BaseModel):
    total: int
    items: List[BookInventoryOut]

    model_config = ConfigDict(extra="forbid")

