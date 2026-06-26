import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    author: str = Field(..., min_length=1, max_length=200)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    genre: str = Field(..., min_length=1, max_length=80)
    cover_url: Optional[str] = None

    has_pdf: bool = False
    pdf_url: Optional[str] = None

    has_audio: bool = False
    audio_url: Optional[str] = None

    has_hardcopy: bool = False
    hardcopy_total: int = Field(0, ge=0)
    hardcopy_available: Optional[int] = Field(None, ge=0)

    total_pages: Optional[int] = Field(None, ge=0)
    audio_duration_sec: Optional[int] = Field(None, ge=0)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    """All fields optional — only the ones provided get updated (PATCH-like PUT)."""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    genre: Optional[str] = Field(None, min_length=1, max_length=80)
    cover_url: Optional[str] = None

    has_pdf: Optional[bool] = None
    pdf_url: Optional[str] = None

    has_audio: Optional[bool] = None
    audio_url: Optional[str] = None

    has_hardcopy: Optional[bool] = None
    hardcopy_total: Optional[int] = Field(None, ge=0)
    hardcopy_available: Optional[int] = Field(None, ge=0)
    total_pages: Optional[int] = Field(None, ge=0)
    audio_duration_sec: Optional[int] = Field(None, ge=0)


class BookOut(BookBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BookOut]
    hardcopy_available: Optional[int] = None  # Include this field if format=hardcopy and available_only=true in the request


class GenreShelf(BaseModel):
    genre: str
    books: List[BookOut]
