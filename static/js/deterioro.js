
let graficoDeterioro = null;
let componentesActuales = [];

// ==========================================
// NAVEGACIÓN
// ==========================================

function mostrarSeccion(id) {
    document.querySelectorAll(".seccion").forEach(seccion => {
        seccion.classList.add("oculto");
    });

    const seleccionada = document.getElementById(id);

    if (seleccionada) {
        seleccionada.classList.remove("oculto");
    }

    document.querySelectorAll(".menu-enlace").forEach(enlace => {
        enlace.classList.toggle(
            "activo",
            enlace.getAttribute("href") === `#${id}`
        );
    });
}

document.querySelectorAll(".menu-enlace").forEach(enlace => {
    enlace.addEventListener("click", function(event) {
        event.preventDefault();

        const id = this.getAttribute("href").substring(1);
        mostrarSeccion(id);
    });
});


// ==========================================
// FORMULARIO
// ==========================================

function mostrarFormulario() {
    document.getElementById("formulario-componente")
        .classList.remove("oculto");

    document.getElementById("formulario-componente")
        .scrollIntoView({ behavior: "smooth" });
}

function ocultarFormulario() {
    document.getElementById("formulario-componente")
        .classList.add("oculto");

    document.getElementById("form-componente").reset();
}


// ==========================================
// CARGAR DATOS DESDE POSTGRESQL
// ==========================================

async function cargarDatos() {
    try {
        const respuesta = await fetch("/api/dashboard/deterioro");

        if (!respuesta.ok) {
            throw new Error("No se pudieron cargar los datos.");
        }

        const datos = await respuesta.json();

        componentesActuales = datos.componentes;
        cargarComponentesMedicion();

        actualizarIndicadores(datos);
        actualizarTablas(datos.componentes);
        actualizarGrafico(datos);

    } catch (error) {
        console.error("Error al cargar el panel:", error);
    }
}


// ==========================================
// INDICADORES
// ==========================================

function actualizarIndicadores(datos) {
    document.getElementById("total-componentes").textContent =
        datos.total_componentes;

    document.getElementById("total-mediciones").textContent =
        datos.total_mediciones;

    document.getElementById("requieren-inspeccion").textContent =
        datos.requieren_inspeccion;

    document.getElementById("ultima-actualizacion").textContent =
        datos.ultima_actualizacion;
}


// ==========================================
// TABLAS
// ==========================================

function crearCelda(fila, valor) {
    const celda = document.createElement("td");
    celda.textContent = valor ?? "--";
    fila.appendChild(celda);
}

function obtenerEstado(componente) {
    if (componente.ultimo_deterioro === null) {
        return "Sin medición";
    }

    if (
        componente.ultimo_deterioro >=
        componente.umbral_inspeccion
    ) {
        return "Requiere inspección";
    }

    return "Operativo";
}

function actualizarTablas(componentes) {
    const tablaPanel = document.getElementById("tabla-componentes");
    const tablaInventario = document.getElementById(
        "inventario-componentes"
    );

    tablaPanel.replaceChildren();
    tablaInventario.replaceChildren();

    if (componentes.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = 6;
        celda.className = "sin-datos";
        celda.textContent = "Todavía no hay componentes registrados.";

        fila.appendChild(celda);
        tablaPanel.appendChild(fila);

        const filaInventario = document.createElement("tr");
        const celdaInventario = document.createElement("td");

        celdaInventario.colSpan = 7;
        celdaInventario.className = "sin-datos";
        celdaInventario.textContent =
            "No hay componentes registrados todavía.";

        filaInventario.appendChild(celdaInventario);
        tablaInventario.appendChild(filaInventario);

        return;
    }

    componentes.forEach(componente => {
        // Tabla del panel principal
        const filaPanel = document.createElement("tr");

        crearCelda(filaPanel, componente.codigo);
        crearCelda(filaPanel, componente.nombre);
        crearCelda(filaPanel, componente.tipo);
        crearCelda(filaPanel, componente.ubicacion);
        crearCelda(
            filaPanel,
            `${componente.umbral_inspeccion} ${componente.unidad_indicador}`
        );
        crearCelda(filaPanel, obtenerEstado(componente));

        tablaPanel.appendChild(filaPanel);


        // Tabla del inventario
        const filaInventario = document.createElement("tr");

        crearCelda(filaInventario, componente.codigo);
        crearCelda(filaInventario, componente.nombre);
        crearCelda(filaInventario, componente.tipo);
        crearCelda(filaInventario, componente.ubicacion);
        crearCelda(filaInventario, componente.unidad_indicador);
        crearCelda(filaInventario, componente.umbral_inspeccion);

        const acciones = document.createElement("td");
        acciones.textContent = "Registrado";

        filaInventario.appendChild(acciones);

        tablaInventario.appendChild(filaInventario);
    });
}


// ==========================================
// GRÁFICO DE DETERIORO
// ==========================================

function actualizarGrafico(datos) {
    const canvas = document.getElementById("grafico-deterioro");

    if (graficoDeterioro) {
        graficoDeterioro.destroy();
    }

    const tiempos = [
        ...new Set(datos.mediciones.map(m => m.tiempo))
    ].sort((a, b) => a - b);

    const datasets = datos.componentes.map(componente => {
        const mediciones = datos.mediciones.filter(
            m => m.componente_id === componente.id
        );

        return {
            label: componente.codigo,
            data: tiempos.map(tiempo => {
                const medicion = mediciones.find(
                    m => m.tiempo === tiempo
                );

                return medicion ? medicion.deterioro : null;
            }),
            borderWidth: 2,
            tension: 0.3,
            spanGaps: false
        };
    }).filter(dataset => dataset.data.some(valor => valor !== null));

    if (datasets.length === 0) {
        return;
    }

    graficoDeterioro = new Chart(canvas, {
        type: "line",

        data: {
            labels: tiempos,
            datasets: datasets
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: "bottom"
                }
            },

            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Tiempo"
                    }
                },

                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Deterioro"
                    }
                }
            }
        }
    });
}


