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
        // Cargar historial al ingresar a esa sección
    if (id === "historial") {
        cargarHistorial();
    }
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
        cargarComponentesRaices();
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

// ==========================================
// SISTEMAS LINEALES
// ==========================================

let escenariosSistemas = [];
let graficoTiempoSistemas = null;
let graficoErrorSistemas = null;


// ------------------------------------------
// 1. CARGAR ESCENARIOS DESDE LA BASE DE DATOS
// ------------------------------------------
async function cargarEscenariosSistemas() {
    const mensaje = document.getElementById("mensaje-sistemas");

    try {
        const respuesta = await fetch("/api/sistemas-lineales/escenarios");
        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || "No se pudieron cargar los escenarios.");
        }

        // Comprobar que Flask haya devuelto una lista.
        if (!Array.isArray(datos)) {
            throw new Error("El servidor no devolvió una lista válida de escenarios.");
        }

        escenariosSistemas = datos;

        const radios = document.querySelectorAll(
            'input[name="escenario-sistema"]'
        );

        radios.forEach(radio => {
            const escenario = escenariosSistemas.find(
                item => item.tipo === radio.value
            );

            radio.disabled = !escenario;

            if (escenario) {
                radio.dataset.escenarioId = escenario.id;
            }
        });

        radios.forEach(radio => {
            radio.removeEventListener(
                "change",
                cargarMatrizEscenarioSeleccionado
            );

            radio.addEventListener(
                "change",
                cargarMatrizEscenarioSeleccionado
            );
        });

        const seleccionado = document.querySelector(
            'input[name="escenario-sistema"]:checked'
        );

        if (seleccionado && !seleccionado.disabled) {
            // Esperar a que la matriz se cargue antes de continuar.
            await cargarMatrizEscenarioSeleccionado();
        }

        if (mensaje) {
            mensaje.textContent = "Escenarios cargados correctamente.";
            mensaje.className = "mensaje-sistemas exito";
        }

    } catch (error) {
        console.error("Error al cargar escenarios:", error);

        if (mensaje) {
            mensaje.textContent = error.message;
            mensaje.className = "mensaje-sistemas error";
        }
    }
}


async function cargarMatrizEscenarioSeleccionado() {

    const seleccionado = document.querySelector(
        'input[name="escenario-sistema"]:checked'
    );

    if (!seleccionado) return;

    const mensaje = document.getElementById("mensaje-sistemas");

    try {
        const respuesta = await fetch(
            `/api/sistemas-lineales/escenarios/${encodeURIComponent(seleccionado.value)}/sistema`
        );

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || "No se pudo cargar el sistema.");
        }
        console.log("Datos recibidos del escenario:", datos);
        mostrarDatosSistema(datos);

        if (mensaje) {
            mensaje.textContent =
                "Sistema cargado. Puedes modificar la matriz y el vector antes de ejecutar.";
            mensaje.className = "mensaje-sistemas exito";
        }

    } catch (error) {
        console.error(error);

        if (mensaje) {
            mensaje.textContent = error.message;
            mensaje.className = "mensaje-sistemas error";
        }
    }
}

// ------------------------------------------
// 2. OBTENER EL ESCENARIO SELECCIONADO
// ------------------------------------------

function obtenerEscenarioSeleccionado() {
    const seleccionado = document.querySelector(
        'input[name="escenario-sistema"]:checked'
    );

    if (!seleccionado) {
        return null;
    }

    return escenariosSistemas.find(
        escenario => escenario.tipo === seleccionado.value
    ) || null;
}


// ------------------------------------------
// 3. FORMATEAR VALORES NUMÉRICOS
// ------------------------------------------

function formatearNumero(valor) {
    if (valor === null || valor === undefined) {
        return "No disponible";
    }

    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return "No disponible";
    }

    return numero.toExponential(4);
}


// ------------------------------------------
// 4. MOSTRAR LA MATRIZ Y EL VECTOR
// ------------------------------------------



function mostrarDatosSistema(datos) {
    const matriz = datos.A || datos.matriz;
    const vector = datos.b || datos.vector_b;

    if (!Array.isArray(matriz) || !Array.isArray(vector)) {
        console.error("Estructura de datos del sistema incorrecta:", datos);
        throw new Error("No se recibió correctamente la matriz o el vector.");
    }
    
    const contenedor = document.getElementById(
        "datos-matriz-sistema"
    );

    if (!contenedor) return;

    contenedor.replaceChildren();

    // Función para crear títulos
    function crearTitulo(texto) {
        const titulo = document.createElement("h4");
        titulo.textContent = texto;
        return titulo;
    }

    // --------------------------------------
    // MATRIZ A: CAMPOS EDITABLES
    // --------------------------------------

    contenedor.appendChild(
        crearTitulo("Matriz del sistema (A)")
    );

    const matrizVisual = document.createElement("div");
    matrizVisual.className = "matriz-visual";

    matriz.forEach((fila, i) => {
        const filaHTML = document.createElement("div");
        filaHTML.className = "fila-matriz";

        fila.forEach((valor, j) => {
            const input = document.createElement("input");

            input.type = "number";
            input.step = "any";
            input.value = valor;
            input.className = "celda-matriz editable-matriz";

            input.dataset.fila = i;
            input.dataset.columna = j;

            filaHTML.appendChild(input);
        });

        matrizVisual.appendChild(filaHTML);
    });

    contenedor.appendChild(matrizVisual);

    // --------------------------------------
    // VECTOR b: CAMPOS EDITABLES
    // --------------------------------------

    contenedor.appendChild(
        crearTitulo("Vector independiente (b)")
    );

    const vectorVisual = document.createElement("div");
    vectorVisual.className = "vector-visual";

    vector.forEach((valor, i) => {
        const input = document.createElement("input");

        input.type = "number";
        input.step = "any";
        input.value = valor;
        input.className = "celda-vector editable-vector";

        input.dataset.indice = i;

        vectorVisual.appendChild(input);
    });

    contenedor.appendChild(vectorVisual);

    // --------------------------------------
    // SOLUCIÓN EXACTA: SOLO LECTURA
    // --------------------------------------

    contenedor.appendChild(
        crearTitulo("Solución exacta de referencia")
    );

    const solucionVisual = document.createElement("div");
    solucionVisual.className = "vector-visual solucion-visual";

    datos.solucion_exacta.forEach(valor => {
        const celda = document.createElement("div");

        celda.className = "celda-solucion";
        celda.textContent = Number(valor).toFixed(4);

        solucionVisual.appendChild(celda);
    });

    contenedor.appendChild(solucionVisual);

    // --------------------------------------
    // NÚMERO DE CONDICIÓN
    // --------------------------------------

    const condicion = document.createElement("p");
    condicion.className = "condicion-sistema";

    const valorCondicion = Number(datos.numero_condicion);

    condicion.textContent =
        "Número de condición: " +
        (Number.isFinite(valorCondicion)
            ? valorCondicion.toLocaleString("es-BO", {
                maximumFractionDigits: 6
            })
            : "No disponible");

    contenedor.appendChild(condicion);

    document.getElementById(
        "contenedor-datos-sistema"
    )?.classList.remove("oculto");
}


