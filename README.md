# Bibliotheca — Books module

This is the **Books** slice of the larger library system: catalogue browsing,
search/filtering, genre shelves, and format/hardcopy-availability display.
Accounts, social features, subscriptions, and hardcopy *ordering* are out of
scope here (they belong to other modules in the architecture diagram) — the
book detail page shows what those modules would hook into, with disabled
preview buttons.

```
bibliotheca/
├── backend/     FastAPI + PostgreSQL
└── frontend/    Plain HTML/CSS/JS (no framework), "Bibliotheca" theme
```

## 1. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Database.** Either run Postgres via Docker:

```bash
docker compose up -d
```

...or point `DATABASE_URL` at any Postgres instance you already have. Copy
`.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

**Seed sample data** (creates tables if they don't exist, then inserts 5 sample books):

```bash
python seed_books.py
```

**Run the API:**

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger docs.

### Endpoints

| Method | Path                 | Purpose                                   |
|--------|----------------------|--------------------------------------------|
| GET    | `/api/books`         | Search/filter/paginate (`search`, `genre`, `format=pdf\|audio\|hardcopy`, `available_only`, `page`, `page_size`, `sort`) |
| GET    | `/api/books/genres`  | Distinct genres, homepage-shelf order first |
| GET    | `/api/books/shelves` | Books grouped by genre, for the homepage   |
| GET    | `/api/books/{id}`    | Single book detail                         |
| POST   | `/api/books`         | Create a book                              |
| PUT    | `/api/books/{id}`    | Update a book (partial)                    |
| DELETE | `/api/books/{id}`    | Delete a book                              |

## 2. Frontend setup

The frontend is static files — no build step, no framework. Serve it with
anything that gives it an HTTP origin (file:// will hit CORS issues with
`fetch`):

```bash
cd frontend
python3 -m http.server 5500
```

Then open `http://localhost:5500`. The API base URL defaults to
`http://localhost:8000`; to point elsewhere, set it before the other scripts
load, e.g. add to the `<head>` of any page:

```html
<script>window.BIBLIOTHECA_API_BASE_URL = "https://your-api.example.com";</script>
```

### Pages

- `index.html` — dark hero with the lamplight signature, then genre shelves
  pulled live from `/api/books/shelves`.
- `catalogue.html` — full search/filter/paginate view of `/api/books`.
- `book.html?id=<uuid>` — single book detail: description, page count /
  audio runtime, and a card per available format (PDF, audio, hardcopy with
  live copy counts and a simple "out of stock" message).

## Notes on the data model

The ERD's `BOOKS` entity didn't include direct file URLs (it implied a
separate `BOOK_FILES` table, one row per format). Since the seed data and
this module's scope call for one row per book, `pdf_url` and `audio_url`
were added directly to `books` alongside the existing `has_pdf` / `has_audio`
flags. If a later iteration needs multiple files per format (e.g. an EPUB
*and* a PDF for the same book), reintroducing `BOOK_FILES` as a child table
is the natural next step — the API shape here wouldn't need to change much,
since `BookOut` could just resolve `pdf_url` from the first matching file.



