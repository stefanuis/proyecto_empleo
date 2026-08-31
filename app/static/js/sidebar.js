document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const overlay = document.getElementById('sidebarOverlay');

  function isMobile() {
    return window.innerWidth <= 768;
  }

  function openMobileSidebar() {
    sidebar.classList.add('mobile-open');
    overlay.classList.add('active');
  }

  function closeMobileSidebar() {
    sidebar.classList.remove('mobile-open');
    overlay.classList.remove('active');
  }

  toggleBtn.addEventListener('click', function () {
    if (isMobile()) {
      // En móvil: abre/cierra el sidebar como panel deslizante
      if (sidebar.classList.contains('mobile-open')) {
        closeMobileSidebar();
      } else {
        openMobileSidebar();
      }
    } else {
      // En escritorio: colapsa/expande (tu sistema actual)
      sidebar.classList.toggle('collapsed');
    }
  });

  // Cierra al tocar el fondo oscuro
  overlay.addEventListener('click', closeMobileSidebar);

  // Cierra el sidebar móvil automáticamente al elegir una opción del menú
  sidebar.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function () {
      if (isMobile()) closeMobileSidebar();
    });
  });

  // Si el usuario redimensiona la ventana, limpia el estado que no aplica
  window.addEventListener('resize', function () {
    if (isMobile()) {
      sidebar.classList.remove('collapsed'); // el collapsed es solo de escritorio
    } else {
      closeMobileSidebar(); // el mobile-open es solo de móvil
    }
  });
});