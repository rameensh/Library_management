"""
seed_books.py

Run with:  python seed_books.py
(from the backend/ directory, with DATABASE_URL set / venv active)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, SessionLocal, engine
from app.models.models import Book

Base.metadata.create_all(bind=engine)

SAMPLE_BOOKS = [
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "isbn": "9780735211292",
        "genre": "Motivational",
        "description": "An easy and proven way to build good habits and break bad ones.",
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg",
        "has_pdf": True,
        "pdf_url": "https://your-bucket.r2.dev/atomic-habits.pdf",
        "has_audio": True,
        "audio_url": "https://your-bucket.r2.dev/atomic-habits.mp3",
        "has_hardcopy": True,
        "hardcopy_total": 5,
        "hardcopy_available": 5,
        "total_pages": 320,
        "audio_duration_sec": 19080,
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "isbn": "9780062315007",
        "genre": "Fiction",
        "description": "A philosophical novel about a young Andalusian shepherd's journey.",
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780062315007-L.jpg",
        "has_pdf": True,
        "pdf_url": "https://your-bucket.r2.dev/the-alchemist.pdf",
        "has_audio": False,
        "audio_url": None,
        "has_hardcopy": True,
        "hardcopy_total": 3,
        "hardcopy_available": 3,
        "total_pages": 208,
        "audio_duration_sec": None,
    },
    {
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "isbn": "9780062316110",
        "genre": "Science",
        "description": "A brief history of humankind from the Stone Age to the present.",
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780062316110-L.jpg",
        "has_pdf": True,
        "pdf_url": "https://your-bucket.r2.dev/sapiens.pdf",
        "has_audio": True,
        "audio_url": "https://your-bucket.r2.dev/sapiens.mp3",
        "has_hardcopy": True,
        "hardcopy_total": 5,
        "hardcopy_available": 2,
        "total_pages": 443,
        "audio_duration_sec": 57600,
    },
    {
        "title": "Gone Girl",
        "author": "Gillian Flynn",
        "isbn": "9780307588371",
        "genre": "Mystery",
        "description": "A psychological thriller about a husband who becomes a suspect when his wife vanishes.",
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780307588371-L.jpg",
        "has_pdf": True,
        "pdf_url": "https://your-bucket.r2.dev/gone-girl.pdf",
        "has_audio": True,
        "audio_url": "https://your-bucket.r2.dev/gone-girl.mp3",
        "has_hardcopy": False,
        "hardcopy_total": 0,
        "hardcopy_available": 0,
        "total_pages": 422,
        "audio_duration_sec": 52200,
    },
    {
        "title": "Elon Musk",
        "author": "Walter Isaacson",
        "isbn": "9781982181284",
        "genre": "Biography",
        "description": "The inside story of the world's most controversial entrepreneur.",
        "cover_url": "https://covers.openlibrary.org/b/isbn/9781982181284-L.jpg",
        "has_pdf": False,
        "pdf_url": None,
        "has_audio": True,
        "audio_url": "https://your-bucket.r2.dev/elon-musk.mp3",
        "has_hardcopy": True,
        "hardcopy_total": 4,
        "hardcopy_available": 0,  # all copies checked out — exercises the ETA feature
        "total_pages": 688,
        "audio_duration_sec": 79200,
    },
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(Book).count()
        if existing:
            print(f"Database already has {existing} books. Skipping seed.")
            return
        for data in SAMPLE_BOOKS:
            db.add(Book(**data))
        db.commit()
        print(f"✓ Seeded {len(SAMPLE_BOOKS)} books successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
