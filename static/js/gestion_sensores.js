
"use strict";

const $ = (id) => document.getElementById(id);

let sensoresCargados = [];

async function solicitarAPI(url, opciones = {}) {
    const respuesta = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(opciones.headers || {})
        },
        ...opciones
    });

    const datos = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok || datos.exito === false) {
        throw new Error(
            datos.error || `Error HTTP ${respuesta.status}`
        );
    }

    return datos;
}

function mostrarMensaje(elemento, mensaje, tipo = "") {
    elemento.textContent = mensaje;
    elemento.className = "mensaje";

    if (tipo) {
        elemento.classList.add(tipo);
    }
}

function escaparHTML(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, caracter => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[caracter]);
}

function limpiarFormulario() {
    $("formSensor").reset();
    $("sensorId").value = "";
    $("tituloFormulario").textContent = "Registrar nuevo sensor";
    $("btnGuardar").textContent = "Registrar sensor";
    $("btnCancelar").hidden = true;
    mostrarMensaje($("mensajeFormulario"), "");
}

function obtenerDatosFormulario() {
    return {
        codigo: $("codigo").value.trim(),
        nombre: $("nombre").value.trim(),
        tipo: $("tipo").value.trim(),
        ubicacion: $("ubicacion").value.trim(),
        unidad_medida: $("unidad").value.trim(),
        descripcion: $("descripcion").value.trim()
    };
}

function validarFormulario(datos) {
    if (!datos.codigo || !datos.nombre || !datos.unidad_medida) {
        throw new Error(
            "Código, nombre y unidad de medida son obligatorios."
        );
    }

    if (datos.codigo.length > 50) {
        throw new Error("El código no puede superar 50 caracteres.");
    }

    if (datos.nombre.length > 100) {
        throw new Error("El nombre no puede superar 100 caracteres.");
    }

    if (datos.unidad_medida.length > 30) {
        throw new Error("La unidad de medida no puede superar 30 caracteres.");
    }
}

async function cargarSensores() {
    const tabla = $("tablaSensores");
    tabla.innerHTML = `
        <tr><td colspan="7">Cargando sensores...</td></tr>
    `;

    try {
        const datos = await solicitarAPI("/api/sensores/listar");
        sensoresCargados = datos.sensores || [];

        renderizarSensores();
        actualizarResumen();

        mostrarMensaje(
            $("estadoLista"),
            `${sensoresCargados.length} sensor(es) consultado(s).`,
            "correcto"
        );
    } catch (error) {
        tabla.innerHTML = `
            <tr><td colspan="7">No se pudieron cargar los sensores.</td></tr>
        `;

        mostrarMensaje(
            $("estadoLista"),
            error.message,
            "error"
        );
    }
}

function actualizarResumen() {
    const activos = sensoresCargados.filter(sensor => sensor.activo).length;
    const inactivos = sensoresCargados.length - activos;

    $("totalSensores").textContent = sensoresCargados.length;
    $("sensoresActivos").textContent = activos;
    $("sensoresInactivos").textContent = inactivos;
}

function renderizarSensores() {
    const tabla = $("tablaSensores");
    tabla.innerHTML = "";

    if (sensoresCargados.length === 0) {
        tabla.innerHTML = `
            <tr>
                <td colspan="7">
                    Todavía no hay sensores registrados.
                </td>
            </tr>
        `;
        return;
    }

    sensoresCargados.forEach(sensor => {
        const fila = document.createElement("tr");

        const estado = sensor.activo
            ? '<span class="estado-etiqueta estado-activo">Activo</span>'
            : '<span class="estado-etiqueta estado-inactivo">Inactivo</span>';

        fila.innerHTML = `
            <td>${escaparHTML(sensor.codigo)}</td>
            <td>${escaparHTML(sensor.nombre)}</td>
            <td>${escaparHTML(sensor.tipo || "No especificado")}</td>
            <td>${escaparHTML(sensor.ubicacion || "No especificada")}</td>
            <td>${escaparHTML(sensor.unidad_medida)}</td>
            <td>${estado}</td>
            <td>
                <button type="button"
                        class="boton-accion boton-editar"
                        data-accion="editar"
                        data-id="${sensor.id}">
                    Editar
                </button>
                <button type="button"
                        class="boton-accion boton-estado"
                        data-accion="estado"
                        data-id="${sensor.id}"
                        data-activo="${sensor.activo ? "true" : "false"}">
                    ${sensor.activo ? "Desactivar" : "Activar"}
                </button>
            </td>
        `;

        tabla.appendChild(fila);
    });
}

