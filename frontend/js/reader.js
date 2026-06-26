// reader.js — renders a book's PDF in-page (via PDF.js) and tracks reading
// progress as a page number + percentage, saved to localStorage.

pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

const readerParams = new URLSearchParams(window.location.search);
const bookId = readerParams.get("id");

let pdfDoc = null;
let currentPage = 1;
let scale = 1.2;
let rendering = false;
let pendingPage = null;

const canvas = document.getElementById("pdf-canvas");
const ctx = canvas.getContext("2d");
const statusEl = document.getElementById("reader-status");
const titleEl = document.getElementById("reader-title");
const pageIndicator = document.getElementById("page-indicator");
const progressFill = document.getElementById("reader-progress-fill");
const backLink = document.getElementById("reader-back");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.display = message ? "block" : "none";
  statusEl.classList.toggle("is-error", isError);
}

function updateProgressUI() {
  const percent = pdfDoc ? Math.round((currentPage / pdfDoc.numPages) * 100) : 0;
  pageIndicator.textContent = pdfDoc ? `${currentPage} / ${pdfDoc.numPages}` : "– / –";
  progressFill.style.width = `${percent}%`;
}

function renderPage(num) {
  rendering = true;
  currentPage = num;

  pdfDoc.getPage(num).then((page) => {
    const viewport = page.getViewport({ scale });
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    page.render({ canvasContext: ctx, viewport }).promise.then(() => {
      rendering = false;
      if (pendingPage !== null) {
        const next = pendingPage;
        pendingPage = null;
        renderPage(next);
      }
    });
  });

  updateProgressUI();
  if (bookId) setPdfProgress(bookId, { page: currentPage, totalPages: pdfDoc.numPages });
}

function queueRenderPage(num) {
  if (rendering) {
    pendingPage = num;
  } else {
    renderPage(num);
  }
}

function goToPage(num) {
  if (!pdfDoc) return;
  const clamped = Math.min(Math.max(num, 1), pdfDoc.numPages);
  queueRenderPage(clamped);
}

document.getElementById("prev-page").addEventListener("click", () => goToPage(currentPage - 1));
document.getElementById("next-page").addEventListener("click", () => goToPage(currentPage + 1));
document.getElementById("zoom-in").addEventListener("click", () => {
  scale = Math.min(scale + 0.2, 3);
  queueRenderPage(currentPage);
});
document.getElementById("zoom-out").addEventListener("click", () => {
  scale = Math.max(scale - 0.2, 0.5);
  queueRenderPage(currentPage);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") goToPage(currentPage + 1);
  if (e.key === "ArrowLeft") goToPage(currentPage - 1);
});

async function initReader() {
  if (!bookId) {
    setStatus("No book selected. Go back to the catalogue and pick one.", true);
    return;
  }
  backLink.href = `book.html?id=${bookId}`;

  try {
    const book = await BooksAPI.getBook(bookId);
    titleEl.textContent = book.title;
    document.title = `${book.title} — Reading`;

    if (!book.has_pdf || !book.pdf_url) {
      setStatus("This book doesn't have a PDF edition.", true);
      return;
    }

    setStatus("Loading PDF…");

    pdfDoc = await pdfjsLib.getDocument(book.pdf_url).promise;
    setStatus("");

    const saved = getPdfProgress(bookId);
    const startPage = saved && saved.page ? Math.min(saved.page, pdfDoc.numPages) : 1;

    goToPage(startPage);

    if (saved && saved.page > 1) {
      setStatus(`Resuming from page ${startPage} of ${pdfDoc.numPages}.`);
      setTimeout(() => setStatus(""), 3000);
    }
  } catch (err) {
    console.error(err);
    setStatus(
      `Couldn't load this PDF. This usually means the file URL isn't a real hosted file yet, or it doesn't allow cross-origin (CORS) access from this site. (${err.message})`,
      true
    );
  }
}

document.addEventListener("DOMContentLoaded", initReader);