// ------------------------------------------
// 5. MOSTRAR RESULTADOS DE LOS MÉTODOS
// ------------------------------------------
function mostrarResultadosSistemas(datos) {
    const resultados = datos.resultados || {};

    const tabla = document.getElementById(
        "tabla-resultados-sistemas"
    );

    const resumen = document.getElementById(
        "resumen-sistemas"
    );

    if (!tabla) return;

    tabla.replaceChildren();

    if (resumen) {
        resumen.textContent =
            "Simulación #" + datos.simulacion_id +
            " | Escenario: " + datos.escenario;
    }

    // Obtener todos los métodos directamente del backend.
    // Así no dependemos de que sus nombres coincidan exactamente.
    const metodos = Object.entries(resultados);

    metodos.forEach(([nombre, resultado]) => {
        const fila = document.createElement("tr");

        const solucion = Array.isArray(resultado.solucion)
            ? "[" + resultado.solucion.map(
                valor => formatearNumero(valor)
            ).join(", ") + "]"
            : formatearNumero(resultado.solucion);

        const valores = [
            nombre,
            resultado.convergio ? "Convergió" : "No convergió",
            solucion,
            formatearNumero(resultado.error_absoluto),
            formatearNumero(resultado.error_relativo),
            formatearNumero(resultado.residual),
            formatearNumero(resultado.tiempo_ms)
        ];

        valores.forEach(valor => {
            const celda = document.createElement("td");
            celda.textContent = valor;
            fila.appendChild(celda);
        });

        tabla.appendChild(fila);
    });

    document.getElementById(
        "contenedor-resultados-sistema"
    )?.classList.remove("oculto");

    actualizarGraficosSistemas(resultados);
    generarInterpretacion(resultados);
    mostrarTablaIteraciones(resultados);
    document.getElementById(
        "contenedor-interpretacion-sistema"
    )?.classList.remove("oculto");
}


// ------------------------------------------
// 6. GRÁFICOS COMPARATIVOS
// ------------------------------------------

function actualizarGraficosSistemas(resultados) {
    if (typeof Chart === "undefined") {
        console.error("Chart.js no está disponible.");
        return;
    }

    const nombres = Object.keys(resultados);

    const tiempos = nombres.map(nombre => {
        const valor = Number(resultados[nombre].tiempo_ms);
        return Number.isFinite(valor) ? valor : null;
    });

    const errores = nombres.map(nombre => {
        const valor = Number(resultados[nombre].error_absoluto);
        return Number.isFinite(valor) ? valor : null;
    });

    const opciones = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };

    // Gráfico de tiempo

    const canvasTiempo = document.getElementById(
        "grafico-tiempo-sistemas"
    );

    if (canvasTiempo) {
        if (graficoTiempoSistemas) {
            graficoTiempoSistemas.destroy();
        }

        graficoTiempoSistemas = new Chart(canvasTiempo, {
            type: "bar",
            data: {
                labels: nombres,
                datasets: [{
                    label: "Tiempo de ejecución (ms)",
                    data: tiempos,
                    backgroundColor: [
                        "#2563eb",
                        "#15966a",
                        "#e99a32",
                        "#8b5cf6"
                    ],
                    borderRadius: 8
                }]
            },
            options: opciones
        });
    }

    // Gráfico de error absoluto

    const canvasError = document.getElementById(
        "grafico-error-sistemas"
    );

    if (canvasError) {
        if (graficoErrorSistemas) {
            graficoErrorSistemas.destroy();
        }

        graficoErrorSistemas = new Chart(canvasError, {
            type: "bar",
            data: {
                labels: nombres,
                datasets: [{
                    label: "Error absoluto",
                    data: errores,
                    backgroundColor: [
                        "#2563eb",
                        "#15966a",
                        "#e99a32",
                        "#8b5cf6"
                    ],
                    borderRadius: 8
                }]
            },
            options: opciones
        });
    }
}


