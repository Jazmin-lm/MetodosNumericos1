
"use strict";

// ======================================================
// SIMTELE-RISK - MODULO 4
// Gestion de sensores y reconstruccion de senales
// ======================================================

let sensores = [];
let senales = [];
let escenarios = [];

let senalActual = null;
let ultimoResultado = null;

let graficaReconstruccion = null;
let graficaErrores = null;
let graficaDashboard = null;


// ======================================================
// UTILIDADES
// ======================================================

const $ = id => document.getElementById(id);

function existe(id) {
    return $(id) !== null;
}

function texto(id, valor) {
    if (existe(id)) {
        $(id).textContent = valor ?? "";
    }
}

function htmlSeguro(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[c]);
}

function numero(valor, decimales = 6) {
    const n = Number(valor);

    if (valor === null || valor === undefined || !Number.isFinite(n)) {
        return "—";
    }

    return n.toFixed(decimales);
}

function mostrarMensaje(id, mensaje, tipo = "info") {
    if (!existe(id)) return;

    $(id).textContent = mensaje;
    $(id).className = "mensaje " + tipo;
}

async function consultarAPI(url, opciones = {}) {
    const respuesta = await fetch(url, opciones);

    let datos;

    try {
        datos = await respuesta.json();
    } catch {
        throw new Error("El servidor devolvió una respuesta no válida.");
    }

    if (!respuesta.ok || datos.exito === false) {
        throw new Error(
            datos.error || "Error al comunicarse con el servidor."
        );
    }

    return datos;
}

function convertirLista(textoValor, nombre) {
    if (!textoValor.trim()) {
        throw new Error("Debes indicar " + nombre + ".");
    }

    const valores = textoValor.split(",").map(v => Number(v.trim()));

    if (valores.some(v => !Number.isFinite(v))) {
        throw new Error(nombre + " contiene valores no válidos.");
    }

    return valores;
}

function parsearPuntos(textoValor, nombre) {
    const lineas = textoValor
        .split(/\r?\n/)
        .map(l => l.trim())
        .filter(Boolean);

    if (!lineas.length) {
        throw new Error("Debes introducir " + nombre + ".");
    }

    return lineas.map((linea, indice) => {
        const partes = linea.split(",").map(v => v.trim());

        if (partes.length !== 2) {
            throw new Error(
                "Formato incorrecto en la línea " + (indice + 1) +
                ". Utiliza tiempo,valor."
            );
        }

        const tiempo = Number(partes[0]);
        const valor = Number(partes[1]);

        if (!Number.isFinite(tiempo) || !Number.isFinite(valor)) {
            throw new Error("Hay valores no numéricos en " + nombre + ".");
        }

        return { tiempo, valor };
    });
}

function llenarSelector(id, elementos, textoInicial, obtenerTexto) {
    if (!existe(id)) return;

    const selector = $(id);
    selector.innerHTML = "";

    const inicial = document.createElement("option");
    inicial.value = "";
    inicial.textContent = textoInicial;
    selector.appendChild(inicial);

    elementos.forEach(elemento => {
        const opcion = document.createElement("option");
        opcion.value = elemento.id;
        opcion.textContent = obtenerTexto(elemento);
        selector.appendChild(opcion);
    });
}

function destruirGrafica(variable) {
    if (variable === "reconstruccion" && graficaReconstruccion) {
        graficaReconstruccion.destroy();
        graficaReconstruccion = null;
    }

    if (variable === "errores" && graficaErrores) {
        graficaErrores.destroy();
        graficaErrores = null;
    }

    if (variable === "dashboard" && graficaDashboard) {
        graficaDashboard.destroy();
        graficaDashboard = null;
    }
}


// ======================================================
// NAVEGACION
// ======================================================

