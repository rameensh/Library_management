// catalogue.js — search, filter, and paginate the full catalogue.

const state = {
  search: "",
  genre: "",
  format: "",
  availableOnly: false,
  page: 1,
  pageSize: 18,
  sort: "title",
};

function readStateFromURL() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("search")) state.search = params.get("search");
  if (params.get("genre")) state.genre = params.get("genre");
  if (params.get("format")) state.format = params.get("format");
}

function syncURL() {
  const params = new URLSearchParams();
  if (state.search) params.set("search", state.search);
  if (state.genre) params.set("genre", state.genre);
  if (state.format) params.set("format", state.format);
  const qs = params.toString();
  history.replaceState(null, "", qs ? `?${qs}` : "catalogue.html");
}

async function loadGenrePills() {
  const wrap = document.getElementById("genre-pills");
  try {
    const genres = await BooksAPI.getGenres();
    wrap.innerHTML =
      `<button class="pill genre-pill${state.genre === "" ? " is-active" : ""}" data-genre="">All genres</button>` +
      genres
        .map(
          (g) =>
            `<button class="pill genre-pill${state.genre === g ? " is-active" : ""}" data-genre="${escapeHTML(g)}">${escapeHTML(g)}</button>`
        )
        .join("");

    wrap.querySelectorAll(".genre-pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.genre = btn.dataset.genre;
        state.page = 1;
        wrap.querySelectorAll(".genre-pill").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        syncURL();
        loadResults();
      });
    });
  } catch (err) {
    wrap.innerHTML = "";
  }
}

function wireFormatPills() {
  document.querySelectorAll(".format-pill").forEach((btn) => {
    if (btn.dataset.format === state.format) btn.classList.add("is-active");
    btn.addEventListener("click", () => {
      state.format = state.format === btn.dataset.format ? "" : btn.dataset.format;
      state.page = 1;
      document.querySelectorAll(".format-pill").forEach((b) => b.classList.remove("is-active"));
      if (state.format) btn.classList.add("is-active");
      syncURL();
      loadResults();
    });
  });
}

function wireSearchInput() {
  const input = document.getElementById("search-input");
  input.value = state.search;
  let debounce;
  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      state.search = input.value.trim();
      state.page = 1;
      syncURL();
      loadResults();
    }, 300);
  });
}

function wireSort() {
  const select = document.getElementById("sort-select");
  select.value = state.sort;
  select.addEventListener("change", () => {
    state.sort = select.value;
    state.page = 1;
    loadResults();
  });
}

function renderSkeletons() {
  const grid = document.getElementById("results-grid");
  grid.innerHTML = Array.from({ length: 8 })
    .map(() => `<div class="skeleton skeleton-card"></div>`)
    .join("");
}

// ─── Get User Helper ────────────────────────────────────────────────────────

