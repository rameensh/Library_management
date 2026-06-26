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

document.addEventListener("DOMContentLoaded", () => {
  readStateFromURL();
  wireSearchInput();
  wireFormatPills();
  wireSort();
  loadGenrePills();
  loadResults();
});
