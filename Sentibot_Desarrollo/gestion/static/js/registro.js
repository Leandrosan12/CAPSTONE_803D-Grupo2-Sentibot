document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("form-registro");
  const correo = document.getElementById("correo");
  const contrasena = document.getElementById("contrasena");

  // Crear feedback si no existe
  function ensureFeedback(el) {
    if (!el.nextElementSibling || !el.nextElementSibling.classList.contains("invalid-feedback")) {
      const fb = document.createElement("div");
      fb.className = "invalid-feedback";
      el.after(fb);
    }
  }
  ensureFeedback(correo);
  ensureFeedback(contrasena);

  function setInvalid(el, message) {
    el.classList.add("is-invalid");
    el.classList.remove("is-valid");
    el.nextElementSibling.textContent = message;
  }

  function setValid(el) {
    el.classList.remove("is-invalid");
    el.classList.add("is-valid");
    if (el.nextElementSibling) el.nextElementSibling.textContent = "";
  }

  // Validación correo (la misma del login)
  function validateEmail(value) {
    if (!value) return { ok: false, msg: "El correo es obligatorio." };
    const v = value.trim().toLowerCase();
    const gmailRegex = /@gmail\.com$/i;
    const duocRegex = /@duocuc\.cl$/i;

    if (!gmailRegex.test(v) && !duocRegex.test(v)) {
      return { ok: false, msg: "Debe terminar en @gmail.com o @duocuc.cl." };
    }
    const basicEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!basicEmail.test(v)) return { ok: false, msg: "Formato inválido." };

    return { ok: true, msg: "" };
  }

  // Validación contraseña (exactamente igual que login)
  function validatePassword(value) {
    if (!value) return { ok: false, msg: "La contraseña es obligatoria." };
    if (value.length < 8) return { ok: false, msg: "Debe tener al menos 8 caracteres." };
    return { ok: true, msg: "" };
  }

  // Validación en vivo
  correo.addEventListener("input", () => {
    const r = validateEmail(correo.value);
    r.ok ? setValid(correo) : setInvalid(correo, r.msg);
  });

  contrasena.addEventListener("input", () => {
    const r = validatePassword(contrasena.value);
    r.ok ? setValid(contrasena) : setInvalid(contrasena, r.msg);
  });

  // Validación al enviar
  form.addEventListener("submit", function (e) {
    const emailResult = validateEmail(correo.value);
    const passResult = validatePassword(contrasena.value);

    emailResult.ok ? setValid(correo) : setInvalid(correo, emailResult.msg);
    passResult.ok ? setValid(contrasena) : setInvalid(contrasena, passResult.msg);

    if (!emailResult.ok || !passResult.ok) {
      e.preventDefault();
      e.stopPropagation();
    }
  });
});
