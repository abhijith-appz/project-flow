/* ProjectFlow — Main JS */

// ── Dark mode ──────────────────────────────────────────────
function toggleTheme() {
  const body = document.body;
  const isDark = body.getAttribute('data-theme') === 'dark';
  const next = isDark ? '' : 'dark';
  body.setAttribute('data-theme', next);
  localStorage.setItem('pf-theme', next);
  const icon = document.getElementById('theme-icon');
  if (icon) icon.className = isDark ? 'fas fa-moon' : 'fas fa-sun';
}

(function applyStoredTheme() {
  const saved = localStorage.getItem('pf-theme');
  if (saved) {
    document.body.setAttribute('data-theme', saved);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.className = saved === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
})();

// ── Mobile sidebar ─────────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(e) {
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.getElementById('sidebar-toggle');
  if (sidebar && sidebar.classList.contains('open') &&
      !sidebar.contains(e.target) && (!toggle || !toggle.contains(e.target))) {
    sidebar.classList.remove('open');
  }
});

// ── Task checkbox (visual only, form handles actual update) ─
document.addEventListener('DOMContentLoaded', function() {

  // Animate progress fills
  document.querySelectorAll('.progress-fill, .progress-bar-fill').forEach(function(el) {
    const w = el.style.width;
    el.style.width = '0';
    setTimeout(function() { el.style.width = w; }, 200);
  });

  // Auto-dismiss toasts
  setTimeout(function() {
    document.querySelectorAll('.toast').forEach(function(t) {
      t.classList.remove('show');
    });
  }, 4500);

  // Tab switching (static tabs on pages like task list)
  document.querySelectorAll('.tab[data-target]').forEach(function(tab) {
    tab.addEventListener('click', function() {
      const targetId = this.getAttribute('data-target');
      document.querySelectorAll('.tab[data-target]').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Confirm delete forms
  document.querySelectorAll('form[data-confirm]').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      if (!confirm(this.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  // File upload area — show selected filename
  const fileInput = document.querySelector('input[type="file"]');
  const uploadArea = document.querySelector('.upload-area');
  if (fileInput && uploadArea) {
    uploadArea.addEventListener('dragover', function(e) {
      e.preventDefault();
      this.style.borderColor = 'var(--brand)';
      this.style.background  = 'rgba(37,99,235,0.06)';
    });
    uploadArea.addEventListener('dragleave', function() {
      this.style.borderColor = '';
      this.style.background  = '';
    });
    uploadArea.addEventListener('drop', function(e) {
      e.preventDefault();
      this.style.borderColor = '';
      this.style.background  = '';
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        updateUploadLabel(e.dataTransfer.files[0]);
      }
    });
    fileInput.addEventListener('change', function() {
      if (this.files[0]) updateUploadLabel(this.files[0]);
    });
  }

  function updateUploadLabel(file) {
    if (!uploadArea) return;
    const title = uploadArea.querySelector('.upload-title');
    const sub   = uploadArea.querySelector('.upload-sub');
    if (title) title.textContent = file.name;
    if (sub)   sub.textContent   = (file.size / 1024 / 1024).toFixed(1) + ' MB';
  }

  // Mark notification as read via AJAX
  document.querySelectorAll('[data-mark-read]').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const pk = this.getAttribute('data-mark-read');
      fetch('/notifications/' + pk + '/read/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
    });
  });
});

// ── CSRF cookie helper ──────────────────────────────────────
function getCookie(name) {
  let value = null;
  document.cookie.split(';').forEach(function(c) {
    c = c.trim();
    if (c.startsWith(name + '=')) value = decodeURIComponent(c.slice(name.length + 1));
  });
  return value;
}
