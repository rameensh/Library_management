import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from unittest.mock import Base
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(300), nullable=False, index=True)
    author = Column(String(200), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=True)
    description = Column(String, nullable=True)
    genre = Column(String(80), nullable=False, index=True)
    cover_url = Column(String, nullable=True)

    has_pdf = Column(Boolean, default=False, nullable=False)
    pdf_url = Column(String, nullable=True)

    has_audio = Column(Boolean, default=False, nullable=False)
    audio_url = Column(String, nullable=True)

    has_hardcopy = Column(Boolean, default=False, nullable=False)
    hardcopy_total = Column(Integer, default=0, nullable=False) # this will show that in total how many hardcopies the library has
    hardcopy_available = Column(Integer, default=0, nullable=False)

    total_pages = Column(Integer, nullable=True)
    audio_duration_sec = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Book {self.title!r} by {self.author!r}>"
    

"""USERS
  user_id (PK)
  username
  email
  password_hash
  address
  is_private
  avatar_url
  created_at"""

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    address = Column(String(200), nullable=True)
    is_private = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String, nullable=True)
    role = Column(String(20), default="user", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.username!r} ({self.email!r})>"
    

class BookInventory(Base):
    __tablename__ = "book_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    copy_number = Column(Integer, nullable=False)  # copy 1, copy 2, copy 3 etc
    condition = Column(String(50), default="good")  # good, damaged, lost
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    book = relationship("Book")

    hardcopy_transactions = relationship(
        "HardcopyTransaction",
        back_populates="inventory"
    )
    
    def __repr__(self) -> str:  # pragma: no cover
        return f"<BookInventory {self.id!r} for Book {self.book_id!r} - Copy {self.copy_number!r} ({self.condition!r})>"

class HardcopyTransaction(Base):
    __tablename__ = "hardcopy_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("book_inventory.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(20), nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    returned_at = Column(DateTime(timezone=True))
    delivery_fee = Column(Float, default=0.0)
    delivery_address = Column(String, nullable=True)

    inventory = relationship(
        "BookInventory",
        back_populates="hardcopy_transactions"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HardcopyTransaction {self.id!r} for Book {self.book_id!r} - User {self.user_id!r}>"
