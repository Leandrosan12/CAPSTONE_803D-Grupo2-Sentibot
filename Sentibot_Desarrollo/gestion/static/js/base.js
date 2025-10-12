document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btn-toggle-sidebar');
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('content');
  const topbar = document.getElementById('topbar');

  // Función para abrir/cerrar sidebar en mobile
  function toggleSidebarMobile() {
    if (window.innerWidth < 1501) { // Mobile
      const isCollapsed = sidebar.classList.contains('collapsed');

      if (isCollapsed) {
        // Abrir sidebar al 50%
        sidebar.classList.remove('collapsed');
        sidebar.style.width = '50%';
        content.style.marginLeft = '50%';
        content.style.width = '50%';
        topbar.style.marginLeft = '50%';
        topbar.style.width = '50%';
      } else {
        // Cerrar sidebar
        sidebar.classList.add('collapsed');
        sidebar.style.width = '';
        content.style.marginLeft = '0';
        content.style.width = '100%';
        topbar.style.marginLeft = '0';
        topbar.style.width = '100%';
      }
    } else {
      // Desktop toggle normal
      sidebar.classList.toggle('collapsed');
      content.classList.toggle('expanded');
      topbar.classList.toggle('expanded');
    }
  }

  // Evento para botón hamburguesa
  btn.addEventListener('click', toggleSidebarMobile);

  // Evento para cerrar sidebar al hacer click en el contenido derecho (mobile)
  content.addEventListener('click', () => {
    if (window.innerWidth < 1501 && !sidebar.classList.contains('collapsed')) {
      toggleSidebarMobile();
    }
  });

  // Detectar tamaño de pantalla al cargar
  function handleResponsiveSidebar() {
    if (window.innerWidth < 1501) {
      sidebar.classList.add('collapsed');
      content.classList.add('expanded');
      topbar.classList.add('expanded');
    } else {
      sidebar.classList.remove('collapsed');
      content.classList.remove('expanded');
      topbar.classList.remove('expanded');
    }

    // Reset estilos inline
    sidebar.style.width = '';
    content.style.marginLeft = '';
    content.style.width = '';
    topbar.style.marginLeft = '';
    topbar.style.width = '';
  }

  // Ejecutar al cargar y al cambiar tamaño
  window.addEventListener('load', handleResponsiveSidebar);
  window.addEventListener('resize', handleResponsiveSidebar);
});
