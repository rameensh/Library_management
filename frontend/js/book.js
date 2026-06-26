// book.js — renders a single book's detail page.

function getBookIdFromURL() {
  return new URLSearchParams(window.location.search).get("id");
}

function formatCardHTML({ available, icon, title, body, cta, href, disabledReason }) {
  const action = href
    ? `<a class="btn btn-amber" href="${href}">${cta}</a>`
    : `<button class="btn btn-outline" disabled title="${disabledReason}">${cta}</button>`;

  return `
    <div class="format-card${available ? "" : " is-unavailable"}">
      <span class="eyebrow">${icon}</span>
      <h4>${title}</h4>
      <p>${body}</p>
      ${action}
    </div>
  `;
}

function renderFormats(book) {
  const cards = [];

  const pdfProgress = book.has_pdf ? getPdfProgress(book.id) : null;
  const hasStarted = pdfProgress && pdfProgress.percent > 0;

  cards.push(
    formatCardHTML({
      available: book.has_pdf,
      icon: "📄 PDF",
      title: book.has_pdf ? "Read on screen" : "No PDF edition",
      body: book.has_pdf
        ? hasStarted
          ? `${pdfProgress.percent}% read — page ${pdfProgress.page} of ${pdfProgress.totalPages}. Picks up where you left off.`
          : `${book.total_pages ? book.total_pages + " pages. " : ""}Opens right here, tracks your page as you go.`
        : "This title isn't available as a PDF.",
      cta: hasStarted ? "Resume reading" : "Open PDF",
      href: book.has_pdf ? `reader.html?id=${book.id}` : null,
      disabledReason: "This title isn't available as a PDF.",
    })
  );

  cards.push(
    formatCardHTML({
      available: book.has_audio,
      icon: "🎧 Audio",
      title: book.has_audio ? "Listen instead" : "No audio edition",
      body: book.has_audio
        ? `${formatDuration(book.audio_duration_sec) || "Runtime varies"} listen, resume where you left off.`
        : "This title isn't available as an audiobook.",
      cta: "Play audio",
      disabledReason: "Listening requires an account — not part of this module yet.",
    })
  );

  if (book.has_hardcopy) {
    const out = book.hardcopy_available <= 0;
    const user = getUser ? getUser() : null;
    const token = localStorage.getItem('bibliotheca:token');
    
    let borrowButton = '';
    if (!out && token) {
      borrowButton = `<button class="btn btn-amber" onclick="quickBorrow('${book.id}', '${escapeHTML(book.title)}')">📚 Request hardcopy</button>`;
    } else if (!out && !token) {
      borrowButton = `<a href="login.html" class="btn btn-amber">🔐 Sign in to borrow</a>`;
    } else {
      borrowButton = `<button class="btn btn-outline" disabled>Join waitlist</button>`;
    }
    
    cards.push(`
      <div class="format-card${out ? " is-unavailable" : ""}">
        <span class="eyebrow">📚 Hardcopy</span>
        <h4>${out ? "All copies checked out" : "Borrow a copy"}</h4>
        <p>${out 
          ? `0 of ${book.hardcopy_total} copies in. Typically back on the shelf within 1–2 weeks.`
          : `${book.hardcopy_available} of ${book.hardcopy_total} copies available. One copy per reader at a time.`
        }</p>
        ${borrowButton}
      </div>
    `);
  }

  return cards.join("");
}

// ─── Quick Borrow Function (for book detail page) ───

window.quickBorrow = async function(bookId, bookTitle) {
  const token = localStorage.getItem('bibliotheca:token');
  
  if (!token) {
    alert('Please sign in first!');
    window.location.href = 'login.html';
    return;
  }
  
  if (!confirm(`📚 Borrow "${bookTitle}"?\n\nYou'll have 14 days to return it.`)) return;
  
  try {
    const res = await fetch(`${API_BASE_URL}/api/book_inventory/borrow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ book_id: bookId })
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data.detail || 'Borrow failed');
    }
    
    alert(`✅ "${bookTitle}" borrowed successfully!\n\nDue date: ${new Date(data.due_date).toLocaleDateString()}`);
    window.location.reload();
  } catch(err) {
    alert('❌ ' + err.message);
  }
};

// ─── Get User Helper ────────────────────────────────────────

function getUser() {
  try {
    const raw = localStorage.getItem('bibliotheca:user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

// ─── Render Book ─────────────────────────────────────────────

async function renderBook() {
  const root = document.getElementById("book-root");
  const id = getBookIdFromURL();

  if (!id) {
    root.innerHTML = `<p class="error-state">No book selected. Head back to the <a href="catalogue.html">catalogue</a>.</p>`;
    return;
  }

  try {
    const book = await BooksAPI.getBook(id);
    document.title = `${book.title} — Bibliotheca`;

    // ─── NEW: Apply genre-based theme ───
    if (book.genre && typeof notifyGenreChange === 'function') {
      notifyGenreChange(book.genre);
    }

    const cover = book.cover_url || placeholderCover(book.title);

    document.getElementById("detail-hero").innerHTML = `
      <div class="container detail-layout">
        <img class="detail-cover" src="${cover}" alt="Cover of ${escapeHTML(book.title)}"
             onerror="this.src='${placeholderCover(book.title)}'">
        <div>
          <span class="detail-genre" data-genre="${escapeHTML(book.genre)}">${escapeHTML(book.genre)}</span>
          <h1>${escapeHTML(book.title)}</h1>
          <p class="detail-author">by ${escapeHTML(book.author)}</p>
          <div class="detail-meta-row">
            ${book.total_pages ? `<span>${book.total_pages} pages</span>` : ""}
            ${book.audio_duration_sec ? `<span>${formatDuration(book.audio_duration_sec)} audio</span>` : ""}
            ${book.isbn ? `<span>ISBN ${escapeHTML(book.isbn)}</span>` : ""}
          </div>
          ${book.description ? `<p class="detail-desc">${escapeHTML(book.description)}</p>` : ""}
        </div>
      </div>
    `;

    root.innerHTML = `
      <div class="container">
        <h2 style="font-size:1.5rem;color:var(--text-primary);">Available formats</h2>
        <div class="format-grid">${renderFormats(book)}</div>
        <p class="detail-note">PDF reading works right here, with progress saved on this browser. Audio and hardcopy actions require an account.</p>
      </div>
    `;
  } catch (err) {
    root.innerHTML = `<p class="error-state">Couldn't load this book. (${escapeHTML(err.message)})</p>`;
  }
}

// ─── Initialize ──────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", renderBook);