document.addEventListener('DOMContentLoaded', function() {
  const editBtn = document.getElementById('editProfileBtn');
  const listItems = document.querySelectorAll('.list-group-item');
  let editing = false;

  editBtn.addEventListener('click', function() {
    if (!editing) {
      // Cambiar a modo edición
      listItems.forEach(item => {
        const valueSpan = item.querySelector('span:last-child');
        const key = valueSpan.textContent.trim();
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control form-control-sm';
        input.value = key;
        input.style.maxWidth = '65%';
        valueSpan.replaceWith(input);
      });
      editBtn.textContent = 'Guardar';
      editBtn.classList.replace('btn-success', 'btn-primary');
      editing = true;
    } else {
      // Guardar cambios
      const updatedData = {};
      listItems.forEach(item => {
        const label = item.querySelector('span:first-child').textContent.replace(':', '').trim();
        const input = item.querySelector('input');
        const newValue = input.value.trim();
        updatedData[label] = newValue;

        const span = document.createElement('span');
        span.textContent = newValue;
        input.replaceWith(span);
      });

      console.log('Datos actualizados:', updatedData);

      // Ejemplo de envío a Django (requiere vista configurada)
      /*
      fetch("{% url 'actualizar_perfil' %}", {
        method: "POST",
        headers: {
          "X-CSRFToken": "{{ csrf_token }}",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(updatedData)
      })
      .then(res => res.json())
      .then(data => console.log('Perfil actualizado:', data));
      */

      editBtn.textContent = 'Editar';
      editBtn.classList.replace('btn-primary', 'btn-success');
      editing = false;
    }
  });
});