function mostrarTablaIteraciones(resultados) {

    const tabla = document.getElementById(
        "tabla-iteraciones-sistemas"
    );

    const resumen = document.getElementById(
        "resumen-iteraciones-sistemas"
    );

    if (!tabla) return;

    tabla.replaceChildren();

    const metodosIterativos = [
        "Jacobi",
        "Gauss-Seidel",
        "Gradiente conjugado"
    ];

    let totalRegistros = 0;

    metodosIterativos.forEach(nombre => {

        const resultado = resultados[nombre];

        if (!resultado) return;

        const historial = resultado.historial || [];

        // Caso: el método no pudo ejecutarse.
        if (resultado.solucion === null || resultado.solucion === undefined) {

            const fila = document.createElement("tr");

            const celda = document.createElement("td");
            celda.colSpan = 6;
            celda.textContent =
                `${nombre}: no disponible. ${resultado.error || "No se generó un historial."}`;

            fila.appendChild(celda);
            tabla.appendChild(fila);

            return;
        }

        // Caso: convergió desde la aproximación inicial.
        if (historial.length === 0) {

            const fila = document.createElement("tr");

            const valores = [
                nombre,
                "0",
                JSON.stringify(resultado.solucion),
                "0",
                formatearNumero(resultado.residual),
                "Convergió desde la aproximación inicial"
            ];

            valores.forEach(valor => {
                const celda = document.createElement("td");
                celda.textContent = valor;
                fila.appendChild(celda);
            });

            tabla.appendChild(fila);
            return;
        }

        historial.forEach((registro, indice) => {

            const fila = document.createElement("tr");

            const esUltima = indice === historial.length - 1;

            let estado = "En proceso";

            if (esUltima && resultado.convergio) {
                estado = `Convergió en la iteración ${registro.iteracion}`;
            } else if (esUltima) {
                estado = `No convergió. Última iteración: ${registro.iteracion}`;
            }

            const aproximacion = Array.isArray(registro.aproximacion)
                ? "[" + registro.aproximacion.map(
                    valor => formatearNumero(valor)
                ).join(", ") + "]"
                : "No disponible";

            const valores = [
                nombre,
                registro.iteracion,
                aproximacion,
                formatearNumero(registro.error),
                formatearNumero(registro.residual),
                estado
            ];

            valores.forEach(valor => {
                const celda = document.createElement("td");
                celda.textContent = valor;
                fila.appendChild(celda);
            });

            if (esUltima) {
                fila.classList.add("fila-ultima-iteracion");
            }

            tabla.appendChild(fila);
            totalRegistros++;
        });
    });

    // LU es un método directo, no tiene iteraciones sucesivas.
    const filaLU = document.createElement("tr");
    const celdaLU = document.createElement("td");

    celdaLU.colSpan = 6;
    celdaLU.textContent =
        "LU: no aplica el historial de iteraciones porque es un método directo.";

    filaLU.appendChild(celdaLU);
    tabla.appendChild(filaLU);

    if (resumen) {
        resumen.textContent =
            `Se registraron ${totalRegistros} iteraciones de los métodos iterativos.`;
    }
}

// ------------------------------------------
// 7. INTERPRETAR LOS RESULTADOS
// ------------------------------------------

function generarInterpretacion(resultados) {
    const contenedor = document.getElementById(
        "texto-interpretacion-grafica"
    );

    if (!contenedor) return;

    contenedor.replaceChildren();

    const metodos = Object.entries(resultados);

    if (metodos.length === 0) {
        contenedor.textContent =
            "No se recibieron resultados para interpretar.";
        return;
    }

    const convergidos = metodos.filter(
        ([, datos]) => datos.convergio
    );

    const noConvergidos = metodos.filter(
        ([, datos]) => !datos.convergio
    );

    const tiemposValidos = metodos.filter(
        ([, datos]) => Number.isFinite(Number(datos.tiempo_ms))
    );

    const erroresValidos = metodos.filter(
        ([, datos]) => Number.isFinite(Number(datos.error_absoluto))
    );

    const parrafos = [];

    parrafos.push(
        `Se ejecutaron ${metodos.length} métodos numéricos. ` +
        `${convergidos.length} alcanzaron la convergencia y ` +
        `${noConvergidos.length} no lograron converger ` +
        "con los parámetros establecidos."
    );

    if (tiemposValidos.length > 0) {
        const masRapido = tiemposValidos.reduce(
            (mejor, actual) =>
                Number(actual[1].tiempo_ms) <
                Number(mejor[1].tiempo_ms) ? actual : mejor
        );

        parrafos.push(
            `El menor tiempo de ejecución correspondió a ` +
            `${masRapido[0]}, con ` +
            `${formatearNumero(masRapido[1].tiempo_ms)} ms.`
        );
    }

    if (erroresValidos.length > 0) {
        const masPreciso = erroresValidos.reduce(
            (mejor, actual) =>
                Number(actual[1].error_absoluto) <
                Number(mejor[1].error_absoluto) ? actual : mejor
        );

        parrafos.push(
            `El menor error absoluto se obtuvo con ` +
            `${masPreciso[0]}, cuyo valor fue ` +
            `${formatearNumero(masPreciso[1].error_absoluto)}.`
        );
    }

    if (noConvergidos.length > 0) {
        parrafos.push(
            "Los métodos que no convergieron requieren un análisis " +
            "de sus condiciones de convergencia, la matriz utilizada " +
            "y el máximo de iteraciones establecido."
        );
    }

    parrafos.forEach(texto => {
        const p = document.createElement("p");
        p.textContent = texto;
        contenedor.appendChild(p);
    });
}


// ------------------------------------------
// 8. EJECUTAR LOS MÉTODOS
// ------------------------------------------

