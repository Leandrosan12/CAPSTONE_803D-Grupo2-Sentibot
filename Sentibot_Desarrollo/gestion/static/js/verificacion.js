// verificacion.js (versión robusta con debug)
// Guarda este archivo como static/js/verificacion.js y enlázalo en tu template
(function () {
  'use strict';

  // --- Helper CSRF / DOM ---
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function qs(id) { return document.getElementById(id); }
  function showMessage(el, text, kind) {
    if (!el) return;
    el.classList.remove('text-success', 'text-danger', 'text-muted');
    if (kind === 'success') el.classList.add('text-success');
    if (kind === 'danger') el.classList.add('text-danger');
    if (kind === 'muted') el.classList.add('text-muted');
    el.innerText = text;
  }

  // Ejecutar solo cuando el DOM esté listo
  document.addEventListener('DOMContentLoaded', function () {
    console.log('verificacion.js: DOMContentLoaded');

    // Elementos esperados
    const btnVerificar = qs('btn-verificar');
    const btnConfirmar = qs('btn-confirmar');
    const btnRegistrar = qs('btn-registrar');
    const inputCorreo = qs('correo');
    const inputCodigo = qs('codigo');
    const campoCodigo = qs('campo-codigo');
    const wrapConfirmar = qs('wrap-confirmar');
    const mensaje = qs('mensaje-verificacion');

    // Mostrar advertencia si elementos no encontrados
    if (!btnVerificar) console.warn('verificacion.js: btn-verificar NO ENCONTRADO');
    if (!btnConfirmar) console.warn('verificacion.js: btn-confirmar NO ENCONTRADO');
    if (!btnRegistrar) console.warn('verificacion.js: btn-registrar NO ENCONTRADO');
    if (!inputCorreo) console.warn('verificacion.js: input correo NO ENCONTRADO (id="correo")');
    if (!inputCodigo) console.warn('verificacion.js: input codigo NO ENCONTRADO (id="codigo")');
    if (!mensaje) console.warn('verificacion.js: mensaje-verificacion NO ENCONTRADO (id="mensaje-verificacion")');

    const csrftoken = getCookie('csrftoken');
    console.log('verificacion.js: csrftoken presente?', !!csrftoken);

    // Si hay errores JS previos que rompan la ejecución, verlos en consola
    try {
      // Si btnVerificar existe, añadir listener
      if (btnVerificar) {
        btnVerificar.addEventListener('click', function (e) {
          e.preventDefault();
          console.log('btn-verificar click');
          enviarCodigo();
        });
      }

      // Si btnConfirmar existe, añadir listener
      if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function (e) {
          e.preventDefault();
          console.log('btn-confirmar click');
          validarCodigo();
        });
      }

      // Si el formulario está enviando y quieres prevenir double submit, puedes observar el submit
      // opcional: habilitar el botón registrar si fue deshabilitado por accidente
      if (btnRegistrar) {
        // Si por alguna razón está deshabilitado, lo dejamos en su estado actual pero lo loggeamos
        console.log('btn-registrar disabled?', btnRegistrar.disabled);
      }

      // Listeners para inputs: si cambian, resetear estado de verificación
      if (inputCorreo) {
        inputCorreo.addEventListener('input', function () {
          console.log('input correo cambiado - reset verificaciones');
          if (btnRegistrar) btnRegistrar.disabled = true;
          if (wrapConfirmar) wrapConfirmar.style.display = 'none';
          if (campoCodigo) campoCodigo.style.display = 'none';
          if (mensaje) mensaje.innerText = '';
          if (btnConfirmar) {
            btnConfirmar.disabled = false;
            btnConfirmar.innerText = 'Confirmar — Todo en orden';
          }
        });
      }

      if (inputCodigo) {
        inputCodigo.addEventListener('input', function () {
          console.log('input codigo modificado - deshabilitando registrar');
          if (btnRegistrar) btnRegistrar.disabled = true;
          if (btnConfirmar) {
            btnConfirmar.disabled = false;
            btnConfirmar.innerText = 'Confirmar — Todo en orden';
          }
        });
      }

    } catch (err) {
      console.error('verificacion.js: error al adjuntar listeners', err);
      if (mensaje) showMessage(mensaje, 'Error interno en la página. Revisa la consola.', 'danger');
    }

    // --- Implementaciones de funciones ---
    async function enviarCodigo() {
      if (!inputCorreo) return console.error('enviarCodigo: inputCorreo no existe');
      const correo = inputCorreo.value.trim();
      if (!correo) {
        showMessage(mensaje, 'Por favor, ingresa un correo válido.', 'danger');
        return;
      }
      showMessage(mensaje, 'Enviando código...', 'muted');

      try {
        const url = `/enviar-codigo/?correo=${encodeURIComponent(correo)}`;
        const resp = await fetch(url, {
          method: 'GET',
          credentials: 'same-origin'
        });
        console.log('enviar-codigo status', resp.status);

        const text = await resp.text();
        let data;
        try { data = JSON.parse(text); } catch (e) { data = null; }

        if (!resp.ok) {
          console.error('enviar-codigo no ok, raw:', text);
          showMessage(mensaje, data && data.error ? data.error : 'Error al enviar código', 'danger');
          return;
        }

        if (data && data.mensaje) {
          showMessage(mensaje, data.mensaje, 'success');
          if (campoCodigo) campoCodigo.style.display = 'block';
          if (wrapConfirmar) wrapConfirmar.style.display = 'block';
          if (inputCodigo) inputCodigo.focus();
          if (inputCorreo) inputCorreo.readOnly = true;
          console.log('enviar-codigo OK - sesión debería contener el código');
        } else {
          showMessage(mensaje, 'Respuesta inesperada del servidor', 'danger');
          console.log('enviar-codigo data:', data, 'text:', text);
        }
      } catch (err) {
        console.error('enviar-codigo fetch error', err);
        showMessage(mensaje, 'Error al enviar el código. Inténtalo de nuevo.', 'danger');
      }
    }

    async function validarCodigo() {
      if (!inputCodigo || !inputCorreo) return console.error('validarCodigo: faltan inputs');
      const correo = inputCorreo.value.trim();
      const codigo = inputCodigo.value.trim();
      if (!codigo) {
        showMessage(mensaje, 'Ingresa el código que recibiste antes de confirmar.', 'danger');
        return;
      }
      showMessage(mensaje, 'Validando código...', 'muted');

      try {
        const resp = await fetch('/validar-codigo/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ correo: correo, codigo: codigo })
        });

        console.log('validar-codigo status', resp.status);
        const text = await resp.text();
        console.log('validar-codigo raw response:', text);
        let data;
        try { data = JSON.parse(text); } catch (e) { data = null; }

        if (!resp.ok) {
          const errMsg = data && data.error ? data.error : `Error servidor (${resp.status})`;
          showMessage(mensaje, errMsg, 'danger');
          console.warn('validar-codigo no ok, parsed data:', data);
          return;
        }

        if (data && data.ok) {
          if (btnRegistrar) btnRegistrar.disabled = false;
          showMessage(mensaje, 'Código válido. Todo en orden — ya puedes registrar.', 'success');
          if (btnConfirmar) {
            btnConfirmar.innerText = 'Todo en orden ✓';
            btnConfirmar.disabled = true;
          }
        } else {
          const err = data && data.error ? data.error : 'Código inválido.';
          showMessage(mensaje, err, 'danger');
          console.log('validar-codigo data no ok:', data);
        }
      } catch (err) {
        console.error('validar-codigo fetch error', err);
        showMessage(mensaje, 'Error validando el código. Inténtalo más tarde.', 'danger');
      }
    }

    // Exponer funciones al window para pruebas manuales desde consola (opcional)
    window.__verificacion_debug = {
      enviarCodigo,
      validarCodigo
    };

  }); // DOMContentLoaded end
})();
