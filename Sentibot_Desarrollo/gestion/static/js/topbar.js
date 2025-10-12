document.addEventListener('DOMContentLoaded', () => {
  function adjustContentForTopbar() {
    const content = document.getElementById('content');
    const topbar = document.getElementById('topbar');

    if (window.innerWidth <= 768) { // móvil
      const height = topbar.offsetHeight;
      content.style.marginTop = height + 'px';
      content.classList.add('mobile-expanded');
    } else {
      content.style.marginTop = '2.6%'; // margen original
      content.classList.remove('mobile-expanded');
    }
  }

  // Ejecutar al cargar y al redimensionar
  window.addEventListener('load', adjustContentForTopbar);
  window.addEventListener('resize', adjustContentForTopbar);
});