function navegarA(seccion) {
    const destino = $(seccion);

    if (!destino) return;

    document.querySelectorAll(".menu-link").forEach(enlace => {
        enlace.classList.toggle(
            "activo",
            enlace.dataset.seccion === seccion
        );
    });

    destino.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function configurarNavegacion() {
    document.querySelectorAll(".menu-link").forEach(enlace => {
        enlace.addEventListener("click", evento => {
            evento.preventDefault();
            navegarA(enlace.dataset.seccion);
        });
    });

    document.querySelectorAll("[data-ir]").forEach(boton => {
        boton.addEventListener("click", () => {
            navegarA(boton.dataset.ir);
        });
    });
}


// ======================================================
// SENSORES
// ======================================================

async function cargarSensores() {
    const datos = await consultarAPI("/api/sensores/listar");

    sensores = datos.sensores || [];

    llenarSelector(
        "sensorParaSenal",
        sensores,
        "Selecciona un sensor",
        s => `${s.codigo} - ${s.nombre}`
    );

    llenarSelector(
        "sensorConsultaSenales",
        sensores,
        "Selecciona un sensor",
        s => `${s.codigo} - ${s.nombre}`
    );

    llenarSelector(
        "sensorReconstruccion",
        sensores,
        "Selecciona un sensor",
        s => `${s.codigo} - ${s.nombre}`
    );

    texto("totalSensores", sensores.length);

    renderizarListaSensores();
}

function renderizarListaSensores() {
    if (!existe("listaSensores")) return;

    const contenedor = $("listaSensores");

    if (!sensores.length) {
        contenedor.innerHTML = "<p>No hay sensores registrados.</p>";
        return;
    }

    contenedor.innerHTML = sensores.map(sensor => `
        <div class="elemento-lista">
            <div class="elemento-icono">◉</div>

            <div class="elemento-contenido">
                <strong>${htmlSeguro(sensor.nombre)}</strong>
                <small>
                    ${htmlSeguro(sensor.codigo)} ·
                    ${htmlSeguro(sensor.tipo || "Sin tipo")}
                </small>
                <small>
                    ${htmlSeguro(sensor.ubicacion || "Sin ubicación")}
                    · ${htmlSeguro(sensor.unidad_medida)}
                </small>
            </div>

            <span class="estado-etiqueta">
                ${sensor.activo ? "Activo" : "Inactivo"}
            </span>
        </div>
    `).join("");
}

async function registrarSensor(evento) {
    evento.preventDefault();

    const formulario = $("formSensor");
    const boton = formulario.querySelector("button[type='submit']");

    boton.disabled = true;

    try {
        const cuerpo = {
            codigo: $("sensorCodigo").value.trim(),
            nombre: $("sensorNombre").value.trim(),
            tipo: $("sensorTipo").value.trim(),
            ubicacion: $("sensorUbicacion").value.trim(),
            unidad_medida: $("sensorUnidad").value.trim(),
            descripcion: $("sensorDescripcion").value.trim()
        };

        const datos = await consultarAPI("/api/sensores/registrar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cuerpo)
        });

        mostrarMensaje(
            "mensajeSensor",
            `${datos.mensaje} ID: ${datos.sensor_id}`,
            "correcto"
        );

        formulario.reset();

        await cargarSensores();
        await actualizarDashboard();

    } catch (error) {
        mostrarMensaje("mensajeSensor", error.message, "error");
    } finally {
        boton.disabled = false;
    }
}


// ======================================================
// SEÑALES
// ======================================================

async function cargarSenales(sensorId, selectorDestino) {
    const selector = $(selectorDestino);

    if (!selector) return [];

    if (!sensorId) {
        selector.innerHTML =
            '<option value="">Selecciona primero un sensor</option>';
        selector.disabled = true;
        return [];
    }

    selector.disabled = true;
    selector.innerHTML = '<option value="">Cargando señales...</option>';

    const datos = await consultarAPI(
        `/api/sensores/senales/${encodeURIComponent(sensorId)}`
    );

    const lista = datos.senales || [];

    llenarSelector(
        selectorDestino,
        lista,
        "Selecciona una señal",
        s => `${s.nombre} (${s.cantidad_puntos} puntos)`
    );

    selector.disabled = lista.length === 0;

    return lista;
}

async function consultarSenalesPanel() {
    if (!existe("listaSenales")) return;

    const contenedor = $("listaSenales");
    const sensorId = $("sensorConsultaSenales").value;

    if (!sensorId) {
        contenedor.innerHTML =
            "<p>Selecciona un sensor para consultar sus señales.</p>";
        return;
    }

    try {
        const datos = await consultarAPI(
            `/api/sensores/senales/${encodeURIComponent(sensorId)}`
        );

        const lista = datos.senales || [];

        if (!lista.length) {
            contenedor.innerHTML =
                "<p>Este sensor todavía no tiene señales registradas.</p>";
            return;
        }

        contenedor.innerHTML = lista.map(senal => `
            <div class="elemento-lista">
                <div class="elemento-icono morado">∿</div>

                <div class="elemento-contenido">
                    <strong>${htmlSeguro(senal.nombre)}</strong>
                    <small>${htmlSeguro(senal.origen || "Sin origen")}</small>
                    <small>${senal.cantidad_puntos} mediciones registradas</small>
                </div>

                <span class="estado-etiqueta">
                    ${htmlSeguro(senal.estado)}
                </span>
            </div>
        `).join("");

    } catch (error) {
        contenedor.innerHTML =
            `<p class="mensaje error">${htmlSeguro(error.message)}</p>`;
    }
}

