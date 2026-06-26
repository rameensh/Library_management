import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
# from models.models import BookInventory
# from models.models import Book

from app.core.database import get_db
from app.models.models import Book, BookInventory, HardcopyTransaction, User
from app.schemas.book_inventory import (
    BookInventoryCreate,
    BookInventoryListResponse,
    BookInventoryOut,
    BookInventoryUpdate,
)
from app.schemas.hardcopy_transaction import (
    BorrowRequest,
    ReturnRequest,
    TransactionOut
)
from app.auth2 import get_current_user

router = APIRouter(prefix="/api/book_inventory", tags=["book_inventory"])

# route to get all book inventory items
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

@router.get("", response_model=BookInventoryListResponse)
def list_book_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(
        None,
        description="Matches book title or author"
    ),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    query = db.query(BookInventory)

    if search:
        like = f"%{search}%"

        query = (
            query
            .join(Book, BookInventory.book_id == Book.id)
            .filter(
                or_(
                    Book.title.ilike(like),
                    Book.author.ilike(like)
                )
            )
        )

    inventories = (
        query
        .order_by(BookInventory.created_at.desc())
        .all()
    )

    return {
        "items": inventories,
        "total": len(inventories)
    }

# now a route to create a book inventory item
@router.post("", response_model=BookInventoryOut)
def create_inventory(
    payload: BookInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    existing_copies = (
        db.query(BookInventory)
        .filter(BookInventory.book_id == payload.book_id)
        .count()
    )

    inventory = BookInventory(
        book_id=payload.book_id,
        copy_number=existing_copies + 1,
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    return inventory

# route to see all available copies of a particular book
@router.get("/book/{book_id}", response_model=List[BookInventoryOut])
def get_book_copies(
    book_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    copies = (
        db.query(BookInventory)
        .filter(BookInventory.book_id == book_id)
        .order_by(BookInventory.created_at.desc())
        .all()
    )

    return copies

# route to update inventory item condition or availability
@router.put("/{inventory_id}", response_model=BookInventoryOut)
def update_inventory(
    inventory_id: uuid.UUID,
    payload: BookInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    inventory = db.query(BookInventory).filter(BookInventory.id == inventory_id).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if payload.condition is not None:
        inventory.condition = payload.condition

    if payload.is_available is not None:
        inventory.is_available = payload.is_available

    db.commit()
    db.refresh(inventory)

    return inventory

# now /api/inventory/{book_id}/borrowedGET See which copies are out means borrowed 
@router.get("/{book_id}/borrowed", response_model=List[BookInventoryOut])
def get_borrowed_copies(
    book_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrowed_copies = (
        db.query(BookInventory)
        .filter(
            BookInventory.book_id == book_id,
            BookInventory.is_available == False
        )
        .order_by(BookInventory.created_at.desc())
        .all()
    )

    return borrowed_copies

# now route /api/inventory/overdueGET See all overdue books
# Meaning of query in this route:
# Give me all inventory copies that:
# are currently not available,
# their due date has passed,
# and they have not yet been returned.
@router.get("/overdue", response_model=List[BookInventoryOut])
def get_overdue_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    overdue_books = (
        db.query(BookInventory)
        .join(HardcopyTransaction)
        .filter(
            BookInventory.is_available == False,
            HardcopyTransaction.due_date < func.now(),
            HardcopyTransaction.returned_at.is_(None)
        )
        .order_by(HardcopyTransaction.due_date.asc())
        .all()
    )

    return overdue_books

# now a route to borrow a book copy, which will create a hardcopy transaction and mark the inventory item as unavailable
@router.post("/borrow", response_model=TransactionOut)
def borrow_book(
    payload: BorrowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.id == payload.book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    user = current_user

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    existing = (
            db.query(HardcopyTransaction)
            .filter(
                HardcopyTransaction.user_id == current_user.id,
                HardcopyTransaction.returned_at.is_(None)
            )
            .first()
        )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have a borrowed book. Return it first."
        )

    if book.hardcopy_available <= 0:
        raise HTTPException(
            status_code=400,
            detail="No copies available"
        )

    copy = (
        db.query(BookInventory)
        .filter(
            BookInventory.book_id == payload.book_id,
            BookInventory.is_available.is_(True)
        )
        .first()
    )

    if not copy:
        raise HTTPException(
            status_code=400,
            detail="No available copy found in inventory"
        )

    copy.is_available = False
    book.hardcopy_available -= 1

    transaction = HardcopyTransaction(
        book_id=payload.book_id,
        inventory_id=copy.id,
        user_id=current_user.id,
        action="borrowed",
        due_date=datetime.now(timezone.utc) + timedelta(days=14)
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

# @router.post("/return", response_model=TransactionOut)
# def return_book(
#     payload: ReturnRequest,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     transaction = db.query(HardcopyTransaction).filter(
#         HardcopyTransaction.book_id == payload.book_id,
#         HardcopyTransaction.user_id == current_user.id,
#         HardcopyTransaction.returned_at.is_(None)
#     ).first()

#     if not transaction:
#         raise HTTPException(
#             status_code=404,
#             detail="No active borrow found"
#         )

#     copy = db.query(BookInventory).filter(
#         BookInventory.id == transaction.inventory_id
#     ).first()

#     if not copy:
#         raise HTTPException(
#             status_code=404,
#             detail="Inventory copy not found"
#         )

#     copy.is_available = True

#     book = db.query(Book).filter(
#         Book.id == payload.book_id
#     ).first()

#     if not book:
#         raise HTTPException(
#             status_code=404,
#             detail="Book not found"
#         )

#     book.hardcopy_available += 1

#     transaction.returned_at = datetime.now(timezone.utc)
#     transaction.action = "returned"

#     db.commit()
#     db.refresh(transaction)

#     return transaction

@router.post("/return", response_model=TransactionOut)
def return_book(
    payload: ReturnRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the active transaction for this user and book
    transaction = db.query(HardcopyTransaction).filter(
        HardcopyTransaction.book_id == payload.book_id,
        HardcopyTransaction.user_id == current_user.id,
        HardcopyTransaction.returned_at.is_(None)
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="No active borrow found for this book"
        )

    # Find the inventory copy
    copy = db.query(BookInventory).filter(
        BookInventory.id == transaction.inventory_id
    ).first()

    if not copy:
        raise HTTPException(
            status_code=404,
            detail="Inventory copy not found"
        )

    # Mark copy as available
    copy.is_available = True

    # Update book available count
    book = db.query(Book).filter(
        Book.id == payload.book_id
    ).first()

    if book:
        book.hardcopy_available += 1

    # Update transaction
    transaction.returned_at = datetime.now(timezone.utc)
    transaction.action = "returned"

    db.commit()
    db.refresh(transaction)

    return transaction

@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    inventory = (
        db.query(BookInventory)
        .filter(BookInventory.id == inventory_id)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory copy not found"
        )

    # Don't allow deletion if currently borrowed
    if not inventory.is_available:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a borrowed copy"
        )

    book = (
        db.query(Book)
        .filter(Book.id == inventory.book_id)
        .first()
    )

    if book and book.hardcopy_available > 0:
        book.hardcopy_available -= 1

    db.delete(inventory)
    db.commit()

    return {
        "message": "Inventory copy deleted successfully"
    }