async function ejecutarSistemasLineales() {
    const boton = document.getElementById(
        "btn-ejecutar-sistemas"
    );

    const mensaje = document.getElementById(
        "mensaje-sistemas"
    );

    const escenario = obtenerEscenarioSeleccionado();

    if (!escenario) {
        mensaje.textContent = "Selecciona un escenario de prueba.";
        mensaje.className = "mensaje-sistemas error";
        return;
    }

    const tolerancia = Number(
        document.getElementById("tolerancia-sistema").value
    );

    const maxIter = Number(
        document.getElementById("max-iter-sistema").value
    );

    if (!Number.isFinite(tolerancia) || tolerancia <= 0) {
        mensaje.textContent = "Ingresa una tolerancia positiva válida.";
        mensaje.className = "mensaje-sistemas error";
        return;
    }

    if (!Number.isInteger(maxIter) || maxIter < 1) {
        mensaje.textContent =
            "El máximo de iteraciones debe ser un entero mayor que cero.";
        mensaje.className = "mensaje-sistemas error";
        return;
    }

    boton.disabled = true;
    boton.textContent = "Ejecutando métodos...";

    mensaje.textContent = "Procesando la simulación...";
    mensaje.className = "mensaje-sistemas";
    // --------------------------------------
// Obtener los valores editados de A y b
// --------------------------------------
    // --------------------------------------
    // Obtener los valores de la matriz y vector
    // --------------------------------------

    const entradasMatriz = [
        ...document.querySelectorAll(".editable-matriz")
    ];

    const entradasVector = [
        ...document.querySelectorAll(".editable-vector")
    ];

    // Comprobar que la matriz del escenario ya se haya cargado.
    if (entradasMatriz.length === 0 || entradasVector.length === 0) {
        mensaje.textContent =
            "La matriz del escenario todavía no se ha cargado. Selecciona nuevamente el escenario.";
        mensaje.className = "mensaje-sistemas error";
        boton.disabled = false;
        boton.textContent = "Ejecutar métodos";
        return;
    }

    const dimension = Math.sqrt(entradasMatriz.length);

    if (
        !Number.isInteger(dimension) ||
        entradasVector.length !== dimension
    ) {
        mensaje.textContent =
            "La matriz o el vector no tienen dimensiones válidas.";
        mensaje.className = "mensaje-sistemas error";
        boton.disabled = false;
        boton.textContent = "Ejecutar métodos";
        return;
    }

    const matriz = Array.from(
        { length: dimension },
        () => Array(dimension).fill(0)
    );

    for (const input of entradasMatriz) {
        const fila = Number(input.dataset.fila);
        const columna = Number(input.dataset.columna);
        const valor = Number(input.value);

        if (
            input.value.trim() === "" ||
            !Number.isFinite(valor) ||
            !Number.isInteger(fila) ||
            !Number.isInteger(columna) ||
            fila < 0 || fila >= dimension ||
            columna < 0 || columna >= dimension
        ) {
            mensaje.textContent =
                "Revisa los valores de la matriz. Hay datos vacíos o inválidos.";
            mensaje.className = "mensaje-sistemas error";
            boton.disabled = false;
            boton.textContent = "Ejecutar métodos";
            return;
        }

        matriz[fila][columna] = valor;
    }

    const entradasVectorOrdenadas = entradasVector.sort(
        (a, b) =>
            Number(a.dataset.indice) - Number(b.dataset.indice)
    );

    const vector_b = [];

    for (const input of entradasVectorOrdenadas) {
        const valor = Number(input.value);
        const indice = Number(input.dataset.indice);

        if (
            input.value.trim() === "" ||
            !Number.isFinite(valor) ||
            !Number.isInteger(indice) ||
            indice < 0 || indice >= dimension
        ) {
            mensaje.textContent =
                "Revisa los valores del vector. Hay datos vacíos o inválidos.";
            mensaje.className = "mensaje-sistemas error";
            boton.disabled = false;
            boton.textContent = "Ejecutar métodos";
            return;
        }

        vector_b.push(valor);
    }

    try {
        const respuesta = await fetch(
            "/api/sistemas-lineales/ejecutar",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                escenario_id: escenario.id,
                tolerancia: tolerancia,
                max_iter: maxIter,
                matriz: matriz,
                vector_b: vector_b
            })
            }
        );

        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.exito) {
            throw new Error(
                datos.error || "No se pudo ejecutar la simulación."
            );
        }

        mostrarDatosSistema(datos);
        mostrarResultadosSistemas(datos);

        mensaje.textContent =
            datos.mensaje +
            " Simulación #" + datos.simulacion_id;

        mensaje.className = "mensaje-sistemas exito";

    } catch (error) {
        console.error("Error al ejecutar sistemas lineales:", error);

        mensaje.textContent = error.message;
        mensaje.className = "mensaje-sistemas error";

    } finally {
        boton.disabled = false;
        boton.textContent = "Ejecutar métodos";
    }
}


// ------------------------------------------
// 9. EVENTO DEL BOTÓN
// ------------------------------------------

document.getElementById("btn-ejecutar-sistemas")
    ?.addEventListener("click", ejecutarSistemasLineales);


// Actualizar la inicialización
document.addEventListener("DOMContentLoaded", () => {

    cargarDatos();
    cargarMediciones();
    cargarEscenariosSistemas();
    inicializarBusquedaRaices();

});

/* ==========================================
   MODULO: BUSQUEDA DE RAICES
   ========================================== */

let graficoTiempoRaices = null;
let graficoErrorRaices = null;

// ------------------------------------------
// 1. CARGAR COMPONENTES EN EL SELECTOR
// ------------------------------------------