// ==========================================
// GUARDAR COMPONENTE
// ==========================================

document.getElementById("form-componente")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const datos = {
            codigo: document.getElementById("codigo").value.trim(),
            nombre: document.getElementById("nombre").value.trim(),
            tipo: document.getElementById("tipo").value,
            ubicacion: document.getElementById("ubicacion").value.trim(),
            unidad_indicador: document.getElementById(
                "unidad-indicador"
            ).value.trim(),
            umbral_inspeccion: document.getElementById("umbral").value,
            descripcion: document.getElementById("descripcion").value.trim()
        };

        try {
            const respuesta = await fetch("/api/componentes", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(datos)
            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                alert(resultado.error || "No se pudo registrar.");
                return;
            }

            alert(resultado.mensaje);

            this.reset();
            ocultarFormulario();

            await cargarDatos();

        } catch (error) {
            console.error("Error al registrar:", error);
            alert("No se pudo conectar con el servidor.");
        }
    });


// ==========================================
// BUSCADOR DE COMPONENTES
// ==========================================

document.getElementById("buscar-componente")
    .addEventListener("input", function() {

        const busqueda = this.value.toLowerCase();

        const filtrados = componentesActuales.filter(componente =>
            componente.codigo.toLowerCase().includes(busqueda) ||
            componente.nombre.toLowerCase().includes(busqueda) ||
            componente.tipo.toLowerCase().includes(busqueda)
        );

        actualizarTablas(filtrados);
    });


// ==========================================
// INICIALIZACIÓN
// ==========================================


// ==========================================
// MEDICIONES DE DETERIORO
// ==========================================

let medicionesActuales = [];


// Mostrar formulario
function mostrarFormularioMedicion() {

    const formulario = document.getElementById(
        "formulario-medicion"
    );

    formulario.classList.remove("oculto");

    cargarComponentesMedicion();

    formulario.scrollIntoView({
        behavior: "smooth"
    });
}


// Ocultar formulario
function ocultarFormularioMedicion() {

    document.getElementById("formulario-medicion")
        .classList.add("oculto");

    document.getElementById("form-medicion").reset();
}


// Cargar componentes en el selector
function cargarComponentesMedicion() {

    const selector = document.getElementById(
        "componente-medicion"
    );

    const valorAnterior = selector.value;

    selector.replaceChildren();

    const opcionInicial = document.createElement("option");

    opcionInicial.value = "";
    opcionInicial.textContent = "Selecciona un componente";

    selector.appendChild(opcionInicial);

    componentesActuales.forEach(componente => {

        const opcion = document.createElement("option");

        opcion.value = componente.id;

        opcion.textContent =
            `${componente.codigo} - ${componente.nombre}`;

        selector.appendChild(opcion);

    });

    if (
        componentesActuales.some(
            componente => String(componente.id) === valorAnterior
        )
    ) {
        selector.value = valorAnterior;
    }
}


// Consultar mediciones
async function cargarMediciones() {

    try {

        const respuesta = await fetch("/api/mediciones");

        if (!respuesta.ok) {
            throw new Error("No se pudieron cargar las mediciones.");
        }

        medicionesActuales = await respuesta.json();

        actualizarTablaMediciones(medicionesActuales);

    } catch (error) {

        console.error("Error al cargar mediciones:", error);

    }
}


// Mostrar tabla de mediciones
function actualizarTablaMediciones(mediciones) {

    const tabla = document.getElementById("tabla-mediciones");

    tabla.replaceChildren();

    if (mediciones.length === 0) {

        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = 6;
        celda.className = "sin-datos";
        celda.textContent = "No hay mediciones registradas todavía.";

        fila.appendChild(celda);
        tabla.appendChild(fila);

        return;
    }

    mediciones.forEach(medicion => {

        const fila = document.createElement("tr");

        crearCelda(fila, medicion.componente);
        crearCelda(fila, medicion.codigo);
        crearCelda(fila, medicion.tiempo);
        crearCelda(fila, medicion.deterioro);
        crearCelda(fila, medicion.fecha_medicion);
        crearCelda(fila, medicion.observacion || "--");

        tabla.appendChild(fila);

    });
}


// Registrar medición
document.getElementById("form-medicion")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const datos = {

            componente_id: document.getElementById(
                "componente-medicion"
            ).value,

            tiempo: document.getElementById(
                "tiempo-medicion"
            ).value,

            deterioro: document.getElementById(
                "valor-deterioro"
            ).value,

            observacion: document.getElementById(
                "observacion-medicion"
            ).value.trim()

        };

        try {

            const respuesta = await fetch("/api/mediciones", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(datos)

            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {

                alert(resultado.error || "No se pudo registrar la medición.");

                return;

            }

            alert(resultado.mensaje);

            this.reset();

            ocultarFormularioMedicion();

            await cargarDatos();

            await cargarMediciones();

        } catch (error) {

            console.error("Error al registrar medición:", error);

            alert("No se pudo conectar con el servidor.");

        }

    });


// Buscar mediciones
document.getElementById("buscar-medicion")
    .addEventListener("input", function() {

        const busqueda = this.value.toLowerCase();

        const filtradas = medicionesActuales.filter(medicion =>

            medicion.componente.toLowerCase().includes(busqueda) ||

            medicion.codigo.toLowerCase().includes(busqueda)

        );

        actualizarTablaMediciones(filtradas);

    });


// Actualizar la inicialización
document.addEventListener("DOMContentLoaded", () => {

    cargarDatos();

    cargarMediciones();

});
