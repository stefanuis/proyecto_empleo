const COLORS = {
  success: "#2E7D32",
  error: "#D81B60",
  alerta: "#f97316",
};


function togglePw() {
  const clave = document.getElementById('clave');
  const icon = document.getElementById('eye-icon');
  if (clave.type === 'password') {
    clave.type = 'text';
    icon.innerHTML = `<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>`;
  } else {
    clave.type = 'password';
    icon.innerHTML = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
  }
}


function mostrarToast(mensaje, color) {
  const toast = document.createElement("div");
  toast.textContent = mensaje;

  Object.assign(toast.style, {
    position:       "fixed",
    bottom:         "30px",
    left:           "50%",
    transform:      "translateX(-50%)",
    backgroundColor: color,
    color:          "#fff",
    padding:        "12px 24px",
    borderRadius:   "8px",
    fontSize:       "14px",
    fontFamily:     "sans-serif",
    boxShadow:      "0 4px 12px rgba(0,0,0,0.2)",
    opacity:        "0",
    transition:     "opacity 0.3s ease",
    zIndex:         "9999",
    whiteSpace:     "nowrap",
  });

  document.body.appendChild(toast);

  // Fade in
  requestAnimationFrame(() => toast.style.opacity = "1");

  // Fade out y eliminar después de 3 segundos
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.addEventListener("transitionend", () => toast.remove());
  }, 3000);
}


async function handleSubmit(e) {

  e.preventDefault();

  const btn = e.target.querySelector('.btn-submit');
  const label = btn.querySelector('.btn-text');
  const chevron = btn.querySelector('.btn-chevron');

  const correo = document.getElementById("correo").value;
  const clave = document.getElementById("clave").value;

  btn.disabled = true;
  label.textContent = 'Verificando...';
  chevron.style.display = 'none';

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      credentials: 'include', // importante: envía y recibe cookies
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        correo: correo,
        clave: clave
      })
    });

    const data = await response.json();

    if (response.ok) {
      //console.log(data);
      label.textContent = '✓ Acceso concedido';
      btn.style.background = COLORS.success;

      setTimeout(() => {
        window.location.href = "/inicial";
      }, 1000);

    } else {
      //label.textContent = "Credenciales incorrectas";
      //alert(data.error);
      btn.disabled = false;
      chevron.style.display = '';
      mostrarToast(data.error || "Credenciales invalidas !!!", COLORS.error); 

      label.textContent = "Iniciar Sesión";
    }

  } catch (error) {
    label.textContent = "Error de conexión";
    btn.disabled = false;
    chevron.style.display = '';

  }
}
