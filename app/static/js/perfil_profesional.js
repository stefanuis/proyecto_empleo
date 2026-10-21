// Selector de funciones por área de aplicación. Lo usan el Perfil
// profesional del candidato y el formulario de vacantes del admin: cualquier
// formulario con data-funciones-url y los mismos ids de elementos.
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form[data-funciones-url]");
    const areaSelect = document.getElementById("area_aplicacion");
    const descripcion = document.getElementById("descripcion");
    const descripcionContador = document.getElementById("perfil-descripcion-contador");
    const busqueda = document.getElementById("buscar-funciones");
    const lista = document.getElementById("funciones-lista");
    const mensaje = document.getElementById("funciones-mensaje");
    const avisoCambio = document.getElementById("funciones-aviso");
    const listaSeleccionadas = document.getElementById("funciones-seleccionadas");
    const funcionesVacias = document.getElementById("funciones-vacias");
    const contador = document.getElementById("funciones-contador");

    if (!form || !areaSelect || !lista) {
        return;
    }

    const funcionesUrl = form.dataset.funcionesUrl;
    const funcionesIniciales = new Set(
        JSON.parse(form.dataset.funcionesIniciales || "[]").map(String)
    );
    const seleccionadas = new Map();
    let solicitudActual = 0;
    let areaActual = areaSelect.value;

    const actualizarContadorDescripcion = () => {
        if (descripcion && descripcionContador) {
            descripcionContador.textContent = `${descripcion.value.length} / 500`;
        }
    };

    const actualizarVistaPrevia = () => {
        listaSeleccionadas.replaceChildren();
        contador.textContent = `${seleccionadas.size} seleccionadas`;
        funcionesVacias.hidden = seleccionadas.size > 0;

        for (const funcion of seleccionadas.values()) {
            const item = document.createElement("li");
            item.className = "perfil-profesional-seleccionada";

            const texto = document.createElement("span");
            texto.textContent = funcion.nombre;

            const quitar = document.createElement("button");
            quitar.type = "button";
            quitar.className = "perfil-profesional-quitar";
            quitar.textContent = "Quitar";
            quitar.setAttribute("aria-label", `Quitar ${funcion.nombre}`);
            quitar.addEventListener("click", () => {
                seleccionadas.delete(String(funcion.id));
                const checkbox = Array.from(
                    lista.querySelectorAll('input[name="funciones"]')
                ).find((elemento) => elemento.value === String(funcion.id));
                if (checkbox) {
                    checkbox.checked = false;
                }
                actualizarVistaPrevia();
            });

            item.append(texto, quitar);
            listaSeleccionadas.append(item);
        }
    };

    const filtrarFunciones = () => {
        const termino = busqueda.value.trim().toLocaleLowerCase("es");
        lista.querySelectorAll(".perfil-profesional-opcion").forEach((opcion) => {
            opcion.hidden = !opcion.dataset.nombre.toLocaleLowerCase("es").includes(termino);
        });
    };

    const mostrarMensaje = (texto) => {
        mensaje.textContent = texto;
        mensaje.hidden = false;
    };

    const cargarFunciones = async ({ mantenerSeleccionadas = false } = {}) => {
        const area = areaSelect.value;
        const solicitud = ++solicitudActual;
        lista.replaceChildren();

        if (!area) {
            busqueda.disabled = true;
            mostrarMensaje("Elige primero un área de aplicación para ver sus funciones.");
            return;
        }

        busqueda.disabled = true;
        mostrarMensaje("Cargando funciones...");

        try {
            const respuesta = await fetch(
                `${funcionesUrl}?area_aplicacion=${encodeURIComponent(area)}`,
                { headers: { Accept: "application/json" } }
            );
            if (!respuesta.ok) {
                throw new Error("No se pudieron cargar las funciones del área.");
            }

            const datos = await respuesta.json();
            if (solicitud !== solicitudActual) {
                return;
            }

            const funciones = Array.isArray(datos.funciones) ? datos.funciones : [];
            if (mantenerSeleccionadas) {
                for (const funcion of funciones) {
                    const id = String(funcion.id);
                    if (funcionesIniciales.has(id)) {
                        seleccionadas.set(id, funcion);
                    }
                }
            }

            for (const funcion of funciones) {
                const id = String(funcion.id);
                const label = document.createElement("label");
                label.className = "perfil-profesional-opcion";
                label.dataset.nombre = funcion.nombre;

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.name = "funciones";
                checkbox.value = id;
                checkbox.checked = seleccionadas.has(id);
                checkbox.addEventListener("change", () => {
                    if (checkbox.checked) {
                        seleccionadas.set(id, funcion);
                    } else {
                        seleccionadas.delete(id);
                    }
                    actualizarVistaPrevia();
                });

                const texto = document.createElement("span");
                texto.textContent = funcion.nombre;
                label.append(checkbox, texto);
                lista.append(label);
            }

            busqueda.disabled = false;
            busqueda.value = "";
            mensaje.hidden = funciones.length > 0;
            if (funciones.length === 0) {
                mostrarMensaje("No hay funciones activas para esta área.");
            }
            actualizarVistaPrevia();
            filtrarFunciones();
        } catch (error) {
            if (solicitud === solicitudActual) {
                mostrarMensaje(error.message);
            }
        }
    };

    if (descripcion) {
        descripcion.addEventListener("input", actualizarContadorDescripcion);
    }
    busqueda.addEventListener("input", filtrarFunciones);
    areaSelect.addEventListener("change", () => {
        if (areaActual && areaSelect.value !== areaActual) {
            seleccionadas.clear();
            avisoCambio.hidden = false;
        }
        areaActual = areaSelect.value;
        funcionesIniciales.clear();
        cargarFunciones();
        actualizarVistaPrevia();
    });

    actualizarContadorDescripcion();
    if (areaSelect.value) {
        cargarFunciones({ mantenerSeleccionadas: true });
    } else {
        mostrarMensaje("Elige primero un área de aplicación para ver sus funciones.");
    }
});