async function registrarSenal(evento) {
    evento.preventDefault();

    const formulario = $("formSenal");
    const boton = formulario.querySelector("button[type='submit']");

    boton.disabled = true;

    try {
        const sensorId = Number($("sensorParaSenal").value);

        if (!sensorId) {
            throw new Error("Debes seleccionar un sensor.");
        }

        const puntos = parsearPuntos(
            $("senalPuntos").value,
            "las mediciones"
        );

        const referenciasTexto = $("senalReferencias").value.trim();

        const referencias = referenciasTexto
            ? parsearPuntos(referenciasTexto, "las referencias").map(p => ({
                tiempo: p.tiempo,
                valor_real: p.valor
            }))
            : [];

        const tiempos = puntos.map(p => p.tiempo);
        const tiemposReferencia = referencias.map(p => p.tiempo);

        if (new Set(tiempos).size !== tiempos.length) {
            throw new Error("No puede haber tiempos repetidos en mediciones.");
        }

        if (new Set(tiemposReferencia).size !== tiemposReferencia.length) {
            throw new Error("No puede haber tiempos repetidos en referencias.");
        }

        const cuerpo = {
            sensor_id: sensorId,
            nombre: $("senalNombre").value.trim(),
            origen: $("senalOrigen").value.trim(),
            descripcion: $("senalDescripcion").value.trim(),
            puntos,
            referencias
        };

        const datos = await consultarAPI("/api/sensores/senales", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cuerpo)
        });

        mostrarMensaje(
            "mensajeSenal",
            `${datos.mensaje} ID de señal: ${datos.senal_id}`,
            "correcto"
        );

        formulario.reset();

        await cargarSenales(sensorId, "sensorConsultaSenales");
        await actualizarDashboard();

    } catch (error) {
        mostrarMensaje("mensajeSenal", error.message, "error");
    } finally {
        boton.disabled = false;
    }
}


// ======================================================
// ESCENARIOS
// ======================================================

async function cargarEscenarios() {
    const datos = await consultarAPI("/api/sensores/escenarios");

    escenarios = datos.escenarios || [];

    llenarSelector(
        "escenarioReconstruccion",
        escenarios,
        "Sin escenario específico",
        e => {
            const nombres = {
                NORMAL: "NORMAL",
                ESTRES: "ESTRÉS",
                MAL_CONDICIONADO: "MAL CONDICIONADO"
            };

            return nombres[String(e.tipo).toUpperCase()] || e.tipo;
        }
    );

    return escenarios;
}


// ======================================================
// DETALLE DE SEÑAL
// ======================================================

