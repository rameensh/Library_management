// catalogue.js - Updated borrow functions

const API_BASE_URL = window.BIBLIOTHECA_API_BASE_URL || "http://localhost:8000";
const AUTH_TOKEN_KEY = "bibliotheca:token";
const AUTH_USER_KEY = "bibliotheca:user";

// ── Helper Functions ──────────────────────────────────────────

function getToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

function getUser() {
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function isLoggedIn() {
  return !!getToken();
}

// ── Borrow Functions ──────────────────────────────────────────

async function quickBorrow(bookId, format = 'HARDCOPY') {
  // ✅ Check if user is logged in first
  if (!isLoggedIn()) {
    alert('Please sign in first to borrow books.');
    window.location.href = 'login.html';
    return;
  }

  const token = getToken();
  if (!token) {
    alert('Session expired. Please sign in again.');
    window.location.href = 'login.html';
    return;
  }

  // Show loading state
  const btn = event?.target?.closest('button');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Processing...';
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/borrow`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        book_id: bookId,
        format: format,
        user_id: getUser()?.id
      })
    });

    // ✅ Handle specific error cases
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(AUTH_USER_KEY);
      alert('Your session has expired. Please sign in again.');
      window.location.href = 'login.html';
      return;
    }

    if (response.status === 400) {
      const error = await response.json();
      alert(error.detail || 'You can only borrow one book at a time.');
      return;
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to borrow book');
    }

    const data = await response.json();
    alert(`✅ Successfully borrowed "${data.book_title || 'book'}"!`);
    
    // Refresh the page to update availability
    location.reload();

  } catch (error) {
    console.error('Borrow error:', error);
    alert(`❌ ${error.message || 'Failed to borrow book. Please try again.'}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Borrow';
    }
  }
}

// ── Alternative: Borrow with format selection ──────────────────

async function borrowWithFormat(bookId) {
  // Show format selection modal or use a default
  const format = prompt('Select format (HARDCOPY, PDF, AUDIO):', 'HARDCOPY');
  if (!format) return; // User cancelled
  
  await quickBorrow(bookId, format.toUpperCase());
}

// ── Debug function to check auth status ───────────────────────

function checkAuthStatus() {
  const token = getToken();
  const user = getUser();
  
  console.log('🔑 Token:', token ? 'Present' : 'Missing');
  console.log('👤 User:', user);
  console.log('✅ Logged in:', isLoggedIn());
  
  if (token) {
    // Verify token is valid
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiry = new Date(payload.exp * 1000);
      console.log('⏰ Token expires:', expiry);
      console.log('⏳ Token valid:', expiry > new Date());
    } catch (e) {
      console.error('Invalid token format:', e);
    }
  }
  
  return isLoggedIn();
}

// ── Auto-check auth on page load ──────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
  // Check auth status on page load
  checkAuthStatus();
  
  // Update UI based on auth status
  updateUIForAuth();
});

function updateUIForAuth() {
  const isLoggedIn = isLoggedIn();
  const borrowButtons = document.querySelectorAll('.borrow-btn');
  
  borrowButtons.forEach(btn => {
    if (!isLoggedIn) {
      btn.textContent = 'Sign in to Borrow';
      btn.style.opacity = '0.7';
      btn.title = 'Please sign in first';
    } else {
      btn.textContent = 'Borrow';
      btn.style.opacity = '1';
      btn.title = '';
    }
  });
}