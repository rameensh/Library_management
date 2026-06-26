import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Book
from app.schemas.book import (
    BookCreate,
    BookListResponse,
    BookOut,
    BookUpdate,
    GenreShelf,
)

router = APIRouter(prefix="/api/books", tags=["books"])

# Matches the "Homepage genre shelves" order from the architecture diagram.
# Genres outside this list still show up, sorted alphabetically, after these.
GENRE_SHELF_ORDER = [
    "Fiction",
    "Motivational",
    "Mystery",
    "Science",
    "Biography",
    "Self-help",
]


def _ordered_genres(db: Session) -> List[str]:
    rows = db.query(Book.genre).distinct().all()
    present = {r[0] for r in rows}
    ordered = [g for g in GENRE_SHELF_ORDER if g in present]
    extra = sorted(g for g in present if g not in GENRE_SHELF_ORDER)
    return ordered + extra


@router.get("", response_model=BookListResponse)
def list_books(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Matches title or author"),
    genre: Optional[str] = Query(None),
    format: Optional[str] = Query(
        None, pattern="^(pdf|audio|hardcopy)$", description="pdf | audio | hardcopy"
    ),
    available_only: bool = Query(
        False, description="With format=hardcopy, only show titles with copies in stock"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("title", pattern="^(title|author|created_at)$"),
):
    query = db.query(Book)

    if search:
        like = f"%{search}%"
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))

    if genre:
        query = query.filter(Book.genre == genre)

    if format == "pdf":
        query = query.filter(Book.has_pdf.is_(True))
    elif format == "audio":
        query = query.filter(Book.has_audio.is_(True))
    elif format == "hardcopy":
        query = query.filter(Book.has_hardcopy.is_(True))
        if available_only:
            query = query.filter(Book.hardcopy_available > 0)

    total = query.count()

    sort_column = getattr(Book, sort)
    query = query.order_by(sort_column)

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return BookListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/genres", response_model=List[str])
def list_genres(db: Session = Depends(get_db)):
    return _ordered_genres(db)


@router.get("/shelves", response_model=List[GenreShelf])
def get_shelves(
    db: Session = Depends(get_db),
    per_shelf: int = Query(10, ge=1, le=50),
):
    shelves = []
    for genre in _ordered_genres(db):
        books = (
            db.query(Book)
            .filter(Book.genre == genre)
            .order_by(Book.created_at.desc())
            .limit(per_shelf)
            .all()
        )
        shelves.append(GenreShelf(genre=genre, books=books))
    return shelves


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=BookOut, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    if payload.isbn:
        existing = db.query(Book).filter(Book.isbn == payload.isbn).first()
        if existing:
            raise HTTPException(status_code=409, detail="A book with this ISBN already exists")

    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: uuid.UUID, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return None