function getUser() {
  try {
    const raw = localStorage.getItem('bibliotheca:user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

// ─── Quick Borrow Function (MAKE IT GLOBAL) ──────────────────────────────────

// DO NOT redeclare API_BASE_URL here - it's already in api.js
// Just use the existing one

// Define as a global function so onclick can find it
window.quickBorrow = async function(bookId, bookTitle) {
  console.log("quickBorrow called for:", bookTitle, bookId);
  
  const token = localStorage.getItem('bibliotheca:token');
  console.log("Token:", token ? "Present" : "Missing");
  
  if (!token) {
    alert('Please sign in first!');
    window.location.href = 'login.html';
    return;
  }
  
  if (!confirm(`Borrow "${bookTitle}"?\n\nYou'll have 14 days to return it.`)) return;
  
  try {
    console.log(" Sending borrow request to:", `${API_BASE_URL}/api/book_inventory/borrow`);
    const res = await fetch(`${API_BASE_URL}/api/book_inventory/borrow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ book_id: bookId })
    });
    
    const data = await res.json();
    console.log("🔵 Response:", data);
    
    if (!res.ok) {
      throw new Error(data.detail || 'Borrow failed');
    }
    
    alert(` "${bookTitle}" borrowed successfully!\n\nDue date: ${new Date(data.due_date).toLocaleDateString()}`);
    window.location.reload();
  } catch(err) {
    console.error("Borrow error:", err);
    alert('❌ ' + err.message);
  }
};

// ─── UPDATED: bookCardHTML with Borrow Button ──────────────────────────────

function bookCardHTML(book) {
  const cover = book.cover_url || placeholderCover(book.title);
  const hasAvailable = book.has_hardcopy && book.hardcopy_available > 0;
  const user = getUser();
  
  // Escape the book title for safe use in onclick
  const safeTitle = escapeHTML(book.title);
  
  let borrowButton = '';
  if (hasAvailable && user) {
    borrowButton = `
      <button class="btn btn-amber" style="margin-top:8px;width:100%;padding:6px;font-size:0.75rem;border-radius:4px;cursor:pointer;" 
              onclick="event.stopPropagation(); window.quickBorrow('${book.id}', '${safeTitle}')">
         Borrow
      </button>
    `;
  } else if (hasAvailable && !user) {
    borrowButton = `
      <a href="login.html" class="btn btn-ghost" style="margin-top:8px;width:100%;padding:6px;font-size:0.75rem;text-align:center;display:block;border:1px solid var(--paper-line);border-radius:4px;color:var(--ink-soft);text-decoration:none;">
         Sign in to borrow
      </a>
    `;
  } else {
    borrowButton = `
      <button class="btn btn-ghost" style="margin-top:8px;width:100%;padding:6px;font-size:0.75rem;border-radius:4px;cursor:not-allowed;opacity:0.5;border:1px solid var(--paper-line);" disabled>
         Unavailable
      </button>
    `;
  }
  
  return `
    <div class="book-card-wrapper" style="display:flex;flex-direction:column;height:100%;">
      <a class="book-card" href="book.html?id=${book.id}" style="flex:1;display:block;">
        <img class="book-cover" src="${cover}" alt="Cover of ${escapeHTML(book.title)}" loading="lazy"
             onerror="this.src='${placeholderCover(book.title)}'">
        <h4>${escapeHTML(book.title)}</h4>
        <p class="author">${escapeHTML(book.author)}</p>
        <div class="badges">${formatBadges(book)}</div>
      </a>
      ${borrowButton}
    </div>
  `;
}

// ─── Load Results ───────────────────────────────────────────────────────────

async function loadResults() {
  const grid = document.getElementById("results-grid");
  const meta = document.getElementById("results-meta");
  const pagination = document.getElementById("pagination");

  renderSkeletons();
  meta.textContent = "";
  pagination.innerHTML = "";

  try {
    const data = await BooksAPI.listBooks({
      search: state.search,
      genre: state.genre,
      format: state.format,
      availableOnly: state.availableOnly,
      page: state.page,
      pageSize: state.pageSize,
      sort: state.sort,
    });

    if (!data.items.length) {
      grid.innerHTML = `<p class="empty-state">No titles match those filters. Try widening the search.</p>`;
      meta.textContent = "";
      return;
    }

    grid.innerHTML = data.items.map(bookCardHTML).join("");

    const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));
    meta.textContent = `${data.total} title${data.total === 1 ? "" : "s"} found`;

    if (totalPages > 1) {
      pagination.innerHTML = `
        <button class="btn btn-outline" id="prev-page" ${state.page <= 1 ? "disabled" : ""}>← Previous</button>
        <span>Page ${data.page} of ${totalPages}</span>
        <button class="btn btn-outline" id="next-page" ${state.page >= totalPages ? "disabled" : ""}>Next →</button>
      `;
      document.getElementById("prev-page")?.addEventListener("click", () => {
        state.page -= 1;
        loadResults();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
      document.getElementById("next-page")?.addEventListener("click", () => {
        state.page += 1;
        loadResults();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  } catch (err) {
    grid.innerHTML = `<p class="error-state">Couldn't reach the library right now. Is the API running at ${API_BASE_URL}?<br>(${escapeHTML(err.message)})</p>`;
  }
}

// ─── Initialize ─────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  console.log("🔵 Catalogue.js loaded");
  readStateFromURL();
  wireSearchInput();
  wireFormatPills();
  wireSort();
  loadGenrePills();
  loadResults();
});