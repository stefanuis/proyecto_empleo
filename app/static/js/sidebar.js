// Menú lateral: en móvil se abre/cierra con la hamburguesa del navbar
// (con fondo oscuro detrás); en escritorio la hamburguesa colapsa el menú.
document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const overlay = document.getElementById('sidebarOverlay');

  if (!sidebar || !toggleBtn) {
    return;
  }

  function isMobile() {
    return window.innerWidth <= 768;
  }

  function openMobileSidebar() {
    sidebar.classList.add('mobile-open');
    if (overlay) overlay.classList.add('active');
    toggleBtn.setAttribute('aria-expanded', 'true');
    toggleBtn.setAttribute('aria-label', 'Cerrar menú');
  }

  function closeMobileSidebar() {
    sidebar.classList.remove('mobile-open');
    if (overlay) overlay.classList.remove('active');
    toggleBtn.setAttribute('aria-expanded', 'false');
    toggleBtn.setAttribute('aria-label', 'Abrir menú');
  }

  toggleBtn.setAttribute('aria-expanded', 'false');

  toggleBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    if (isMobile()) {
      if (sidebar.classList.contains('mobile-open')) {
        closeMobileSidebar();
      } else {
        openMobileSidebar();
      }
    } else {
      sidebar.classList.toggle('collapsed');
    }
  });

  // Cierra al tocar el fondo oscuro
  if (overlay) {
    overlay.addEventListener('click', closeMobileSidebar);
  }

  // Cierra con la tecla Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
      closeMobileSidebar();
      toggleBtn.focus();
    }
  });

  // Cierra el sidebar móvil automáticamente al elegir una opción del menú
  sidebar.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      if (isMobile()) closeMobileSidebar();
    });
  });

  // Si se redimensiona la ventana, limpia el estado que no aplica
  window.addEventListener('resize', function () {
    if (isMobile()) {
      sidebar.classList.remove('collapsed'); // el collapsed es solo de escritorio
    } else {
      closeMobileSidebar(); // el mobile-open es solo de móvil
    }
  });
});