function cargarComponentesRaices() {

    const selector = document.getElementById("componente-raices");

    if (!selector) return;

    const valorAnterior = selector.value;

    selector.innerHTML = `
        <option value="">Selecciona un componente</option>
    `;

    componentesActuales.forEach(componente => {

        const opcion = document.createElement("option");

        opcion.value = componente.id;
        opcion.textContent =
            `${componente.codigo} - ${componente.nombre}`;

        selector.appendChild(opcion);
    });

    // Mantener la selección si el componente sigue existiendo.
    if (
        valorAnterior &&
        componentesActuales.some(
            componente => String(componente.id) === valorAnterior
        )
    ) {
        selector.value = valorAnterior;
    }
}


// ------------------------------------------
// 2. MOSTRAR MENSAJES
// ------------------------------------------

function mostrarMensajeRaices(mensaje, tipo = "info") {

    const elemento = document.getElementById("mensaje-raices");

    if (!elemento) return;

    elemento.textContent = mensaje;

    const estilos = {
        info: {
            color: "#1d4ed8",
            background: "#eff6ff"
        },
        error: {
            color: "#b91c1c",
            background: "#fef2f2"
        },
        exito: {
            color: "#15803d",
            background: "#f0fdf4"
        }
    };

    const estilo = estilos[tipo] || estilos.info;

    elemento.style.color = estilo.color;
    elemento.style.background = estilo.background;
    elemento.style.padding = "10px 12px";
    elemento.style.borderRadius = "8px";
}


// ------------------------------------------
// 3. EJECUTAR ANALISIS
// ------------------------------------------

async function ejecutarAnalisisRaices() {

    const selector = document.getElementById("componente-raices");
    const toleranciaInput = document.getElementById("tolerancia-raices");
    const iteracionesInput = document.getElementById("max-iter-raices");
    const boton = document.getElementById("btn-ejecutar-raices");

    const componenteId = selector.value;
    const tolerancia = Number(toleranciaInput.value);
    const maxIter = Number(iteracionesInput.value);

    // Validaciones del formulario.

    if (!componenteId) {
        mostrarMensajeRaices(
            "Selecciona un componente mecánico.",
            "error"
        );
        return;
    }

    if (!Number.isFinite(tolerancia) || tolerancia <= 0) {
        mostrarMensajeRaices(
            "La tolerancia debe ser un número mayor que cero.",
            "error"
        );
        return;
    }

    if (
        !Number.isInteger(maxIter) ||
        maxIter < 1
    ) {
        mostrarMensajeRaices(
            "El máximo de iteraciones debe ser un entero positivo.",
            "error"
        );
        return;
    }

    // Ocultar resultados anteriores mientras se ejecuta.

    document.getElementById(
        "contenedor-modelo-raices"
    ).classList.add("oculto");

    document.getElementById(
        "contenedor-resultados-raices"
    ).classList.add("oculto");

    boton.disabled = true;
    boton.textContent = "Ejecutando...";

    mostrarMensajeRaices(
        "Calculando el modelo y ejecutando los métodos numéricos...",
        "info"
    );

    try {

        const respuesta = await fetch(
            "/api/busqueda-raices/ejecutar",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    componente_id: Number(componenteId),
                    tolerancia: tolerancia,
                    max_iter: maxIter
                })
            }
        );

        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.exito) {
            throw new Error(
                datos.error || datos.mensaje ||
                "No fue posible ejecutar el análisis."
            );
        }

        // Mostrar resultados.

        mostrarModeloRaices(datos.modelo);

        mostrarResultadosRaices(datos);

        mostrarMensajeRaices(
            "Análisis ejecutado correctamente. Simulación: " +
            datos.simulacion_id,
            "exito"
        );

        document.getElementById(
            "contenedor-modelo-raices"
        ).classList.remove("oculto");

        document.getElementById(
            "contenedor-resultados-raices"
        ).classList.remove("oculto");

    } catch (error) {

        console.error("Error en búsqueda de raíces:", error);

        mostrarMensajeRaices(
            error.message || "Ocurrió un error al ejecutar el análisis.",
            "error"
        );

    } finally {

        boton.disabled = false;
        boton.textContent = "Ejecutar análisis";
    }
}


// ------------------------------------------
// 4. INICIALIZAR EVENTO DEL BOTON
// ------------------------------------------

function inicializarBusquedaRaices() {

    const boton = document.getElementById("btn-ejecutar-raices");

    if (boton) {
        boton.addEventListener(
            "click",
            ejecutarAnalisisRaices
        );
    }
}

/* ==========================================
   4. MOSTRAR MODELO CUADRATICO
   ========================================== */

function formatearNumeroRaices(valor, decimales = 8) {

    if (valor === null || valor === undefined) {
        return "--";
    }

    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return "--";
    }

    return numero.toLocaleString("es-ES", {
        maximumFractionDigits: decimales
    });
}


function mostrarModeloRaices(modelo) {

    if (!modelo) return;

    document.getElementById("valor-d0-raices").textContent =
        formatearNumeroRaices(modelo.D0);

    document.getElementById("valor-alpha-raices").textContent =
        formatearNumeroRaices(modelo.alpha);

    document.getElementById("valor-beta-raices").textContent =
        formatearNumeroRaices(modelo.beta);

    document.getElementById("error-modelo-raices").textContent =
        formatearNumeroRaices(modelo.error_cuadratico);

    document.getElementById("formula-obtenida-raices").textContent =
        modelo.formula ||
        `D(t) = ${formatearNumeroRaices(modelo.D0)} + ` +
        `${formatearNumeroRaices(modelo.alpha)}t + ` +
        `${formatearNumeroRaices(modelo.beta)}t²`;
}

/* ==========================================
   5. TABLA COMPARATIVA DE METODOS
   ========================================== */

