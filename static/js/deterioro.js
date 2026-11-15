
const escenarios = {
    normal: {
        d0: 5, a: 0.8, b: 0.04, dlim: 25,
        t1: 1, t2: 2, t3: 3,
        descripcion: "Condiciones habituales de deterioro."
    },
    estres: {
        d0: 5, a: 1.4, b: 0.08, dlim: 22,
        t1: 1, t2: 2, t3: 3,
        descripcion: "Condiciones exigentes de funcionamiento."
    },
    mal: {
        d0: 5, a: 0.8, b: 0.04, dlim: 25,
        t1: 1, t2: 1.01, t3: 1.02,
        descripcion: "Observaciones muy cercanas entre sí; pueden generar sensibilidad en la calibración."
    }
};

let escenarioActual = "normal";

function cargarEscenario(nombre) {
    const e = escenarios[nombre];
    if (!e) return;

    escenarioActual = nombre;

    document.getElementById("d0").value = e.d0;
    document.getElementById("a").value = e.a;
    document.getElementById("b").value = e.b;
    document.getElementById("dlim").value = e.dlim;
    document.getElementById("t1").value = e.t1;
    document.getElementById("t2").value = e.t2;
    document.getElementById("t3").value = e.t3;

    document.getElementById("descripcion-escenario").textContent =
        e.descripcion;

    document.querySelectorAll(".boton-escenario").forEach(boton => {
        boton.classList.toggle(
            "activo",
            boton.dataset.escenario === nombre
        );
    });
}

document.querySelectorAll(".boton-escenario").forEach(boton => {
    boton.addEventListener("click", () => {
        cargarEscenario(boton.dataset.escenario);
    });
});

document.getElementById("ejecutar").addEventListener("click", async () => {
    const estado = document.getElementById("estado-resultados");
    const solucion = document.getElementById("solucion");
    const error = document.getElementById("error");
    const residual = document.getElementById("residual");

    try {
        const coeficientes = [...document.querySelectorAll(".coeficiente")];
        const independientes = [...document.querySelectorAll(".independiente")];

        const A = [];
        for (let i = 0; i < 3; i++) {
            A.push(
                coeficientes.slice(i * 3, i * 3 + 3)
                    .map(input => Number(input.value))
            );
        }

        const b = independientes.map(input => Number(input.value));

        const tolerancia = Number(document.getElementById("tolerancia").value);
        const max_iter = Number(document.getElementById("iteraciones").value);
        const x0 = Number(document.getElementById("x0").value);

        if (
            [...A.flat(), ...b, tolerancia, max_iter, x0].some(v => !Number.isFinite(v)) ||
            tolerancia <= 0 || max_iter < 1
        ) {
            throw new Error("Revisa los valores ingresados. Deben ser números válidos.");
        }

        estado.textContent = "Calculando métodos...";
        solucion.textContent = "Procesando...";
        error.textContent = "Procesando...";
        residual.textContent = "Procesando...";

        const respuesta = await fetch("/ejecutar-sistema", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                A,
                b,
                tolerancia,
                max_iter,
                x0
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.exito) {
            throw new Error(datos.error || "No se pudo ejecutar el cálculo.");
        }

        const resultados = datos.resultados;

        solucion.innerHTML = "";
        error.innerHTML = "";
        residual.innerHTML = "";

        let tabla = `
            <h3>Resultados de los métodos</h3>
            <div class="tabla-resultados">
            <table>
                <thead>
                    <tr>
                        <th>Método</th>
                        <th>Solución (x, y, z)</th>
                        <th>Iteraciones</th>
                        <th>Error</th>
                        <th>Residual</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const [nombre, r] of Object.entries(resultados)) {
            const valores = r.solucion.map(v => Number(v).toFixed(6)).join(", ");
            const iter = r.iteraciones ?? "—";
            const err = r.error !== undefined ? Number(r.error).toExponential(3) : "—";
            const res = Number(r.residual).toExponential(3);

            tabla += `
                <tr>
                    <td>${nombre}</td>
                    <td>${valores}</td>
                    <td>${iter}</td>
                    <td>${err}</td>
                    <td>${res}</td>
                </tr>
            `;
        }

        tabla += "</tbody></table></div>";

        estado.innerHTML = tabla;

        const referencia = resultados["Referencia directa"];
        solucion.textContent = referencia.solucion
            .map(v => v.toFixed(6)).join(", ");

        error.textContent = "Consulta la tabla de resultados";
        residual.textContent = Number(referencia.residual).toExponential(3);

    } catch (e) {
        estado.textContent = "No se pudo completar el cálculo: " + e.message;
        solucion.textContent = "—";
        error.textContent = "—";
        residual.textContent = "—";
    }
});

cargarEscenario("normal");