async function obtenerDatosSenal(senalId) {
    if (!senalId) {
        senalActual = null;

        texto(
            "detalleSenalSeleccionada",
            "Selecciona una señal para consultar sus mediciones."
        );

        return null;
    }

    const datos = await consultarAPI(
        `/api/sensores/senal/${encodeURIComponent(senalId)}`
    );

    senalActual = datos;

    const puntos = datos.puntos || [];
    const referencias = datos.referencias || [];

    const tiempos = puntos.map(p => Number(p.tiempo));

    const minimo = tiempos.length ? Math.min(...tiempos) : null;
    const maximo = tiempos.length ? Math.max(...tiempos) : null;

    if (existe("detalleSenalSeleccionada")) {
        $("detalleSenalSeleccionada").innerHTML = `
            <strong>${htmlSeguro(datos.senal.nombre)}</strong>

            <div class="resumen-puntos">
                <span>Mediciones conocidas: <b>${puntos.length}</b></span>
                <span>Referencias: <b>${referencias.length}</b></span>
                <span>Intervalo: <b>${minimo ?? "—"} a ${maximo ?? "—"}</b></span>
            </div>

            <div class="tabla-scroll">
                <table>
                    <thead>
                        <tr>
                            <th>Tiempo</th>
                            <th>Valor medido</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${puntos.map(p => `
                            <tr>
                                <td>${numero(p.tiempo)}</td>
                                <td>${numero(p.valor)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    }

    return datos;
}


// ======================================================
// SELECTORES DE RECONSTRUCCION
// ======================================================

async function cambioSensorReconstruccion() {
    const sensorId = $("sensorReconstruccion").value;
    const selectorSenal = $("senalReconstruccion");

    senalActual = null;

    selectorSenal.disabled = true;
    selectorSenal.innerHTML =
        '<option value="">Cargando señales...</option>';

    texto(
        "detalleSenalSeleccionada",
        "Selecciona una señal para consultar sus mediciones."
    );

    limpiarResultados();

    try {
        const lista = await cargarSenales(
            sensorId,
            "senalReconstruccion"
        );

        if (!lista.length) {
            texto(
                "detalleSenalSeleccionada",
                "El sensor seleccionado no tiene señales registradas."
            );
        }

    } catch (error) {
        selectorSenal.innerHTML =
            '<option value="">Error al cargar señales</option>';

        texto("estadoReconstruccion", error.message);
    }
}

async function cambioSenalReconstruccion() {
    try {
        limpiarResultados();

        await obtenerDatosSenal(
            $("senalReconstruccion").value
        );

    } catch (error) {
        texto("detalleSenalSeleccionada", error.message);
    }
}


// ======================================================
// LIMPIAR RESULTADOS
// ======================================================

function limpiarResultados() {
    if (existe("tablaResultados")) {
        $("tablaResultados").innerHTML =
            '<tr><td colspan="8">Ejecuta una reconstrucción para consultar resultados.</td></tr>';
    }

    ["Lagrange", "Newton", "Splines"].forEach(nombre => {
        texto("rmse" + nombre, "—");
        texto("mae" + nombre, "MAE: —");
    });

    texto(
        "identificadorReconstruccion",
        "Todavía no se ha ejecutado ninguna reconstrucción."
    );

    destruirGrafica("reconstruccion");
    destruirGrafica("errores");

    ultimoResultado = null;
}


// ======================================================
// EJECUTAR RECONSTRUCCION
// ======================================================

async function ejecutarReconstruccion() {
    const boton = $("ejecutarReconstruccion");

    boton.disabled = true;
    boton.textContent = "Procesando...";

    try {
        const senalId = Number($("senalReconstruccion").value);

        if (!senalId) {
            throw new Error("Debes seleccionar una señal.");
        }

        if (!senalActual || Number(senalActual.senal.id) !== senalId) {
            await obtenerDatosSenal(senalId);
        }

        const puntosEvaluar = convertirLista(
            $("puntosEvaluar").value,
            "los tiempos que deseas reconstruir"
        );

        if (new Set(puntosEvaluar).size !== puntosEvaluar.length) {
            throw new Error("No puede haber tiempos repetidos.");
        }

        if (!senalActual.puntos || senalActual.puntos.length < 2) {
            throw new Error(
                "La señal debe tener al menos dos mediciones conocidas."
            );
        }

        const tiempos = senalActual.puntos.map(p => Number(p.tiempo));
        const minimo = Math.min(...tiempos);
        const maximo = Math.max(...tiempos);

        if (puntosEvaluar.some(t => t < minimo || t > maximo)) {
            throw new Error(
                `Los tiempos deben estar entre ${minimo} y ${maximo}.`
            );
        }

        const escenarioValor = $("escenarioReconstruccion").value;

        const cuerpo = {
            senal_id: senalId,
            puntos_evaluar: puntosEvaluar,
            escenario_id: escenarioValor ? Number(escenarioValor) : null,
            observacion: $("observacionReconstruccion").value.trim()
        };

        texto(
            "estadoReconstruccion",
            "Ejecutando Lagrange, Newton y splines cúbicos..."
        );

        const datos = await consultarAPI("/api/sensores/reconstruir", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cuerpo)
        });

        if (!datos.resultado || !datos.resultado.comparacion) {
            throw new Error(
                "El servidor no devolvió la comparación de resultados."
            );
        }

        ultimoResultado = datos;

        mostrarResultados(datos);

        texto(
            "estadoReconstruccion",
            "Reconstrucción ejecutada y guardada correctamente."
        );

        if (existe("estadoReconstruccion")) {
            $("estadoReconstruccion").className = "mensaje correcto";
        }

        await actualizarDashboard();
        await cargarHistorial();

    } catch (error) {
        texto(
            "estadoReconstruccion",
            "No se pudo completar la reconstrucción: " + error.message
        );

        if (existe("estadoReconstruccion")) {
            $("estadoReconstruccion").className = "mensaje error";
        }

    } finally {
        boton.disabled = false;
        boton.textContent = "Ejecutar reconstrucción";
    }
}


