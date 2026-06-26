// progress.js — browser-only PDF reading progress.
//
// No backend involved: progress is saved per-device/per-browser via
// localStorage, not tied to a real account (there's no auth system yet).
// Key format: bibliotheca:pdf-progress:<bookId>

const PDF_PROGRESS_PREFIX = "bibliotheca:pdf-progress:";

function getCurrentUserId() {
  try {
    // get the token from localStorage
    const token = localStorage.getItem("bibliotheca:token");
    if (!token) return "guest";

    // JWT is three parts separated by dots: header.payload.signature
    // the payload is base64 encoded — decode it to get user_id
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id || "guest";
  } catch {
    return "guest";
  }
}

function getPdfProgress(bookId) {
  const key = PDF_PROGRESS_PREFIX + getCurrentUserId() + ":" + bookId;
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (err) {
    return null;
  }
}

function setPdfProgress(bookId, { page, totalPages }) {
  const percent = totalPages ? Math.round((page / totalPages) * 100) : 0;
  const data = { page, totalPages, percent, updatedAt: new Date().toISOString() };
  const key = PDF_PROGRESS_PREFIX + getCurrentUserId() + ":" + bookId;
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (err) {}
  return data;
}

function clearPdfProgress(bookId) {
  const key = PDF_PROGRESS_PREFIX + getCurrentUserId() + ":" + bookId;
  try {
    localStorage.removeItem(key);
  } catch (err) {}
}