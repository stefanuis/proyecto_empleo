// Cierre de sesión por inactividad (complementa el control del servidor).
//
// - Avisa poco antes de cerrar y permite seguir conectado.
// - Si se cumple el tiempo, va a /cerrar-sesion: no quedan datos a la vista
//   en un equipo desatendido.
// - Mientras la persona trabaja sin cambiar de página (p. ej. llenando un
//   formulario largo) avisa al servidor para que no le cierre la sesión.
// - La actividad se comparte entre pestañas con localStorage.
(function () {
    const script = document.currentScript;
    if (!script) {
        return;
    }

    const minutos = Number(script.dataset.minutos) || 30;
    const urlMantener = script.dataset.mantener;
    const urlSalir = script.dataset.salir;

    const LIMITE = minutos * 60 * 1000;
    const AVISO_ANTES = Math.min(2 * 60 * 1000, LIMITE / 2);
    const CADA_CUANTO_AVISAR_SERVIDOR = Math.min(5 * 60 * 1000, LIMITE / 3);
    const CLAVE = "sesion_ultima_actividad";

    let ultimoAvisoServidor = Date.now();
    let aviso = null;

    function leerActividad() {
        try {
            return Number(localStorage.getItem(CLAVE)) || 0;
        } catch (e) {
            return 0;
        }
    }

    function guardarActividad(momento) {
        try {
            localStorage.setItem(CLAVE, String(momento));
        } catch (e) {
            // Sin localStorage cada pestaña lleva su propia cuenta
        }
        ultimaActividadLocal = momento;
    }

    let ultimaActividadLocal = Date.now();
    guardarActividad(ultimaActividadLocal);

    function ultimaActividad() {
        return Math.max(ultimaActividadLocal, leerActividad());
    }

    function mantenerServidor() {
        ultimoAvisoServidor = Date.now();
        fetch(urlMantener, { credentials: "same-origin", redirect: "manual" })
            .then(function (respuesta) {
                // 204 = sesión viva; cualquier otra cosa = el servidor ya la cerró
                if (respuesta.status !== 204) {
                    window.location.href = urlSalir;
                }
            })
            .catch(function () { /* sin conexión: se reintenta en el próximo ciclo */ });
    }

    function ocultarAviso() {
        if (aviso) {
            aviso.hidden = true;
        }
    }

    function mostrarAviso() {
        if (!aviso) {
            aviso = document.createElement("div");
            aviso.className = "aviso-sesion";
            aviso.setAttribute("role", "alertdialog");
            aviso.setAttribute("aria-live", "assertive");
            aviso.innerHTML =
                '<p>Tu sesión se cerrará pronto por inactividad.</p>' +
                '<button type="button" class="btn-primary btn-sm">Seguir conectado</button>';
            aviso.querySelector("button").addEventListener("click", function () {
                registrarActividad();
                mantenerServidor();
            });
            document.body.appendChild(aviso);
        }
        aviso.hidden = false;
    }

    function registrarActividad() {
        guardarActividad(Date.now());
        ocultarAviso();
    }

    ["mousedown", "keydown", "scroll", "touchstart", "mousemove"].forEach(function (evento) {
        window.addEventListener(evento, registrarActividad, { passive: true });
    });

    setInterval(function () {
        const ahora = Date.now();
        const inactivo = ahora - ultimaActividad();

        if (inactivo >= LIMITE) {
            window.location.href = urlSalir;
            return;
        }

        if (inactivo >= LIMITE - AVISO_ANTES) {
            mostrarAviso();
        } else {
            ocultarAviso();
        }

        // Hubo actividad desde el último aviso al servidor
        if (ultimaActividad() > ultimoAvisoServidor && ahora - ultimoAvisoServidor >= CADA_CUANTO_AVISAR_SERVIDOR) {
            mantenerServidor();
        }
    }, 15 * 1000);
})();
