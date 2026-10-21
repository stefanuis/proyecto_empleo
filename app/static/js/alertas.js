// Alertas propias de la aplicación (reemplazan alert/confirm del navegador
// y SweetAlert).
//
// - Alertas.mostrar(mensaje, tipo, opciones): aviso flotante (toast).
//   tipo: "success" | "error" | "warning" | "info".
// - Alertas.confirmar(mensaje, opciones): ventana de confirmación con los
//   colores de la app. Devuelve una promesa que resuelve true / false.
// - Cualquier <form data-confirmar="..."> pide confirmación antes de enviarse.
//   Con data-confirmar-tipo="peligro" el botón de aceptar sale en rojo.
// - Los mensajes que envía el servidor (_alertas.html) salen como toasts.
(function () {
    const DURACION = { success: 5000, info: 5000, warning: 8000, error: 0 };
    const ICONOS = { success: "✓", error: "✕", warning: "!", info: "i" };
    const TITULOS = { success: "Listo", error: "Error", warning: "Atención", info: "Información" };

    function normalizarTipo(tipo) {
        if (tipo === "danger") {
            return "error";
        }
        return ICONOS[tipo] ? tipo : "info";
    }

    function contenedor() {
        let caja = document.querySelector(".alertas-globales");
        if (!caja) {
            caja = document.createElement("div");
            caja.className = "alertas-globales";
            caja.setAttribute("aria-live", "polite");
            document.body.appendChild(caja);
        }
        return caja;
    }

    function cerrar(alerta) {
        if (!alerta || alerta.classList.contains("alerta-saliendo")) {
            return;
        }
        alerta.classList.add("alerta-saliendo");
        window.setTimeout(function () {
            alerta.remove();
        }, 250);
    }

    // Activa cierre, autocierre y pausa al pasar el mouse sobre un toast
    function preparar(alerta) {
        const boton = alerta.querySelector("[data-alerta-cerrar]");
        if (boton) {
            boton.addEventListener("click", function () {
                cerrar(alerta);
            });
        }

        const demora = Number(alerta.dataset.alertaAutocierre);
        if (!Number.isFinite(demora) || demora <= 0) {
            return;
        }

        const barra = alerta.querySelector(".alerta-progreso");
        if (barra) {
            barra.style.animationDuration = demora + "ms";
        }

        let restante = demora;
        let inicio = Date.now();
        let temporizador = window.setTimeout(function () { cerrar(alerta); }, restante);

        alerta.addEventListener("mouseenter", function () {
            window.clearTimeout(temporizador);
            restante -= Date.now() - inicio;
            alerta.classList.add("alerta-pausada");
        });
        alerta.addEventListener("mouseleave", function () {
            inicio = Date.now();
            temporizador = window.setTimeout(function () { cerrar(alerta); }, Math.max(restante, 1000));
            alerta.classList.remove("alerta-pausada");
        });
    }

    function mostrar(mensaje, tipo, opciones) {
        opciones = opciones || {};
        tipo = normalizarTipo(tipo);
        const duracion = opciones.duracion !== undefined ? opciones.duracion : DURACION[tipo];

        const alerta = document.createElement("div");
        alerta.className = "alerta alerta-" + tipo;
        alerta.setAttribute("role", tipo === "error" || tipo === "warning" ? "alert" : "status");
        if (duracion > 0) {
            alerta.dataset.alertaAutocierre = String(duracion);
        }

        const icono = document.createElement("span");
        icono.className = "alerta-icono";
        icono.setAttribute("aria-hidden", "true");
        icono.textContent = ICONOS[tipo];

        const cuerpo = document.createElement("div");
        cuerpo.className = "alerta-cuerpo";
        const titulo = document.createElement("strong");
        titulo.className = "alerta-titulo";
        titulo.textContent = opciones.titulo || TITULOS[tipo];
        const texto = document.createElement("span");
        texto.className = "alerta-mensaje";
        texto.textContent = mensaje;
        cuerpo.append(titulo, texto);

        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "alerta-cerrar";
        boton.setAttribute("aria-label", "Cerrar alerta");
        boton.setAttribute("data-alerta-cerrar", "");
        boton.textContent = "×";

        alerta.append(icono, cuerpo, boton);
        if (duracion > 0) {
            const barra = document.createElement("span");
            barra.className = "alerta-progreso";
            alerta.appendChild(barra);
        }

        contenedor().appendChild(alerta);
        preparar(alerta);
        return alerta;
    }

    function confirmar(mensaje, opciones) {
        opciones = opciones || {};
        const peligro = opciones.tipo === "peligro";
        const focoAnterior = document.activeElement;

        return new Promise(function (resolver) {
            const fondo = document.createElement("div");
            fondo.className = "confirmacion-fondo";

            const caja = document.createElement("div");
            caja.className = "confirmacion" + (peligro ? " confirmacion-peligro" : "");
            caja.setAttribute("role", "alertdialog");
            caja.setAttribute("aria-modal", "true");
            caja.setAttribute("aria-labelledby", "confirmacion-titulo");
            caja.setAttribute("aria-describedby", "confirmacion-mensaje");

            const icono = document.createElement("span");
            icono.className = "confirmacion-icono";
            icono.setAttribute("aria-hidden", "true");
            icono.textContent = peligro ? "!" : "?";

            const titulo = document.createElement("h2");
            titulo.id = "confirmacion-titulo";
            titulo.className = "confirmacion-titulo";
            titulo.textContent = opciones.titulo || (peligro ? "¿Estás seguro?" : "Confirmar acción");

            const texto = document.createElement("p");
            texto.id = "confirmacion-mensaje";
            texto.className = "confirmacion-mensaje";
            texto.textContent = mensaje;

            const acciones = document.createElement("div");
            acciones.className = "confirmacion-acciones";

            const cancelar = document.createElement("button");
            cancelar.type = "button";
            cancelar.className = "btn-secondary";
            cancelar.textContent = opciones.textoCancelar || "Cancelar";

            const aceptar = document.createElement("button");
            aceptar.type = "button";
            aceptar.className = "btn-primary confirmacion-aceptar";
            aceptar.textContent = opciones.textoAceptar || (peligro ? "Sí, continuar" : "Aceptar");

            acciones.append(cancelar, aceptar);
            caja.append(icono, titulo, texto, acciones);
            fondo.appendChild(caja);
            document.body.appendChild(fondo);
            document.body.classList.add("confirmacion-abierta");

            requestAnimationFrame(function () {
                fondo.classList.add("abierta");
            });
            // En acciones peligrosas el foco empieza en "Cancelar"
            (peligro ? cancelar : aceptar).focus();

            function terminar(resultado) {
                document.removeEventListener("keydown", teclado, true);
                fondo.classList.remove("abierta");
                document.body.classList.remove("confirmacion-abierta");
                window.setTimeout(function () { fondo.remove(); }, 200);
                if (focoAnterior && typeof focoAnterior.focus === "function") {
                    focoAnterior.focus();
                }
                resolver(resultado);
            }

            function teclado(e) {
                if (e.key === "Escape") {
                    e.preventDefault();
                    terminar(false);
                } else if (e.key === "Tab") {
                    // Mantiene el foco dentro de la ventana
                    e.preventDefault();
                    (document.activeElement === cancelar ? aceptar : cancelar).focus();
                }
            }

            cancelar.addEventListener("click", function () { terminar(false); });
            aceptar.addEventListener("click", function () { terminar(true); });
            fondo.addEventListener("click", function (e) {
                if (e.target === fondo) {
                    terminar(false);
                }
            });
            document.addEventListener("keydown", teclado, true);
        });
    }

    window.Alertas = { mostrar: mostrar, confirmar: confirmar, cerrar: cerrar };

    // Formularios con data-confirmar: se pausa el envío hasta que la persona acepte
    document.addEventListener("submit", function (e) {
        const form = e.target;
        if (!(form instanceof HTMLFormElement) || !form.dataset.confirmar) {
            return;
        }
        if (form.dataset.confirmado === "1") {
            delete form.dataset.confirmado;
            return;
        }
        e.preventDefault();
        const boton = e.submitter;
        confirmar(form.dataset.confirmar, {
            tipo: form.dataset.confirmarTipo,
            titulo: form.dataset.confirmarTitulo,
            textoAceptar: form.dataset.confirmarAceptar
        }).then(function (ok) {
            if (!ok) {
                return;
            }
            form.dataset.confirmado = "1";
            if (typeof form.requestSubmit === "function") {
                form.requestSubmit(boton || undefined);
            } else {
                form.submit();
            }
        });
    }, true);

    function iniciar() {
        // Se lleva al <body> para que ningún contenedor animado lo desplace
        const caja = document.querySelector(".alertas-globales");
        if (caja && caja.parentElement !== document.body) {
            document.body.appendChild(caja);
        }
        document.querySelectorAll(".alertas-globales .alerta").forEach(preparar);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar);
    } else {
        iniciar();
    }
})();
