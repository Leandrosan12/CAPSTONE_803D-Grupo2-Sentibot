document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("form-registro");
  const correo = document.getElementById("correo");
  const contrasena = document.getElementById("contrasena");
  const escuelaSelect = document.getElementById("escuela");
  const originalOptions = Array.from(escuelaSelect.options);

  function filterEscuelas(isDuoc) {
    escuelaSelect.innerHTML = '';
    if (isDuoc) {
      const colabOption = originalOptions.find(opt => opt.textContent.toLowerCase().includes('colaborador'));
      if (colabOption) {
        escuelaSelect.appendChild(colabOption.cloneNode(true));
      }
    } else {
      // Mostrar todas excepto Colaboradores
      originalOptions.forEach(opt => {
        if (!opt.textContent.toLowerCase().includes('colaborador')) {
          escuelaSelect.appendChild(opt.cloneNode(true));
        }
      });
    }
  }

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

  function setValid(el, message = "") {
    el.classList.remove("is-invalid");
    el.classList.add("is-valid");
    el.nextElementSibling.textContent = message;
  }

  // Validación correo (la misma del login)
  function validateEmail(value) {
    if (!value) return { ok: false, msg: "El correo es obligatorio." };
    const v = value.trim().toLowerCase();
    const gmailRegex = /@gmail\.com$/i;
    const duocRegex = /@(duocuc\.cl|duoc\.cl|profesor\.duoc\.cl)$/i;

    if (!gmailRegex.test(v) && !duocRegex.test(v)) {
      return { ok: false, msg: "Debe terminar en @gmail.com, @duocuc.cl, @duoc.cl o @profesor.duoc.cl." };
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
    const v = correo.value.trim().toLowerCase();
    const isDuoc = v.endsWith('@duoc.cl') || v.endsWith('@profesor.duoc.cl');
    if (r.ok) {
      setValid(correo, isDuoc ? "Estás usando un formato de correo permitido" : "");
    } else {
      setInvalid(correo, r.msg);
    }
    filterEscuelas(isDuoc);
  });

  // Initial check
  const initialV = correo.value.trim().toLowerCase();
  const initialIsDuoc = initialV.endsWith('@duoc.cl') || initialV.endsWith('@profesor.duoc.cl');
  filterEscuelas(initialIsDuoc);

  contrasena.addEventListener("input", () => {
    const r = validatePassword(contrasena.value);
    r.ok ? setValid(contrasena) : setInvalid(contrasena, r.msg);
  });

  // Validación al enviar
  form.addEventListener("submit", function (e) {
    const emailResult = validateEmail(correo.value);
    const v = correo.value.trim().toLowerCase();
    const isDuoc = v.endsWith('@duoc.cl') || v.endsWith('@profesor.duoc.cl');

    if (emailResult.ok) {
      setValid(correo, isDuoc ? "Estás usando un formato de correo permitido" : "");
    } else {
      setInvalid(correo, emailResult.msg);
    }
    const passResult = validatePassword(contrasena.value);

    passResult.ok ? setValid(contrasena) : setInvalid(contrasena, passResult.msg);

    if (!emailResult.ok || !passResult.ok) {
      e.preventDefault();
      e.stopPropagation();
    }
  });
});