// ======================================================
// MOSTRAR RESULTADOS
// ======================================================

function mostrarResultados(datos) {
    const resultado = datos.resultado;
    const filas = resultado.comparacion || [];
    const curvas = resultado.curvas || {};
    const metricas = datos.metricas || {};

    const nombresEscenarios = {
        NORMAL: "NORMAL",
        ESTRES: "ESTRÉS",
        MAL_CONDICIONADO: "MAL CONDICIONADO"
    };

    const escenario = String(
        datos.escenario || "NORMAL"
    ).toUpperCase();

    const nombreEscenario =
        nombresEscenarios[escenario] || escenario;

    const descripcionPreparacion =
        datos.datos_entrada?.descripcion ||
        "Se utilizaron los datos disponibles de la señal.";

    if (existe("identificadorReconstruccion")) {
        $("identificadorReconstruccion").innerHTML = `
            <strong>Reconstrucción guardada correctamente.</strong>

            <div class="resumen-puntos">
                <span>ID: <b>${datos.reconstruccion_id}</b></span>
                <span>Señal: <b>${datos.senal_id}</b></span>
                <span>Escenario: <b>${htmlSeguro(nombreEscenario)}</b></span>
                <span>Estado: <b>${htmlSeguro(datos.estado)}</b></span>
                <span>Tiempo total: <b>${numero(datos.tiempo_ms, 3)} ms</b></span>
            </div>

            <p>
                <strong>Preparación de datos:</strong>
                ${htmlSeguro(descripcionPreparacion)}
            </p>
        `;
    }

    const nombres = {
        lagrange: "Lagrange",
        newton: "Newton",
        splines: "Splines"
    };

    Object.entries(nombres).forEach(([clave, nombre]) => {
        const metrica = metricas[clave];

        texto(
            "rmse" + nombre,
            metrica ? numero(metrica.rmse, 8) : "Sin referencia"
        );

        texto(
            "mae" + nombre,
            metrica
                ? (
                    "MAE: " + numero(metrica.mae, 8) +
                    " | Error relativo: " +
                    (
                        metrica.error_porcentual_medio !== null &&
                        metrica.error_porcentual_medio !== undefined
                            ? numero(metrica.error_porcentual_medio, 4) + "%"
                            : "No definido"
                    )
                )
                : "MAE: —"
        );
    });

    // ==============================================
    // CONCLUSIONES
    // ==============================================

    const conclusiones = datos.conclusiones || {};

    texto(
        "conclusionNumerica",
        conclusiones.numerica ||
        "No hay conclusión numérica disponible."
    );

    texto(
        "conclusionProblema",
        conclusiones.problema ||
        "No hay conclusión del problema disponible."
    );

    // ==============================================
    // ANÁLISIS DE MAL CONDICIONAMIENTO
    // ==============================================

    const analisis =
        datos.analisis_mal_condicionado ||
        datos.datos_entrada?.analisis_mal_condicionado;

    if (existe("analisisMalCondicionado")) {

        if (analisis) {
            $("analisisMalCondicionado").innerHTML = `
                <p>
                    <strong>Función:</strong>
                    ${htmlSeguro(analisis.funcion)}
                </p>

                <p>
                    <strong>Cantidad de nodos:</strong>
                    ${numero(analisis.cantidad_nodos, 0)}
                </p>

                <p>
                    <strong>Error máximo con nodos equidistantes:</strong>
                    ${numero(analisis.error_maximo_equidistante, 10)}
                </p>

                <p>
                    <strong>Error máximo con nodos de Chebyshev:</strong>
                    ${numero(analisis.error_maximo_chebyshev, 10)}
                </p>

                <p>
                    <strong>Perturbación de entrada:</strong>
                    ${numero(analisis.perturbacion_maxima_entrada, 12)}
                </p>

                <p>
                    <strong>Cambio máximo de salida:</strong>
                    ${numero(analisis.cambio_maximo_salida, 12)}
                </p>

                <p>
                    <strong>Factor de amplificación:</strong>
                    ${numero(analisis.factor_amplificacion, 8)}
                </p>
            `;
        } else {
            $("analisisMalCondicionado").textContent =
                "Este escenario no incluye un análisis de mal condicionamiento.";
        }
    }


    mostrarTablaResultados(filas);

    const puntosGrafica =
        datos.datos_entrada?.puntos_conocidos ||
        senalActual.puntos.map(p => ({
            tiempo: Number(p.tiempo),
            valor: Number(p.valor)
        }));

    mostrarGraficaReconstruccion(
        puntosGrafica,
        filas,
        curvas
    );

    mostrarGraficaErrores(filas);
}

