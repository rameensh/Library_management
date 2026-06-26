// home.js — renders the genre shelves on the homepage.

async function renderShelves() {
  const root = document.getElementById("shelves-root");
  const stat = document.getElementById("hero-stat");
  
  if (!root) {
    console.error("shelves-root element not found!");
    return;
  }

  try {
    console.log("Fetching shelves from API...");
    const shelves = await BooksAPI.getShelves(12);

    if (!shelves || !shelves.length) {
      console.log("No shelves returned");
      root.innerHTML = `<p class="empty-state">The shelves are empty right now — run the seed script to add some books.</p>`;
      return;
    }

    const totalBooks = shelves.reduce((sum, s) => sum + s.books.length, 0);
    if (stat) {
      stat.innerHTML = `Currently lighting <strong>${totalBooks}+</strong> titles across <strong>${shelves.length}</strong> genres`;
    }

    root.innerHTML = shelves
      .map(
        (shelf) => `
        <div class="shelf">
          <div class="shelf-label">
            <h3>${escapeHTML(shelf.genre)}</h3>
            <span class="shelf-count">${shelf.books.length} title${shelf.books.length === 1 ? "" : "s"}</span>
          </div>
          <div class="shelf-row">
            ${shelf.books.map(bookCardHTML).join("")}
          </div>
        </div>
      `
      )
      .join("");
      
    console.log("Shelves rendered successfully!");
  } catch (err) {
    console.error("Error rendering shelves:", err);
    root.innerHTML = `<p class="error-state">Couldn't reach the library right now. Is the API running at ${API_BASE_URL}?<br>(${escapeHTML(err.message)})</p>`;
  }
}

function wireHeroSearch() {
  const form = document.getElementById("hero-search-form");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = form.querySelector("input").value.trim();
    window.location.href = q
      ? `catalogue.html?search=${encodeURIComponent(q)}`
      : "catalogue.html";
  });
}

// Make sure functions are available globally
window.renderShelves = renderShelves;
window.wireHeroSearch = wireHeroSearch;

// Auto-initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function() {
  console.log("home.js loaded - initializing...");
  renderShelves();
  wireHeroSearch();
});