// api.js — thin wrapper around the Bibliotheca Books API.
// Change this to match your backend URL
const API_BASE_URL = "http://localhost:8000";  // ← Make sure this is 8000

async function apiGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

const BooksAPI = {
  getShelves(perShelf = 12) {
    return apiGet(`/api/books/shelves?per_shelf=${perShelf}`);
  },
  getGenres() {
    return apiGet(`/api/books/genres`);
  },
  listBooks({ search, genre, format, availableOnly, page = 1, pageSize = 20, sort = "title" } = {}) {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (genre) params.set("genre", genre);
    if (format) params.set("format", format);
    if (availableOnly) params.set("available_only", "true");
    params.set("page", page);
    params.set("page_size", pageSize);
    params.set("sort", sort);
    return apiGet(`/api/books?${params.toString()}`);
  },
  getBook(id) {
    return apiGet(`/api/books/${id}`);
  },
};

// ---- shared rendering helpers ----

function formatBadges(book) {
  const badges = [];
  if (book.has_pdf) badges.push(`<span class="badge badge-pdf">PDF</span>`);
  if (book.has_audio) badges.push(`<span class="badge badge-audio">Audio</span>`);
  if (book.has_hardcopy) {
    const out = book.hardcopy_available <= 0;
    badges.push(
      `<span class="badge badge-hardcopy${out ? " is-out" : ""}">${
        out ? "Hardcopy — out" : "Hardcopy"
      }</span>`
    );
  }
  return badges.join("");
}

function bookCardHTML(book) {
  const cover = book.cover_url || placeholderCover(book.title);
  return `
    <a class="book-card" href="book.html?id=${book.id}">
      <img class="book-cover" src="${cover}" alt="Cover of ${escapeHTML(book.title)}" loading="lazy"
           onerror="this.src='${placeholderCover(book.title)}'">
      <h4>${escapeHTML(book.title)}</h4>
      <p class="author">${escapeHTML(book.author)}</p>
      <div class="badges">${formatBadges(book)}</div>
    </a>
  `;
}

function placeholderCover(title) {
  const initials = encodeURIComponent((title || "?").slice(0, 1).toUpperCase());
  return `data:image/svg+xml,${encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="170" height="248">
      <rect width="170" height="248" fill="#EFE9DD"/>
      <text x="50%" y="54%" font-family="Georgia, serif" font-size="48" fill="#8B9BB4"
            text-anchor="middle" dominant-baseline="middle">${initials}</text>
    </svg>
  `)}`;
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatDuration(seconds) {
  if (!seconds) return null;
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.round((seconds % 3600) / 60);
  if (hrs && mins) return `${hrs} hr ${mins} min`;
  if (hrs) return `${hrs} hr`;
  return `${mins} min`;
}