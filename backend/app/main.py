from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import books
from app.api.routes import auth
from app.core.config import settings
from app.core.database import Base, engine
from app.api.routes import users, inventory
from app.api.routes import hardcopy_transactions

# In a larger system this would be handled by Alembic migrations.
# For this standalone Books module, create-on-startup keeps setup to one step.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(hardcopy_transactions.router)

@app.get("/")
def root():
    return {"service": "bibliotheca-books-api", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


