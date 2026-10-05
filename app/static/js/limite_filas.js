(function () {

    function esActiva(fila) {
        if (fila.style.display === "none") return false;

        var marca = fila.querySelector('input[name$="-eliminar"], .campo-eliminar');

        return !(marca && marca.value === "1");
    }

    function iniciar(contenedor) {
        var max = parseInt(contenedor.dataset.maxFilas, 10);
        var selector = contenedor.dataset.filaSelector;
        var boton = contenedor.dataset.botonAgregar
            ? document.querySelector(contenedor.dataset.botonAgregar)
            : null;

        if (!max || !selector || !boton) return;

        function actualizar() {
            var total = Array.prototype.filter.call(
                contenedor.querySelectorAll(selector),
                esActiva
            ).length;

            var lleno = total >= max;

            if (boton.disabled !== lleno) {
                boton.disabled = lleno;
            }
        }

        new MutationObserver(actualizar).observe(contenedor, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["style"]
        });

        actualizar();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-max-filas]").forEach(iniciar);
    });

})();