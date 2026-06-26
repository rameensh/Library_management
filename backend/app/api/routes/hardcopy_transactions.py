import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.models.models import Book, BookInventory, HardcopyTransaction, User
from app.schemas.hardcopy_transaction import (  
    BookAvailabilityOut,
    BorrowRequest,
    ReturnRequest,
    TransactionOut,
    UpdateRequest,
    OverdueSummaryOut,
    ReturnBorrowedBookUser
)

from app.auth2 import get_current_user
from app.schemas import book

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

# route to get all book inventory items
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

# these starting from route 1 to route 4 are admin specific routes
# route 1 - to get all the trasaction from the database without pagination
# @router.get("/all", response_model=List[TransactionOut])
# def get_all_transactions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized to access this resource")
#     transactions = (
#         db.query(HardcopyTransaction)
#         .order_by(HardcopyTransaction.issued_at.desc())
#         .all()
#    )
#     return transactions

@router.get("/current", response_model=List[TransactionOut])
def get_current_borrowed_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all books currently borrowed by the logged-in user"""
    try:
        transactions = (
            db.query(HardcopyTransaction)
            .filter(
                HardcopyTransaction.user_id == current_user.id,
                HardcopyTransaction.returned_at.is_(None)
            )
            .order_by(HardcopyTransaction.issued_at.desc())
            .all()
        )
        
        # If no transactions, return empty list
        if not transactions:
            return []
        
        result = []
        for t in transactions:
            try:
                result.append(
                    TransactionOut(
                        id=t.id,
                        book_id=t.book_id,
                        inventory_id=t.inventory_id,
                        user_id=t.user_id,
                        action=t.action if t.action else "borrowed",
                        issued_at=t.issued_at,
                        due_date=t.due_date,
                        returned_at=t.returned_at,
                        delivery_fee=float(t.delivery_fee) if t.delivery_fee is not None else 0.0,
                        delivery_address=t.delivery_address if t.delivery_address else None,
                    )
                )
            except Exception as e:
                print(f"Error converting transaction {t.id}: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"Error in current endpoint: {e}")
        return []


@router.get("/history", response_model=List[TransactionOut])
def get_user_transaction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete transaction history for the logged-in user"""
    try:
        transactions = (
            db.query(HardcopyTransaction)
            .filter(HardcopyTransaction.user_id == current_user.id)
            .order_by(HardcopyTransaction.issued_at.desc())
            .all()
        )
        
        # If no transactions, return empty list
        if not transactions:
            return []
        
        result = []
        for t in transactions:
            try:
                result.append(
                    TransactionOut(
                        id=t.id,
                        book_id=t.book_id,
                        inventory_id=t.inventory_id,
                        user_id=t.user_id,
                        action=t.action if t.action else "borrowed",
                        issued_at=t.issued_at,
                        due_date=t.due_date,
                        returned_at=t.returned_at,
                        delivery_fee=float(t.delivery_fee) if t.delivery_fee is not None else 0.0,
                        delivery_address=t.delivery_address if t.delivery_address else None,
                    )
                )
            except Exception as e:
                print(f"Error converting transaction {t.id}: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"Error in history endpoint: {e}")
        return []


@router.get("/overdue", response_model=List[TransactionOut])
def get_overdue_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # If not admin, return empty list
        if current_user.role != "admin":
            return []
        
        now = datetime.now(timezone.utc)
        overdue_transactions = (
            db.query(HardcopyTransaction)
            .filter(
                HardcopyTransaction.due_date < now,
                HardcopyTransaction.returned_at.is_(None)
            )
            .order_by(HardcopyTransaction.due_date.asc())
            .all()
        )
        
        # If no overdue transactions, return empty list
        if not overdue_transactions:
            return []
        
        result = []
        for t in overdue_transactions:
            try:
                result.append(
                    TransactionOut(
                        id=t.id,
                        book_id=t.book_id,
                        inventory_id=t.inventory_id,
                        user_id=t.user_id,
                        action=t.action if t.action else "borrowed",
                        issued_at=t.issued_at,
                        due_date=t.due_date,
                        returned_at=t.returned_at,
                        delivery_fee=float(t.delivery_fee) if t.delivery_fee is not None else 0.0,
                        delivery_address=t.delivery_address if t.delivery_address else None,
                    )
                )
            except Exception as e:
                print(f"Error converting transaction {t.id}: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"Error in overdue endpoint: {e}")
        return []
    

@router.get("/all", response_model=List[TransactionOut])
def get_all_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If not admin, return empty list instead of 403
    if current_user.role != "admin":
        return []
    
    transactions = (
        db.query(HardcopyTransaction)
        .order_by(HardcopyTransaction.issued_at.desc())
        .all()
    )
    
    result = []
    for t in transactions:
        result.append(
            TransactionOut(
                id=t.id,
                book_id=t.book_id,
                inventory_id=t.inventory_id,
                user_id=t.user_id,
                action=t.action if t.action else "borrowed",
                issued_at=t.issued_at,
                due_date=t.due_date,
                returned_at=t.returned_at,
                delivery_fee=float(t.delivery_fee) if t.delivery_fee is not None else 0.0,
                delivery_address=t.delivery_address if t.delivery_address else None,
            )
        )
    
    return result

# route 2 - this route will help getting a single transaction by its id
@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction_by_id(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = (
        db.query(HardcopyTransaction)
        .filter(HardcopyTransaction.id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    if (
        current_user.role != "admin"
        and transaction.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )

    return transaction

# route 3 - now the rouute to update the transactio if suppose admin made a msitake in the transaction
@router.put("/update/{transaction_id}/admin", response_model=TransactionOut)
def update_transaction(
     payload : UpdateRequest,
     transaction_id: uuid.UUID,
     db: Session = Depends(get_db),
     current_user: User = Depends(get_current_user)
):
    transaction = (
        db.query(HardcopyTransaction)
        .filter(HardcopyTransaction.id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )
    
    # Update the transaction fields based on the payload
    if payload.due_date is not None:
        transaction.due_date = payload.due_date

    if payload.returned_at is not None:
        transaction.returned_at = payload.returned_at

    if payload.delivery_fee is not None:
        transaction.delivery_fee = payload.delivery_fee
    db.commit()
    db.refresh(transaction)
    return transaction
    
# route 4 - this route will help an admin to delete a transaction by its id
@router.delete("/delete/{transaction_id}/admin")
def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = (
        db.query(HardcopyTransaction)
        .filter(HardcopyTransaction.id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )

    db.delete(transaction)
    db.commit()
    return {"detail": "Transaction deleted successfully"}

# Now from here we will start creating user focused routes 
# route 5 - using this route a particular login usser can check history of borrowing and returning books
# @router.get("/history", response_model=List[TransactionOut])
# def get_user_transaction_history(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     transactions = (
#         db.query(HardcopyTransaction)
#         .filter(HardcopyTransaction.user_id == current_user.id)
#         .order_by(HardcopyTransaction.issued_at.desc())
#         .all()
#     )
#     return transactions

    
    # Debug: Print the first transaction to see what's in it
    # if transactions:
    #     print("First transaction:", transactions[0].__dict__)
    

# route 6 - this route will help the user to check his/her's current borrowed books and their due dates
# @router.get("/current", response_model=List[TransactionOut])
# def get_current_borrowed_books(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     transactions = (
#         db.query(HardcopyTransaction)
#         .filter(
#             HardcopyTransaction.user_id == current_user.id,
#             HardcopyTransaction.returned_at.is_(None)
#         )
#         .order_by(HardcopyTransaction.issued_at.desc())
#         .all()
#         # the query says Give me all books currently borrowed by the logged-in user that have not yet been returned.
#     )
#     return transactions
    

# Now thw routes will be related with Inventory of books
# route 7 - this route will help to check available copies of a particular book in the library
@router.get(
    "/book/{book_id}/availability",
    response_model=BookAvailabilityOut
)
def get_book_availability(
    book_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    total_copies = (
        db.query(BookInventory)
        .filter(BookInventory.book_id == book_id)
        .count()
    )

    available_copies = (
        db.query(BookInventory)
        .filter(
            BookInventory.book_id == book_id,
            BookInventory.is_available.is_(True)
        )
        .count()
    )

    borrowed_copies = total_copies - available_copies

    return {
        "book_id": book_id,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "borrowed_copies": borrowed_copies
    }

# route 8 - this route will tell the admin who borrowed a particular book and when it is due to be returned
@router.get("/book/{book_id}/borrowers",response_model=List[TransactionOut])
def get_book_borrowers(
    book_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )
    
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    transactions = (
        db.query(HardcopyTransaction)
        .filter(
            HardcopyTransaction.book_id == book_id,
            HardcopyTransaction.returned_at.is_(None)
        )
        .order_by(HardcopyTransaction.issued_at.desc())
        .all()
    )

    return transactions

# Now the routes will be related  to overdue management
# route 9 - this route will help the admin to get all the overdue books
# @router.get("/overdue", response_model=List[TransactionOut])
# def get_overdue_transactions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if current_user.role != "admin":
#         raise HTTPException(
#             status_code=403,
#             detail="Not authorized to access this resource"
#         )

#     now = datetime.now(timezone.utc)

#     overdue_transactions = (
#         db.query(HardcopyTransaction)
#         .filter(
#             HardcopyTransaction.due_date < now,
#             HardcopyTransaction.returned_at.is_(None)
#         )
#         .order_by(HardcopyTransaction.due_date.asc())
#         .all()
#     )

#     return overdue_transactions

# @router.get("/overdue", response_model=List[TransactionOut])
# def get_overdue_transactions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # If not admin, return empty list instead of 403
#     if current_user.role != "admin":
#         return []
    
#     now = datetime.now(timezone.utc)
#     overdue_transactions = (
#         db.query(HardcopyTransaction)
#         .filter(
#             HardcopyTransaction.due_date < now,
#             HardcopyTransaction.returned_at.is_(None)
#         )
#         .order_by(HardcopyTransaction.due_date.asc())
#         .all()
#     )
    
#     result = []
#     for t in overdue_transactions:
#         result.append(
#             TransactionOut(
#                 id=t.id,
#                 book_id=t.book_id,
#                 inventory_id=t.inventory_id,
#                 user_id=t.user_id,
#                 action=t.action if t.action else "borrowed",
#                 issued_at=t.issued_at,
#                 due_date=t.due_date,
#                 returned_at=t.returned_at,
#                 delivery_fee=float(t.delivery_fee) if t.delivery_fee is not None else 0.0,
#                 delivery_address=t.delivery_address if t.delivery_address else None,
#             )
#         )
    
#     return result

# route 10 - Specific users overdue status
@router.get("/overdue/user/{user_id}", response_model=List[TransactionOut])
def get_user_overdue_transactions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )

    now = datetime.now(timezone.utc)

    overdue_transactions = (
        db.query(HardcopyTransaction)
        .filter(
            HardcopyTransaction.user_id == user_id,
            HardcopyTransaction.due_date < func.now(),
            HardcopyTransaction.returned_at.is_(None)
        )
        .order_by(HardcopyTransaction.due_date.asc())
        .all()
    )

    return overdue_transactions

@router.get(
    "/overdue/summary",
    response_model=OverdueSummaryOut
)
def get_overdue_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )

    now = datetime.now(timezone.utc)

    overdue_transactions = (
        db.query(HardcopyTransaction)
        .filter(
            HardcopyTransaction.due_date < now,
            HardcopyTransaction.returned_at.is_(None)
        )
        .all()
    )

    total_overdue_books = len(overdue_transactions)

    total_users_with_overdues = len(
        {t.user_id for t in overdue_transactions}
    )

    longest_overdue_days = 0

    if overdue_transactions:
        longest_overdue_days = max(
            (now - t.due_date).days
            for t in overdue_transactions
        )

    return {
        "total_overdue_books": total_overdue_books,
        "total_users_with_overdues": total_users_with_overdues,
        "longest_overdue_days": longest_overdue_days
    }

# route 12 - route to check if user already has a book
@router.get(
    "/users/{user_id}/active",
    response_model=ReturnBorrowedBookUser
)
def get_users_with_book(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    transaction = (
        db.query(HardcopyTransaction)
        .filter(
            HardcopyTransaction.user_id == current_user.id,
            HardcopyTransaction.returned_at.is_(None)
        )
        .first()
    )

    if not transaction:
        return {
            "has_active_book": False,
            "book_id": None
        }

    return {
        "has_active_book": True,
        "book_id": transaction.book_id
    }

@router.get("/debug-current")
def debug_current(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to see what's actually being returned"""
    transactions = (
        db.query(HardcopyTransaction)
        .filter(
            HardcopyTransaction.user_id == current_user.id,
            HardcopyTransaction.returned_at.is_(None)
        )
        .all()
    )
    
    result = []
    for t in transactions:
        result.append({
            "id": str(t.id),
            "book_id": str(t.book_id),
            "inventory_id": str(t.inventory_id),
            "user_id": str(t.user_id),
            "action": t.action,
            "issued_at": t.issued_at.isoformat() if t.issued_at else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "returned_at": t.returned_at.isoformat() if t.returned_at else None,
            "delivery_fee": float(t.delivery_fee) if t.delivery_fee else 0.0,
            "delivery_address": t.delivery_address,
        })
    
    return {
        "count": len(result),
        "user_id": str(current_user.id),
        "username": current_user.username,
        "transactions": result
    }