function prepararEdicion(sensorId) {
    const sensor = sensoresCargados.find(
        item => Number(item.id) === Number(sensorId)
    );

    if (!sensor) {
        mostrarMensaje(
            $("mensajeFormulario"),
            "No se encontró el sensor seleccionado.",
            "error"
        );
        return;
    }

    $("sensorId").value = sensor.id;
    $("codigo").value = sensor.codigo || "";
    $("nombre").value = sensor.nombre || "";
    $("tipo").value = sensor.tipo || "";
    $("ubicacion").value = sensor.ubicacion || "";
    $("unidad").value = sensor.unidad_medida || "";
    $("descripcion").value = sensor.descripcion || "";

    $("tituloFormulario").textContent = "Editar sensor";
    $("btnGuardar").textContent = "Guardar cambios";
    $("btnCancelar").hidden = false;

    mostrarMensaje(
        $("mensajeFormulario"),
        `Editando el sensor ${sensor.codigo}.`
    );

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

async function guardarSensor(evento) {
    evento.preventDefault();

    const boton = $("btnGuardar");
    const sensorId = $("sensorId").value;
    const datos = obtenerDatosFormulario();

    try {
        validarFormulario(datos);

        boton.disabled = true;
        boton.textContent = "Guardando...";

        if (sensorId) {
            await solicitarAPI(`/api/sensores/${sensorId}`, {
                method: "PUT",
                body: JSON.stringify(datos)
            });

            mostrarMensaje(
                $("mensajeFormulario"),
                "Sensor actualizado correctamente.",
                "correcto"
            );
        } else {
            await solicitarAPI("/api/sensores/registrar", {
                method: "POST",
                body: JSON.stringify(datos)
            });

            mostrarMensaje(
                $("mensajeFormulario"),
                "Sensor registrado correctamente.",
                "correcto"
            );
        }

        limpiarFormulario();
        await cargarSensores();

    } catch (error) {
        mostrarMensaje(
            $("mensajeFormulario"),
            error.message,
            "error"
        );
    } finally {
        boton.disabled = false;
        boton.textContent = $("sensorId").value
            ? "Guardar cambios"
            : "Registrar sensor";
    }
}

async function cambiarEstado(sensorId, estadoActual) {
    const nuevoEstado = !estadoActual;
    const accion = nuevoEstado ? "activar" : "desactivar";

    const confirmado = window.confirm(
        `¿Estás seguro de que deseas ${accion} este sensor?`
    );

    if (!confirmado) {
        return;
    }

    try {
        await solicitarAPI(`/api/sensores/${sensorId}/estado`, {
            method: "PATCH",
            body: JSON.stringify({
                activo: nuevoEstado
            })
        });

        await cargarSensores();

        mostrarMensaje(
            $("estadoLista"),
            `Sensor ${nuevoEstado ? "activado" : "desactivado"} correctamente.`,
            "correcto"
        );
    } catch (error) {
        mostrarMensaje(
            $("estadoLista"),
            error.message,
            "error"
        );
    }
}

$("formSensor").addEventListener("submit", guardarSensor);

$("btnCancelar").addEventListener("click", limpiarFormulario);

$("btnActualizar").addEventListener("click", cargarSensores);

$("tablaSensores").addEventListener("click", evento => {
    const boton = evento.target.closest("button[data-accion]");

    if (!boton) {
        return;
    }

    const sensorId = Number(boton.dataset.id);

    if (boton.dataset.accion === "editar") {
        prepararEdicion(sensorId);
    }

    if (boton.dataset.accion === "estado") {
        cambiarEstado(
            sensorId,
            boton.dataset.activo === "true"
        );
    }
});

document.addEventListener("DOMContentLoaded", cargarSensores);