function mostrarTablaResultadosRaices(datos) {

    const tabla = document.getElementById(
        "tabla-resultados-raices"
    );

    tabla.innerHTML = "";

    const metodos = [
        {
            clave: "BISECCION",
            nombre: "Bisección"
        },
        {
            clave: "NEWTON_RAPHSON",
            nombre: "Newton-Raphson"
        },
        {
            clave: "SECANTE",
            nombre: "Secante"
        }
    ];

    metodos.forEach(metodo => {

        const resultado = datos.resultados[metodo.clave];

        if (!resultado) return;

        const solucion = resultado.solucion;

        const deterioro = solucion !== null &&
            solucion !== undefined &&
            Number.isFinite(Number(solucion))
            ? Number(datos.modelo.D0) +
              Number(datos.modelo.alpha) * Number(solucion) +
              Number(datos.modelo.beta) * Number(solucion) ** 2
            : null;

        const estado = resultado.convergio
            ? "Convergió"
            : "No convergió";

        const fila = document.createElement("tr");

        const valores = [
            metodo.nombre,
            estado,
            formatearNumeroRaices(solucion),
            formatearNumeroRaices(deterioro),
            formatearNumeroRaices(resultado.error_abs),
            formatearNumeroRaices(resultado.residual),
            resultado.iteraciones ?? "--",
            formatearNumeroRaices(resultado.tiempo_ms, 4)
        ];

        valores.forEach(valor => {

            const celda = document.createElement("td");

            celda.textContent = valor;

            fila.appendChild(celda);
        });

        tabla.appendChild(fila);
    });
}

/* ==========================================
   6. GRAFICO DE TIEMPOS ESTIMADOS
   ========================================== */

function graficarTiempoRaices(datos) {

    const canvas = document.getElementById(
        "grafico-tiempo-raices"
    );

    if (!canvas) return;

    if (graficoTiempoRaices) {
        graficoTiempoRaices.destroy();
    }

    const metodos = [
        { clave: "BISECCION", nombre: "Bisección" },
        { clave: "NEWTON_RAPHSON", nombre: "Newton-Raphson" },
        { clave: "SECANTE", nombre: "Secante" }
    ];

    const etiquetas = [];
    const valores = [];

    metodos.forEach(metodo => {

        const resultado = datos.resultados[metodo.clave];

        if (!resultado) return;

        etiquetas.push(metodo.nombre);

        valores.push(
            resultado.convergio &&
            resultado.solucion !== null
                ? Number(resultado.solucion)
                : null
        );
    });

    graficoTiempoRaices = new Chart(canvas, {

        type: "bar",

        data: {
            labels: etiquetas,

            datasets: [{
                label: "Tiempo estimado",
                data: valores,
                backgroundColor: [
                    "#2563eb",
                    "#16a34a",
                    "#f59e0b"
                ],
                borderRadius: 7
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    callbacks: {
                        label: contexto =>
                            `Tiempo estimado: ${
                                formatearNumeroRaices(contexto.raw)
                            }`
                    }
                }
            },

            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: "Tiempo estimado"
                    }
                },

                x: {
                    title: {
                        display: true,
                        text: "Método numérico"
                    }
                }
            }
        }
    });
}


/* ==========================================
   7. GRAFICO DE CONVERGENCIA
   ========================================== */

function graficarErrorRaices(datos) {

    const canvas = document.getElementById(
        "grafico-error-raices"
    );

    if (!canvas) return;

    if (graficoErrorRaices) {
        graficoErrorRaices.destroy();
    }

    const configuracion = [
        {
            clave: "BISECCION",
            nombre: "Bisección",
            color: "#2563eb"
        },
        {
            clave: "NEWTON_RAPHSON",
            nombre: "Newton-Raphson",
            color: "#16a34a"
        },
        {
            clave: "SECANTE",
            nombre: "Secante",
            color: "#f59e0b"
        }
    ];

    const conjuntos = [];

    configuracion.forEach(metodo => {

        const resultado = datos.resultados[metodo.clave];

        if (!resultado) return;

        const historial = resultado.historial || [];

        if (historial.length === 0) return;

        conjuntos.push({

            label: metodo.nombre,

            data: historial.map(iteracion => ({
                x: Number(iteracion.iteracion),
                y: Math.abs(Number(iteracion.residual))
            })),

            borderColor: metodo.color,
            backgroundColor: metodo.color,
            borderWidth: 2,
            tension: 0.25,
            pointRadius: 3,
            fill: false
        });
    });

    graficoErrorRaices = new Chart(canvas, {

        type: "line",

        data: {
            datasets: conjuntos
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                tooltip: {
                    callbacks: {
                        label: contexto =>
                            `${contexto.dataset.label}: ${
                                formatearNumeroRaices(contexto.parsed.y)
                            }`
                    }
                }
            },

            scales: {

                x: {
                    type: "linear",
                    title: {
                        display: true,
                        text: "Iteración"
                    },
                    ticks: {
                        precision: 0
                    }
                },

                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Valor absoluto del residual"
                    }
                }
            }
        }
    });
}

/* ==========================================
   8. HISTORIAL DE ITERACIONES
   ========================================== */

function mostrarIteracionesRaices(datos) {

    const tabla = document.getElementById(
        "tabla-iteraciones-raices"
    );

    const resumen = document.getElementById(
        "resumen-iteraciones-raices"
    );

    tabla.innerHTML = "";

    let totalIteraciones = 0;

    const metodos = [
        { clave: "BISECCION", nombre: "Bisección" },
        { clave: "NEWTON_RAPHSON", nombre: "Newton-Raphson" },
        { clave: "SECANTE", nombre: "Secante" }
    ];

    metodos.forEach(metodo => {

        const resultado = datos.resultados[metodo.clave];

        if (!resultado) return;

        const historial = resultado.historial || [];

        totalIteraciones += historial.length;

        historial.forEach(iteracion => {

            const fila = document.createElement("tr");

            const valores = [
                metodo.nombre,
                iteracion.iteracion,
                formatearNumeroRaices(iteracion.aproximacion),
                formatearNumeroRaices(iteracion.error_abs),
                formatearNumeroRaices(iteracion.error_rel),
                formatearNumeroRaices(iteracion.residual)
            ];

            valores.forEach(valor => {

                const celda = document.createElement("td");

                celda.textContent = valor;

                fila.appendChild(celda);
            });

            tabla.appendChild(fila);
        });
    });

    resumen.textContent =
        `Se registraron ${totalIteraciones} iteraciones ` +
        `en los tres métodos numéricos.`;
}

