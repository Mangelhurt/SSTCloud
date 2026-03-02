// profile.js — Profile page logic
const API = 'http://localhost:5000/api';

let currentUser = null;

// ── Auth helpers ────────────────────────────────────────────────────────────
function token() { return localStorage.getItem('token'); }

async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: {
      'Authorization': `Bearer ${token()}`,
      ...(opts.headers || {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) { logout(); return null; }
  return { ok: res.ok, data };
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
}

// ── Navigation ───────────────────────────────────────────────────────────────
function navigate(sectionId) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.sidebar-item').forEach(b => b.classList.remove('active'));
  document.getElementById(sectionId).classList.add('active');
  document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
}

// ── Alert helpers ────────────────────────────────────────────────────────────
function showAlert(id, msg, type = 'error') {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
  setTimeout(() => el.className = 'alert', 4000);
}

// ── Render user ───────────────────────────────────────────────────────────────
function renderUser(user) {
  currentUser = user;

  // Sidebar avatar area
  document.getElementById('profile-name').textContent = user.name;
  document.getElementById('profile-email').textContent = user.email;
  renderAvatar(user);

  // Info form
  document.getElementById('f-name').value = user.name;
  document.getElementById('f-bio').value = user.bio || '';
  document.getElementById('f-phone').value = user.phone || '';
  document.getElementById('f-location').value = user.location || '';
  document.getElementById('f-email').value = user.email;
}

function renderAvatar(user) {
  const wrap = document.getElementById('avatar-display');
  if (user.avatar) {
    wrap.innerHTML = `<img class="avatar-img" src="${API}/profile/avatar/${user.avatar}" alt="Avatar" id="avatar-img">`;
  } else {
    const initial = (user.name || 'U')[0].toUpperCase();
    wrap.innerHTML = `<div class="avatar-placeholder" id="avatar-placeholder">${initial}</div>`;
  }
  // Show/hide delete button
  const delBtn = document.getElementById('btn-delete-avatar');
  delBtn.style.display = user.avatar ? 'inline-flex' : 'none';
}

// ── Load profile ─────────────────────────────────────────────────────────────
async function loadProfile() {
  const result = await apiFetch('/profile');
  if (!result) return;
  if (result.ok) renderUser(result.data);
}

// ── Update basic info ─────────────────────────────────────────────────────────
async function saveInfo(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-save-info');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  const payload = {
    name: document.getElementById('f-name').value.trim(),
    bio: document.getElementById('f-bio').value.trim(),
    phone: document.getElementById('f-phone').value.trim(),
    location: document.getElementById('f-location').value.trim(),
  };

  const result = await apiFetch('/profile', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  btn.disabled = false;
  btn.textContent = 'Guardar cambios';

  if (!result) return;
  if (result.ok) {
    renderUser(result.data);
    showAlert('info-alert', 'Perfil actualizado correctamente', 'success');
  } else {
    showAlert('info-alert', result.data.error || 'Error al guardar', 'error');
  }
}

// ── Change password ───────────────────────────────────────────────────────────
async function changePassword(e) {
  e.preventDefault();
  const newPwd = document.getElementById('f-new-password').value;
  const confirmPwd = document.getElementById('f-confirm-password').value;

  if (newPwd !== confirmPwd) {
    showAlert('pwd-alert', 'Las contraseñas no coinciden', 'error');
    return;
  }

  const btn = document.getElementById('btn-change-pwd');
  btn.disabled = true;
  btn.textContent = 'Actualizando...';

  const result = await apiFetch('/auth/change-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      current_password: document.getElementById('f-current-password').value,
      new_password: newPwd,
    }),
  });

  btn.disabled = false;
  btn.textContent = 'Cambiar contraseña';

  if (!result) return;
  if (result.ok) {
    document.getElementById('pwd-form').reset();
    showAlert('pwd-alert', 'Contraseña actualizada correctamente', 'success');
  } else {
    showAlert('pwd-alert', result.data.error || 'Error al cambiar la contraseña', 'error');
  }
}

// ── Avatar upload ─────────────────────────────────────────────────────────────
async function uploadAvatar(file) {
  if (!file) return;

  const allowedTypes = ['image/png', 'image/jpeg', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    showAlert('avatar-alert', 'Formato no permitido. Usa PNG, JPG o WEBP', 'error');
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    showAlert('avatar-alert', 'El archivo no puede superar 5 MB', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('avatar', file);

  const btn = document.getElementById('btn-upload-avatar');
  btn.disabled = true;
  btn.textContent = 'Subiendo...';

  const result = await apiFetch('/profile/avatar', { method: 'POST', body: formData });
  btn.disabled = false;
  btn.textContent = 'Subir foto';

  if (!result) return;
  if (result.ok) {
    renderUser(result.data);
    showAlert('avatar-alert', 'Foto actualizada correctamente', 'success');
  } else {
    showAlert('avatar-alert', result.data.error || 'Error al subir la foto', 'error');
  }
}

// ── Avatar delete ─────────────────────────────────────────────────────────────
async function deleteAvatar() {
  if (!confirm('¿Seguro que deseas eliminar tu foto de perfil?')) return;

  const result = await apiFetch('/profile/avatar', { method: 'DELETE' });
  if (!result) return;
  if (result.ok) {
    renderUser(result.data);
    showAlert('avatar-alert', 'Foto eliminada', 'success');
  } else {
    showAlert('avatar-alert', result.data.error || 'Error al eliminar', 'error');
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (!token()) { window.location.href = 'index.html'; return; }

  loadProfile();

  // Sidebar navigation
  document.querySelectorAll('.sidebar-item[data-section]').forEach(btn => {
    btn.addEventListener('click', () => navigate(btn.dataset.section));
  });

  // Logout
  document.getElementById('btn-logout').addEventListener('click', logout);

  // Info form
  document.getElementById('info-form').addEventListener('submit', saveInfo);

  // Password form
  document.getElementById('pwd-form').addEventListener('submit', changePassword);

  // Avatar file input
  document.getElementById('avatar-input').addEventListener('change', e => {
    uploadAvatar(e.target.files[0]);
    e.target.value = '';
  });

  // Upload button triggers file input
  document.getElementById('btn-upload-avatar').addEventListener('click', () => {
    document.getElementById('avatar-input').click();
  });

  // Delete avatar
  document.getElementById('btn-delete-avatar').addEventListener('click', deleteAvatar);
});