function mostrarTablaResultados(filas) {
    if (!existe("tablaResultados")) return;

    if (!filas.length) {
        $("tablaResultados").innerHTML =
            '<tr><td colspan="8">No hay resultados para mostrar.</td></tr>';
        return;
    }

    $("tablaResultados").innerHTML = filas.map(fila => `
        <tr>
            <td>${numero(fila.tiempo)}</td>
            <td>${numero(fila.real)}</td>
            <td>${numero(fila.lagrange)}</td>
            <td>${numero(fila.newton)}</td>
            <td>${numero(fila.splines)}</td>
            <td>${numero(fila.error_lagrange)}</td>
            <td>${numero(fila.error_newton)}</td>
            <td>${numero(fila.error_splines)}</td>
        </tr>
    `).join("");
}


// ======================================================
// GRAFICA DE RECONSTRUCCION
// ======================================================

function mostrarGraficaReconstruccion(puntos, filas, curvas) {
    if (!existe("graficaReconstruccion") || typeof Chart === "undefined") {
        return;
    }

    destruirGrafica("reconstruccion");

    const conocidos = puntos.map(p => ({
        x: Number(p.tiempo),
        y: Number(p.valor)
    }));

    const reales = filas
        .filter(f => f.real !== undefined && f.real !== null)
        .map(f => ({
            x: Number(f.tiempo),
            y: Number(f.real)
        }));

    const crearCurva = clave => {
        if (!curvas[clave]) return [];

        return curvas[clave].x.map((x, i) => ({
            x: Number(x),
            y: Number(curvas[clave].y[i])
        }));
    };

    graficaReconstruccion = new Chart(
        $("graficaReconstruccion"),
        {
            type: "scatter",
            data: {
                datasets: [
                    {
                        label: "Mediciones conocidas",
                        data: conocidos,
                        showLine: false,
                        pointRadius: 5,
                        backgroundColor: "#2563eb"
                    },
                    {
                        label: "Valores reales de referencia",
                        data: reales,
                        showLine: false,
                        pointRadius: 7,
                        backgroundColor: "#16a34a"
                    },
                    {
                        label: "Lagrange",
                        data: crearCurva("lagrange"),
                        showLine: true,
                        pointRadius: 0,
                        borderColor: "#2563eb",
                        borderWidth: 2
                    },
                    {
                        label: "Newton",
                        data: crearCurva("newton"),
                        showLine: true,
                        pointRadius: 0,
                        borderColor: "#9333ea",
                        borderWidth: 2
                    },
                    {
                        label: "Splines cúbicos",
                        data: crearCurva("splines"),
                        showLine: true,
                        pointRadius: 0,
                        borderColor: "#ea580c",
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                parsing: false,
                interaction: {
                    intersect: false,
                    mode: "nearest"
                },
                plugins: {
                    legend: {
                        position: "bottom"
                    },
                    tooltip: {
                        callbacks: {
                            label: contexto =>
                                `t=${numero(contexto.parsed.x)} | y=${numero(contexto.parsed.y)}`
                        }
                    }
                },
                scales: {
                    x: {
                        type: "linear",
                        title: {
                            display: true,
                            text: "Tiempo"
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Valor de la señal"
                        }
                    }
                }
            }
        }
    );
}


// ======================================================
// GRAFICA DE ERRORES
// ======================================================

function mostrarGraficaErrores(filas) {
    if (!existe("graficaErrores") || typeof Chart === "undefined") {
        return;
    }

    destruirGrafica("errores");

    const conReferencias = filas.filter(
        fila => fila.error_lagrange !== undefined
    );

    if (!conReferencias.length) {
        return;
    }

    graficaErrores = new Chart($("graficaErrores"), {
        type: "bar",
        data: {
            labels: conReferencias.map(f => "t = " + f.tiempo),
            datasets: [
                {
                    label: "Lagrange",
                    data: conReferencias.map(f => f.error_lagrange),
                    backgroundColor: "#2563eb"
                },
                {
                    label: "Newton",
                    data: conReferencias.map(f => f.error_newton),
                    backgroundColor: "#9333ea"
                },
                {
                    label: "Splines",
                    data: conReferencias.map(f => f.error_splines),
                    backgroundColor: "#ea580c"
                }
            ]
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
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Error absoluto"
                    }
                }
            }
        }
    });
}


