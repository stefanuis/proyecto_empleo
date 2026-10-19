document.addEventListener("DOMContentLoaded", () => {
    const flatpickr = window.flatpickr;
    const localeEspanol = flatpickr.l10ns.es;
    const contenedor = document.getElementById("experiencia-container");
    const selectorFecha = 'input.campo-fecha:not([type="hidden"])';
    const selectorFechaNueva = `${selectorFecha}:not([data-fecha-ok="1"])`;
    const estadoDisabledOriginal = new WeakMap();

    const sincronizarFechaSalida = (fila) => {
        const trabajoActual = fila.querySelector(".campo-actual");
        const fechaSalida = fila.querySelector(
            'input.campo-fecha[name$="-fecha_salida"]'
        );

        if (!trabajoActual || !fechaSalida) {
            return;
        }

        const disabled = trabajoActual.checked
            || estadoDisabledOriginal.get(fechaSalida);
        fechaSalida.disabled = Boolean(disabled);

        const instancia = fechaSalida._flatpickr;
        if (instancia && instancia.altInput) {
            instancia.altInput.disabled = Boolean(disabled);
            if (fechaSalida.readOnly) {
                instancia.altInput.readOnly = true;
            }
        }
    };

    const inicializarFecha = (input) => {
        if (
            input.type === "hidden"
            || input.dataset.fechaOk === "1"
        ) {
            return;
        }

        estadoDisabledOriginal.set(input, input.disabled);
        const instancia = flatpickr(input, {
            locale: localeEspanol,
            altInput: true,
            altInputClass: "form-control",
            altFormat: "d/m/Y",
            dateFormat: "Y-m-d",
            maxDate: "today",
        });
        input.dataset.fechaOk = "1";

        if (instancia.altInput) {
            instancia.altInput.disabled = input.disabled;
            if (input.readOnly) {
                instancia.altInput.readOnly = true;
            }
        }
    };

    const inicializarFechasEn = (nodo) => {
        if (nodo.matches && nodo.matches(selectorFechaNueva)) {
            inicializarFecha(nodo);
        }

        if (nodo.querySelectorAll) {
            nodo.querySelectorAll(selectorFechaNueva).forEach(inicializarFecha);
        }

        const fila = nodo.closest
            ? nodo.closest(".experiencia-fila")
            : null;
        if (fila) {
            sincronizarFechaSalida(fila);
        }

        if (nodo.querySelectorAll) {
            nodo.querySelectorAll(".experiencia-fila").forEach(
                sincronizarFechaSalida
            );
        }
    };

    document.querySelectorAll(selectorFecha).forEach(inicializarFecha);
    contenedor.querySelectorAll(".experiencia-fila").forEach(
        sincronizarFechaSalida
    );

    contenedor.addEventListener("change", (evento) => {
        if (!evento.target.matches(".campo-actual")) {
            return;
        }

        const fila = evento.target.closest(".experiencia-fila");
        if (!fila) {
            return;
        }

        const fechaSalida = fila.querySelector(
            'input.campo-fecha[name$="-fecha_salida"]'
        );
        if (fechaSalida && evento.target.checked) {
            const instancia = fechaSalida._flatpickr;
            if (instancia) {
                instancia.clear();
            } else {
                fechaSalida.value = "";
            }
        }

        sincronizarFechaSalida(fila);
    });

    new MutationObserver((mutaciones) => {
        for (const mutacion of mutaciones) {
            mutacion.addedNodes.forEach((nodo) => {
                if (
                    nodo.matches?.(selectorFechaNueva)
                    || nodo.querySelector?.(selectorFechaNueva)
                ) {
                    inicializarFechasEn(nodo);
                }
            });
        }
    }).observe(contenedor, { childList: true, subtree: true });
});
