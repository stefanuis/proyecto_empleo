document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-alerta-cerrar]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const alerta = boton.closest(".alerta");
            if (alerta) {
                alerta.remove();
            }
        });
    });

    document.querySelectorAll("[data-alerta-autocierre]").forEach(function (alerta) {
        const demora = Number(alerta.dataset.alertaAutocierre);
        if (Number.isFinite(demora) && demora > 0) {
            window.setTimeout(function () {
                alerta.remove();
            }, demora);
        }
    });
});
