// themes.js — Genre-based theme management

const THEME_STORAGE_KEY = 'bibliotheca:theme';

// Genre to theme mapping
const GENRE_THEME_MAP = {
  'Fiction': 'fiction',
  'Motivational': 'motivational',
  'Mystery': 'mystery',
  'Science': 'science',
  'Biography': 'biography',
  'Self-help': 'self-help',
  'Non-fiction': 'default'
};

const DEFAULT_THEME = 'default';
const DARK_THEME = 'dark';

const ThemeManager = {
  
  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || DEFAULT_THEME;
  },
  
  getPreference() {
    try {
      const data = JSON.parse(localStorage.getItem(THEME_STORAGE_KEY) || '{}');
      return data;
    } catch {
      return { autoTheme: true, theme: DEFAULT_THEME };
    }
  },
  
  savePreference(prefs) {
    localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(prefs));
  },
  
  applyTheme(themeName, smooth = true) {
    console.log('🎨 Applying theme:', themeName);
    
    if (!smooth) {
      document.documentElement.style.transition = 'none';
    }
    
    document.documentElement.setAttribute('data-theme', themeName);
    
    if (!smooth) {
      setTimeout(() => {
        document.documentElement.style.transition = '';
      }, 50);
    }
    
    this.updateToggleButton(themeName);
    this.updateToggleUI();
    
    // Dispatch event for any listeners
    document.dispatchEvent(new CustomEvent('theme-applied', { 
      detail: { theme: themeName } 
    }));
  },
  
  applyGenreTheme(genre) {
    console.log('🎨 Applying genre theme for:', genre);
    const prefs = this.getPreference();
    
    if (!prefs.autoTheme) {
      const theme = prefs.theme || DEFAULT_THEME;
      this.applyTheme(theme);
      return;
    }
    
    const themeName = GENRE_THEME_MAP[genre] || DEFAULT_THEME;
    this.applyTheme(themeName);
  },
  
  toggleAutoTheme() {
    const prefs = this.getPreference();
    prefs.autoTheme = !prefs.autoTheme;
    
    if (prefs.autoTheme) {
      const currentGenre = this.getCurrentGenre();
      this.applyGenreTheme(currentGenre);
    } else {
      const theme = prefs.theme || DEFAULT_THEME;
      this.applyTheme(theme);
    }
    
    this.savePreference(prefs);
    this.updateToggleUI();
    return prefs.autoTheme;
  },
  
  toggleDark() {
    const prefs = this.getPreference();
    const current = this.getCurrentTheme();
    
    if (current === DARK_THEME) {
      if (prefs.autoTheme) {
        const genre = this.getCurrentGenre();
        this.applyGenreTheme(genre);
      } else {
        this.applyTheme(DEFAULT_THEME);
      }
      prefs.theme = DEFAULT_THEME;
    } else {
      this.applyTheme(DARK_THEME);
      prefs.theme = DARK_THEME;
    }
    
    this.savePreference(prefs);
    this.updateToggleUI();
  },
  
  getCurrentGenre() {
    if (window.location.pathname.includes('reader.html')) {
      const bookData = sessionStorage.getItem('current_book');
      if (bookData) {
        try {
          const book = JSON.parse(bookData);
          return book.genre;
        } catch {}
      }
    }
    const genreEl = document.querySelector('[data-genre]');
    if (genreEl) {
      return genreEl.dataset.genre;
    }
    const genreText = document.querySelector('.detail-genre');
    if (genreText) {
      return genreText.textContent.trim();
    }
    return null;
  },
  
  updateToggleButton(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    
    const isDark = theme === DARK_THEME;
    const icon = isDark ? '🌙' : '☀️';
    const label = isDark ? 'Dark' : 'Light';
    
    btn.innerHTML = `${icon} ${label}`;
  },
  
  updateToggleUI() {
    const prefs = this.getPreference();
    const autoToggle = document.getElementById('auto-theme-toggle');
    
    if (autoToggle) {
      autoToggle.checked = prefs.autoTheme;
    }
    
    const status = document.getElementById('theme-status');
    if (status) {
      const currentTheme = this.getCurrentTheme();
      const isAuto = prefs.autoTheme;
      const themeName = currentTheme.charAt(0).toUpperCase() + currentTheme.slice(1);
      status.textContent = isAuto ? `🎨 Auto: ${themeName}` : `🔒 Manual: ${themeName}`;
    }
  },
  
  init() {
    console.log('🎨 Theme Manager initializing...');
    const prefs = this.getPreference();
    
    if (prefs.autoTheme) {
      const genre = this.getCurrentGenre();
      this.applyGenreTheme(genre);
    } else {
      const theme = prefs.theme || DEFAULT_THEME;
      this.applyTheme(theme);
    }
    
    this.updateToggleUI();
    
    // Listen for theme toggle events
    document.addEventListener('theme-change', (e) => {
      if (e.detail && e.detail.theme) {
        this.applyTheme(e.detail.theme);
      }
    });
    
    console.log('🎨 Theme Manager initialized');
  }
};

// ─── Generate theme toggle HTML ───
function getThemeToggleHTML() {
  return `
    <div class="theme-controls">
      <button id="theme-toggle-btn" class="theme-toggle-btn" onclick="window.toggleTheme()">
        ☀️ Light
      </button>
      <label style="display:flex;align-items:center;gap:6px;font-family:var(--font-ui);font-size:0.78rem;color:var(--text-secondary);cursor:pointer;">
        <input type="checkbox" id="auto-theme-toggle" onchange="window.toggleAutoTheme()">
        Auto
      </label>
      <span id="theme-status" style="font-family:var(--font-ui);font-size:0.72rem;color:var(--text-muted);"></span>
    </div>
  `;
}

// ─── Global toggle functions ───
window.toggleTheme = function() {
  console.log('🔄 Toggle theme clicked');
  if (typeof ThemeManager !== 'undefined') {
    ThemeManager.toggleDark();
  } else {
    console.error('ThemeManager not available');
  }
};

window.toggleAutoTheme = function() {
  console.log('🔄 Toggle auto theme clicked');
  if (typeof ThemeManager !== 'undefined') {
    ThemeManager.toggleAutoTheme();
  } else {
    console.error('ThemeManager not available');
  }
};

// ─── Notify genre change ───
function notifyGenreChange(genre) {
  console.log('📚 Genre changed to:', genre);
  const event = new CustomEvent('genre-change', { detail: { genre } });
  document.dispatchEvent(event);
  if (typeof ThemeManager !== 'undefined' && ThemeManager) {
    ThemeManager.applyGenreTheme(genre);
  }
}

// ─── Initialize ───
document.addEventListener('DOMContentLoaded', () => {
  console.log('🎨 DOM ready - initializing ThemeManager');
  if (typeof ThemeManager !== 'undefined' && ThemeManager) {
    ThemeManager.init();
  } else {
    console.error('ThemeManager not available on DOM ready');
  }
});

// Listen for genre changes
document.addEventListener('genre-change', (e) => {
  if (typeof ThemeManager !== 'undefined' && ThemeManager) {
    ThemeManager.applyGenreTheme(e.detail.genre);
  }
});

// Make globally available
window.ThemeManager = ThemeManager;
window.getThemeToggleHTML = getThemeToggleHTML;
window.notifyGenreChange = notifyGenreChange;