/* ==========================================
   9. INTERPRETACION DE RESULTADOS
   ========================================== */

function mostrarInterpretacionRaices(datos) {

    const contenedor = document.getElementById(
        "interpretacion-raices"
    );

    const metodos = [
        { clave: "BISECCION", nombre: "Bisección" },
        { clave: "NEWTON_RAPHSON", nombre: "Newton-Raphson" },
        { clave: "SECANTE", nombre: "Secante" }
    ];

    const convergentes = metodos
        .filter(metodo => {
            const resultado = datos.resultados[metodo.clave];
            return resultado && resultado.convergio;
        })
        .map(metodo => ({
            ...metodo,
            resultado: datos.resultados[metodo.clave]
        }));

    if (convergentes.length === 0) {

        contenedor.textContent =
            "Ninguno de los métodos logró converger. " +
            "Se recomienda revisar las mediciones, el modelo " +
            "y los parámetros numéricos.";

        return;
    }

    const mejor = convergentes.reduce((actual, siguiente) => {

        return Math.abs(Number(siguiente.resultado.residual ?? Infinity)) <
               Math.abs(Number(actual.resultado.residual ?? Infinity))
            ? siguiente
            : actual;

    });

    const tiempoEstimado = Number(mejor.resultado.solucion);

    const unidad = datos.componente.unidad || "";

    contenedor.textContent =
        `El componente ${datos.componente.codigo} - ` +
        `${datos.componente.nombre} tiene un umbral de inspección de ` +
        `${formatearNumeroRaices(datos.componente.umbral)} ${unidad}. ` +
        `De los métodos que convergieron, ${mejor.nombre} obtuvo ` +
        `el menor residual, con un tiempo estimado de ` +
        `${formatearNumeroRaices(tiempoEstimado)} unidades de tiempo. ` +
        `Convergieron ${convergentes.length} de 3 métodos. ` +
        `Esta estimación es una predicción matemática basada en las ` +
        `mediciones registradas y no sustituye una inspección mecánica.`;
}


/* ==========================================
   10. RESUMEN DE SIMULACION
   ========================================== */

function mostrarResumenSimulacionRaices(datos) {

    const elemento = document.getElementById(
        "resumen-simulacion-raices"
    );

    elemento.textContent =
        `Simulación registrada correctamente. ` +
        `ID: ${datos.simulacion_id}. ` +
        `Componente: ${datos.componente.codigo}. ` +
        `Intervalo de búsqueda: [` +
        `${formatearNumeroRaices(datos.intervalo_busqueda.a)}, ` +
        `${formatearNumeroRaices(datos.intervalo_busqueda.b)}].`;
}


/* ==========================================
   11. MOSTRAR TODOS LOS RESULTADOS
   ========================================== */

function mostrarResultadosRaices(datos) {

    mostrarTablaResultadosRaices(datos);

    graficarTiempoRaices(datos);

    graficarErrorRaices(datos);

    mostrarIteracionesRaices(datos);

    mostrarInterpretacionRaices(datos);

    mostrarResumenSimulacionRaices(datos);
}

/* ==========================================
   MODULO: HISTORIAL DE SIMULACIONES
========================================== */

// ------------------------------------------
// 1. CARGAR HISTORIAL DESDE POSTGRESQL
// ------------------------------------------

async function cargarHistorial() {

    const tabla = document.getElementById("tabla-historial");
    const mensaje = document.getElementById("mensaje-historial");

    if (!tabla) return;

    tabla.innerHTML = `
        <tr>
            <td colspan="6">Consultando simulaciones...</td>
        </tr>
    `;

    mensaje?.classList.add("oculto");

    try {

        const respuesta = await fetch("/api/historial");
        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.exito) {
            throw new Error(
                datos.error || "No se pudo consultar el historial."
            );
        }

        actualizarResumenHistorial(datos.historial);

        mostrarTablaHistorial(datos.historial);

    } catch (error) {

        console.error("Error al cargar historial:", error);

        tabla.innerHTML = `
            <tr>
                <td colspan="6">No se pudo cargar el historial.</td>
            </tr>
        `;

        if (mensaje) {
            mensaje.textContent = error.message;
            mensaje.classList.remove("oculto");
        }
    }
}


// ------------------------------------------
// 2. ACTUALIZAR TARJETAS DE RESUMEN
// ------------------------------------------

function actualizarResumenHistorial(historial) {

    const total = historial.length;

    const completadas = historial.filter(
        simulacion => simulacion.estado === "COMPLETADA"
    ).length;

    document.getElementById("historial-total").textContent = total;

    document.getElementById("historial-completadas").textContent =
        completadas;
}


// ------------------------------------------
// 3. IDENTIFICAR TIPO DE ANALISIS
// ------------------------------------------

function obtenerTipoAnalisis(escenario) {

    if (escenario === "BUSQUEDA_RAICES") {
        return "Búsqueda de raíces";
    }

    return "Sistemas lineales";
}


// ------------------------------------------
// 4. MOSTRAR TABLA DE HISTORIAL
// ------------------------------------------

