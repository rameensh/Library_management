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
      icon: "PDF",
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
      icon: "Audio",
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
    cards.push(
      formatCardHTML({
        available: !out,
        icon: "Hardcopy",
        title: out ? "All copies checked out" : "Borrow a copy",
        body: out
          ? `0 of ${book.hardcopy_total} copies in. Typically back on the shelf within 1–2 weeks.`
          : `${book.hardcopy_available} of ${book.hardcopy_total} copies available. One copy per reader at a time.`,
        cta: out ? "Join waitlist" : "Request hardcopy",
        disabledReason: "Ordering requires an account — not part of this module yet.",
      })
    );
  }

  return cards.join("");
}

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

    const cover = book.cover_url || placeholderCover(book.title);

    document.getElementById("detail-hero").innerHTML = `
      <div class="container detail-layout">
        <img class="detail-cover" src="${cover}" alt="Cover of ${escapeHTML(book.title)}"
             onerror="this.src='${placeholderCover(book.title)}'">
        <div>
          <span class="detail-genre">${escapeHTML(book.genre)}</span>
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
        <h2 style="font-size:1.5rem;color:var(--ink);">Available formats</h2>
        <div class="format-grid">${renderFormats(book)}</div>
        <p class="detail-note">PDF reading works right here, with progress saved on this browser. Audio and hardcopy actions are previews — accounts and ordering live in other modules of the system.</p>
      </div>
    `;
  } catch (err) {
    root.innerHTML = `<p class="error-state">Couldn't load this book. (${escapeHTML(err.message)})</p>`;
  }
}

document.addEventListener("DOMContentLoaded", renderBook);
