// static/js/login.js
document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  const email = document.getElementById('correo_login');
  const password = document.getElementById('contrasena_login');

  // Crear feedback si no existe
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

  function setValid(el, message = "") {
    el.classList.remove('is-invalid');
    el.classList.add('is-valid');
    if (el.nextElementSibling) el.nextElementSibling.textContent = message;
  }

  // Validación de email
  function validateEmail(value) {
    if (!value) return { ok: false, msg: 'El correo es obligatorio.' };
    const v = value.trim().toLowerCase();
    const gmailRegex = /@gmail\.com$/i;
    const duocRegex = /@(duocuc\.cl|duoc\.cl|profesor\.duoc\.cl)$/i;
    if (!gmailRegex.test(v) && !duocRegex.test(v)) {
      return { ok: false, msg: 'El correo debe terminar en @gmail.com, @duocuc.cl, @duoc.cl o @profesor.duoc.cl.' };
    }
    const basicEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!basicEmail.test(v)) return { ok: false, msg: 'Formato de correo inválido.' };
    return { ok: true, msg: '' };
  }

  // Validación de contraseña
  function validatePassword(value) {
    if (!value) return { ok: false, msg: 'La contraseña es obligatoria.' };
    if (value.length < 8) return { ok: false, msg: 'Debe tener al menos 8 caracteres.' };
    return { ok: true, msg: '' };
  }

  // Validación en tiempo real
  email.addEventListener('input', () => {
    const r = validateEmail(email.value);
    const v = email.value.trim().toLowerCase();
    const isDuoc = v.endsWith('@duoc.cl') || v.endsWith('@profesor.duoc.cl');
    if (r.ok) {
      setValid(email, isDuoc ? "Estás usando un formato de correo permitido" : "");
    } else {
      setInvalid(email, r.msg);
    }
  });

  password.addEventListener('input', () => {
    const r = validatePassword(password.value);
    r.ok ? setValid(password) : setInvalid(password, r.msg);
  });

  // Validación al enviar
  form.addEventListener('submit', function (e) {
    const emailResult = validateEmail(email.value);
    const v = email.value.trim().toLowerCase();
    const isDuoc = v.endsWith('@duoc.cl') || v.endsWith('@profesor.duoc.cl');

    if (emailResult.ok) {
      setValid(email, isDuoc ? "Estás usando un formato de correo permitido" : "");
    } else {
      setInvalid(email, emailResult.msg);
    }
    const passResult = validatePassword(password.value);

    passResult.ok ? setValid(password) : setInvalid(password, passResult.msg);

    if (!emailResult.ok || !passResult.ok) {
      e.preventDefault();
      e.stopPropagation();
    }
  });
});