// ======================================================
// HISTORIAL
// ======================================================

async function cargarHistorial() {
    const datos = await consultarAPI(
        "/api/sensores/historial?limite=50"
    );

    const historial = datos.historial || [];

    if (!existe("tablaHistorial")) return historial;

    const tabla = $("tablaHistorial");

    if (!historial.length) {
        tabla.innerHTML =
            '<tr><td colspan="6">No hay reconstrucciones guardadas.</td></tr>';
        return historial;
    }

    tabla.innerHTML = historial.map(item => `
        <tr>
            <td>${item.id}</td>
            <td>${htmlSeguro(item.sensor)}</td>
            <td>${htmlSeguro(item.senal)}</td>
            <td>${item.fecha ? new Date(item.fecha).toLocaleString() : "—"}</td>
            <td>
                <span class="estado-etiqueta">
                    ${htmlSeguro(item.estado)}
                </span>
            </td>
            <td>
                <div class="acciones-historial">
                    <button class="boton-tabla"
                            data-reconstruccion="${item.id}">
                        Ver detalle
                    </button>

                    <button class="boton-tabla boton-repetir"
                            data-repetir="${item.id}">
                        Repetir
                    </button>
                </div>
            </td>
        </tr>
    `).join("");

    tabla.querySelectorAll("[data-reconstruccion]").forEach(boton => {
        boton.addEventListener("click", () => {
            consultarDetalleHistorial(boton.dataset.reconstruccion);
        });
    });
    tabla.querySelectorAll("[data-repetir]").forEach(boton => {
        boton.addEventListener("click", async () => {
            await repetirReconstruccion(
                boton.dataset.repetir
            );
        });
    });
    return historial;
}

async function consultarDetalleHistorial(id) {
    try {
        const datos = await consultarAPI(
            `/api/sensores/reconstruccion/${encodeURIComponent(id)}`
        );

        const r = datos.reconstruccion;

        if (!existe("detalleHistorial")) return;

        $("detalleHistorial").innerHTML = `
            <h3>Reconstrucción #${r.id}</h3>
            <p><strong>Señal:</strong> ${htmlSeguro(r.senal)}</p>
            <p><strong>Estado:</strong> ${htmlSeguro(r.estado)}</p>
            <p><strong>Fecha:</strong>
                ${r.fecha ? new Date(r.fecha).toLocaleString() : "—"}
            </p>

            <h4>Parámetros utilizados</h4>
            <pre>${htmlSeguro(JSON.stringify(r.parametros, null, 2))}</pre>

            <h4>Métricas guardadas</h4>
            <pre>${htmlSeguro(JSON.stringify(r.metricas, null, 2))}</pre>

            <h4>Detalles por método</h4>
            <pre>${htmlSeguro(JSON.stringify(r.detalles, null, 2))}</pre>
        `;

    } catch (error) {
        texto("detalleHistorial", error.message);
    }
}


async function repetirReconstruccion(id) {
    try {
        const confirmar = confirm(
            "¿Deseas repetir esta reconstrucción con los mismos parámetros?"
        );

        if (!confirmar) return;

        texto(
            "detalleHistorial",
            "Repitiendo reconstrucción..."
        );

        const datos = await consultarAPI(
            `/api/sensores/reconstruccion/${encodeURIComponent(id)}/repetir`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            }
        );

        ultimoResultado = datos;

        mostrarResultados(datos);

        navegarA("resultados");

        texto(
            "estadoReconstruccion",
            "Reconstrucción repetida y guardada correctamente. " +
            "Nuevo ID: " + datos.reconstruccion_id
        );

        if (existe("estadoReconstruccion")) {
            $("estadoReconstruccion").className = "mensaje correcto";
        }

        await cargarHistorial();
        await actualizarDashboard();

    } catch (error) {
        texto(
            "detalleHistorial",
            "No se pudo repetir la reconstrucción: " + error.message
        );
    }
}


// ======================================================
// DASHBOARD
// ======================================================