function mostrarTablaHistorial(historial) {

    const tabla = document.getElementById("tabla-historial");

    tabla.replaceChildren();

    if (historial.length === 0) {

        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = 6;
        celda.textContent = "Todavía no hay simulaciones registradas.";

        fila.appendChild(celda);
        tabla.appendChild(fila);

        return;
    }

    historial.forEach(simulacion => {

        const fila = document.createElement("tr");

        const nombresMetodos = simulacion.metodos
            .map(metodo => metodo.metodo)
            .join(", ");

        const valores = [
            simulacion.fecha,
            obtenerTipoAnalisis(simulacion.escenario),
            simulacion.escenario,
            nombresMetodos || "--",
            simulacion.estado
        ];

        valores.forEach(valor => {

            const celda = document.createElement("td");
            celda.textContent = valor;

            fila.appendChild(celda);
        });

        // Botón para consultar los resultados
        const celdaAcciones = document.createElement("td");

        const boton = document.createElement("button");

        boton.type = "button";
        boton.textContent = "Ver resultados";
        boton.className = "btn-secundario";

        boton.addEventListener("click", () => {
            mostrarDetalleHistorial(simulacion);
        });

        celdaAcciones.appendChild(boton);
        fila.appendChild(celdaAcciones);

        tabla.appendChild(fila);
    });
}


// ------------------------------------------
// 5. FORMATEAR RESULTADOS
// ------------------------------------------

function formatearResultadoHistorial(valor) {

    if (valor === null || valor === undefined) {
        return "No disponible";
    }

    if (Array.isArray(valor)) {

        return "[" + valor.map(elemento =>
            formatearResultadoHistorial(elemento)
        ).join(", ") + "]";
    }

    if (typeof valor === "object") {
        return JSON.stringify(valor);
    }

    if (typeof valor === "number") {

        return valor.toLocaleString("es-BO", {
            maximumFractionDigits: 10
        });
    }

    return String(valor);
}


// ------------------------------------------
// 6. MOSTRAR DETALLE DE UNA SIMULACIÓN
// ------------------------------------------

function mostrarDetalleHistorial(simulacion) {

    const panel = document.getElementById("detalle-historial");

    const descripcion = document.getElementById(
        "detalle-historial-descripcion"
    );

    const contenido = document.getElementById(
        "contenido-detalle-historial"
    );

    contenido.replaceChildren();

    descripcion.textContent =
        `Simulación #${simulacion.id} | ` +
        `${simulacion.fecha} | ` +
        `Escenario: ${simulacion.escenario}`;

    if (!simulacion.metodos || simulacion.metodos.length === 0) {

        contenido.textContent =
            "Esta simulación no tiene resultados de métodos registrados.";

    } else {

        simulacion.metodos.forEach(metodo => {

            const tarjeta = document.createElement("div");
            tarjeta.className = "historial-metodo";

            const titulo = document.createElement("h4");
            titulo.textContent = metodo.metodo;

            tarjeta.appendChild(titulo);

            // Estado de convergencia
            agregarDatoHistorial(
                tarjeta,
                "Estado",
                metodo.convergio ? "Convergió" : "No convergió"
            );

            // Resultado numérico
            agregarDatoHistorial(
                tarjeta,
                "Resultado",
                formatearResultadoHistorial(metodo.resultado)
            );

            // Parámetros utilizados
            agregarDatoHistorial(
                tarjeta,
                "Tolerancia",
                formatearResultadoHistorial(metodo.tolerancia)
            );

            agregarDatoHistorial(
                tarjeta,
                "Máximo de iteraciones",
                formatearResultadoHistorial(metodo.max_iter)
            );

            // Tiempo de ejecución
            agregarDatoHistorial(
                tarjeta,
                "Tiempo de ejecución",
                metodo.tiempo_ms !== null &&
                metodo.tiempo_ms !== undefined
                    ? `${formatearResultadoHistorial(metodo.tiempo_ms)} ms`
                    : "No disponible"
            );

            // Métricas de error
            const tituloMetricas = document.createElement("h5");
            tituloMetricas.textContent = "Métricas del método";

            tarjeta.appendChild(tituloMetricas);

            const metricas = metodo.metricas || {};

            if (Object.keys(metricas).length === 0) {

                agregarDatoHistorial(
                    tarjeta,
                    "Métricas",
                    "No disponibles"
                );

            } else {

                Object.entries(metricas).forEach(([clave, valor]) => {

                    const nombre = clave
                        .replaceAll("_", " ")
                        .replace(/^./, letra => letra.toUpperCase());

                    agregarDatoHistorial(
                        tarjeta,
                        nombre,
                        formatearResultadoHistorial(valor)
                    );
                });
            }

            // Interpretación
            if (metodo.interpretacion) {

                const interpretacion = document.createElement("p");

                interpretacion.textContent = metodo.interpretacion;
                interpretacion.className = "historial-interpretacion";

                tarjeta.appendChild(interpretacion);
            }

            contenido.appendChild(tarjeta);
        });
    }

    panel.classList.remove("oculto");

    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ------------------------------------------
// 7. CREAR CAMPOS DEL DETALLE
// ------------------------------------------

function agregarDatoHistorial(contenedor, nombre, valor) {

    const parrafo = document.createElement("p");

    const etiqueta = document.createElement("strong");
    etiqueta.textContent = `${nombre}: `;

    const texto = document.createElement("span");
    texto.textContent = valor;

    parrafo.appendChild(etiqueta);
    parrafo.appendChild(texto);

    contenedor.appendChild(parrafo);
}


// ------------------------------------------
// 8. CERRAR DETALLE
// ------------------------------------------

function cerrarDetalleHistorial() {

    document.getElementById("detalle-historial")
        ?.classList.add("oculto");
}
