// auth.js — Login logic
const API = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
  // If already logged in, go to profile
  if (localStorage.getItem('token')) {
    window.location.href = 'profile.html';
    return;
  }

  const form = document.getElementById('login-form');
  const errorEl = document.getElementById('login-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Ingresando...';
    hideAlert(errorEl);

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    try {
      const res = await fetch(`${API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Error de servidor');

      localStorage.setItem('token', data.token);
      window.location.href = 'profile.html';
    } catch (err) {
      showAlert(errorEl, err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Iniciar sesión';
    }
  });
});

function showAlert(el, msg, type) {
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
}
function hideAlert(el) {
  el.className = 'alert';
}
