// static/js/login.js
document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  const email = document.getElementById('correo_login');
  const password = document.getElementById('contrasena_login');

  // Asegura que existan los mensajes de error de Bootstrap
  function ensureFeedback(el) {
    if (!el.nextElementSibling || !el.nextElementSibling.classList.contains('invalid-feedback')) {
      const fb = document.createElement('div');
      fb.className = 'invalid-feedback';
      el.after(fb);
    }
  }
  ensureFeedback(email);
  ensureFeedback(password);

  function setInvalid(el, message) {
    el.classList.add('is-invalid');
    el.classList.remove('is-valid');
    el.nextElementSibling.textContent = message;
  }

  function setValid(el) {
    el.classList.remove('is-invalid');
    el.classList.add('is-valid');
    if (el.nextElementSibling) el.nextElementSibling.textContent = '';
  }

  // ✅ Validación de email (acepta @gmail.com y @duocuc.cl)
  function validateEmail(value) {
    if (!value) return { ok: false, msg: 'El correo es obligatorio.' };
    const v = value.trim().toLowerCase();

    // formatos aceptados
    const gmailRegex = /@gmail\.com$/i;
    const duocRegex = /@duocuc\.cl$/i;

    if (!gmailRegex.test(v) && !duocRegex.test(v)) {
      return { ok: false, msg: 'El correo debe terminar en @gmail.com o @duocuc.cl.' };
    }

    // validación básica general de email
    const basicEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!basicEmail.test(v)) return { ok: false, msg: 'Formato de correo inválido.' };

    return { ok: true, msg: '' };
  }

  // ✅ Validación de contraseña
  function validatePassword(value) {
    if (!value) return { ok: false, msg: 'La contraseña es obligatoria.' };
    if (value.length < 8) return { ok: false, msg: 'Debe tener al menos 8 caracteres.' };
    return { ok: true, msg: '' };
  }

  // Validación en tiempo real
  email.addEventListener('input', () => {
    const r = validateEmail(email.value);
    r.ok ? setValid(email) : setInvalid(email, r.msg);
  });

  password.addEventListener('input', () => {
    const r = validatePassword(password.value);
    r.ok ? setValid(password) : setInvalid(password, r.msg);
  });

  // Validar al enviar
  form.addEventListener('submit', function (e) {
    const emailResult = validateEmail(email.value);
    const passResult = validatePassword(password.value);

    if (!emailResult.ok) setInvalid(email, emailResult.msg); else setValid(email);
    if (!passResult.ok) setInvalid(password, passResult.msg); else setValid(password);

    if (!emailResult.ok || !passResult.ok) {
      e.preventDefault();
      e.stopPropagation();
    }
  });
});
