// auth.js — handles all authentication logic for Bibliotheca.

const AUTH_TOKEN_KEY = "bibliotheca:token";
const AUTH_USER_KEY = "bibliotheca:user";

// API_BASE_URL is already defined in api.js
// Make sure api.js is loaded BEFORE auth.js

const AuthAPI = {

  getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  getUser() {
    try {
      const raw = localStorage.getItem(AUTH_USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  saveSession(token, user) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
  },

  requireAuth(redirectTo = "login.html") {
    if (!this.isLoggedIn()) {
      window.location.href = redirectTo;
      return false;
    }
    return true;
  },

  requireGuest(redirectTo = "index.html") {
    if (this.isLoggedIn()) {
      window.location.href = redirectTo;
      return false;
    }
    return true;
  },

  logout() {
    this.clearSession();
    window.location.href = "login.html";
  },

  async register({ username, email, password, address, avatar_url, is_private }) {
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password, address, avatar_url, is_private }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Registration failed");
    }
    return data;
  },

  async loginAndFetch({ username, password }) {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);

    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      body: form,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Login failed");
    }

    const meRes = await fetch(`${API_BASE_URL}/api/users/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    
    if (!meRes.ok) {
      throw new Error("Failed to fetch user profile");
    }
    
    const user = await meRes.json();
    return { token: data.access_token, user };
  },

  async login({ username, password }) {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);

    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      body: form,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Login failed");
    }
    return data;
  },

  async fetchMe() {
    const token = this.getToken();
    if (!token) return null;

    const res = await fetch(`${API_BASE_URL}/api/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    return res.json();
  },
};

// ── Update navigation based on auth state ────────────────────

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function isUserAdmin() {
  const user = AuthAPI.getUser();
  return user && user.role === "admin";
}

function updateNavForAuth() {
  const nav = document.querySelector(".site-nav");
  if (!nav) return;

  // Remove previous auth items
  nav.querySelectorAll(".auth-nav-item").forEach(el => el.remove());

  const user = AuthAPI.getUser();

  // Inventory link
  const inventory = document.getElementById("inventoryNavLink");
  if (inventory) {
    inventory.style.display = isUserAdmin() ? "" : "none";
  }

  if (user) {
    nav.insertAdjacentHTML(
      "beforeend",
      `
      <span class="auth-nav-item">
        👤 ${escapeHTML(user.username)}
      </span>

      <button
        class="auth-nav-item btn btn-ghost"
        onclick="AuthAPI.logout()">
        Sign out
      </button>
      `
    );

    if (isUserAdmin()) {
      document.body.classList.add("admin-logged-in");
    } else {
      document.body.classList.remove("admin-logged-in");
    }

  } else {

    nav.insertAdjacentHTML(
      "beforeend",
      `
      <a href="login.html" class="auth-nav-item">
        Sign in
      </a>

      <a href="register.html"
         class="auth-nav-item btn btn-amber">
         Join free
      </a>
      `
    );

    document.body.classList.remove("admin-logged-in");
  }
}

// Add this function to auth.js
function logoutUser() {
  AuthAPI.clearSession();
  document.body.classList.remove('admin-logged-in');
  window.location.href = 'index.html';
}

// Make it global
window.logoutUser = logoutUser;

document.addEventListener("DOMContentLoaded", updateNavForAuth);

window.updateNavForAuth = updateNavForAuth;
window.isUserAdmin = isUserAdmin;