async function contarSenales() {
    let total = 0;

    for (const sensor of sensores) {
        try {
            const datos = await consultarAPI(
                `/api/sensores/senales/${sensor.id}`
            );

            total += (datos.senales || []).length;

        } catch (error) {
            console.error("No se pudieron contar las señales:", error);
        }
    }

    return total;
}

function dibujarGraficaDashboard(historial) {
    if (!existe("graficaDashboard") || typeof Chart === "undefined") {
        return;
    }

    destruirGrafica("dashboard");

    const acumulados = {
        lagrange: [],
        newton: [],
        splines: []
    };

    historial.forEach(item => {
        const metricas = item.metricas || {};

        ["lagrange", "newton", "splines"].forEach(metodo => {
            const m = metricas[metodo];

            if (m && Number.isFinite(Number(m.rmse))) {
                acumulados[metodo].push(Number(m.rmse));
            }
        });
    });

    const promedio = valores => valores.length
        ? valores.reduce((a, b) => a + b, 0) / valores.length
        : 0;

    graficaDashboard = new Chart($("graficaDashboard"), {
        type: "bar",
        data: {
            labels: ["Lagrange", "Newton", "Splines"],
            datasets: [{
                label: "RMSE promedio",
                data: [
                    promedio(acumulados.lagrange),
                    promedio(acumulados.newton),
                    promedio(acumulados.splines)
                ],
                backgroundColor: ["#2563eb", "#9333ea", "#ea580c"],
                borderRadius: 7
            }]
        },
        options: {
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
        }
    });
}

async function actualizarDashboard() {
    const datos = await consultarAPI(
        "/api/sensores/historial?limite=50"
    );

    const historial = datos.historial || [];

    texto("totalSensores", sensores.length);

    const totalSenales = await contarSenales();

    texto("totalSenales", totalSenales);
    texto("totalReconstrucciones", historial.length);

    texto(
        "ultimoEstado",
        historial.length ? historial[0].estado : "Sin datos"
    );

    if (existe("tablaRecientes")) {
        const tabla = $("tablaRecientes");

        if (!historial.length) {
            tabla.innerHTML =
                '<tr><td colspan="5">No hay reconstrucciones registradas.</td></tr>';
        } else {
            tabla.innerHTML = historial.slice(0, 5).map(item => `
                <tr>
                    <td>${item.id}</td>
                    <td>${htmlSeguro(item.sensor)}</td>
                    <td>${htmlSeguro(item.senal)}</td>
                    <td>${htmlSeguro(item.estado)}</td>
                    <td>
                        ${item.fecha
                            ? new Date(item.fecha).toLocaleDateString()
                            : "—"}
                    </td>
                </tr>
            `).join("");
        }
    }

    dibujarGraficaDashboard(historial);
}


// ======================================================
// INICIALIZACION
// ======================================================

async function iniciarDashboard() {
    configurarNavegacion();

    if (existe("formSensor")) {
        $("formSensor").addEventListener("submit", registrarSensor);
    }

    if (existe("formSenal")) {
        $("formSenal").addEventListener("submit", registrarSenal);
    }

    if (existe("sensorConsultaSenales")) {
        $("sensorConsultaSenales").addEventListener(
            "change",
            consultarSenalesPanel
        );
    }

    if (existe("sensorReconstruccion")) {
        $("sensorReconstruccion").addEventListener(
            "change",
            cambioSensorReconstruccion
        );
    }

    if (existe("senalReconstruccion")) {
        $("senalReconstruccion").addEventListener(
            "change",
            cambioSenalReconstruccion
        );
    }

    if (existe("ejecutarReconstruccion")) {
        $("ejecutarReconstruccion").addEventListener(
            "click",
            ejecutarReconstruccion
        );
    }

    if (existe("recargarSensores")) {
        $("recargarSensores").addEventListener("click", async () => {
            try {
                await cargarSensores();
                await actualizarDashboard();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    if (existe("actualizarDashboard")) {
        $("actualizarDashboard").addEventListener("click", async () => {
            try {
                await cargarSensores();
                await actualizarDashboard();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    if (existe("actualizarHistorial")) {
        $("actualizarHistorial").addEventListener("click", async () => {
            try {
                await cargarHistorial();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    try {
        await cargarSensores();
        await cargarEscenarios();
        await cargarHistorial();
        await actualizarDashboard();

        console.log("Módulo de sensores iniciado correctamente.");

    } catch (error) {
        console.error(error);
        alert("Error al iniciar el dashboard: " + error.message);
    }
}

document.addEventListener("DOMContentLoaded", iniciarDashboard);
