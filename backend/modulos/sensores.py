
import time

from backend.metodos.interpolacion import (
    lagrange,
    newton,
    splines_cubicos
)


def reconstruir_senal(datos):
    x = [float(v) for v in datos["x"]]
    y = [float(v) for v in datos["y"]]
    puntos = [float(v) for v in datos["puntos_evaluar"]]
    reales = datos.get("valores_reales")

    if not x or len(x) != len(y):
        raise ValueError(
            "Los tiempos y mediciones deben tener el mismo tamaño."
        )

    if len(x) < 2:
        raise ValueError(
            "Se necesitan al menos dos puntos conocidos."
        )

    if len(set(x)) != len(x):
        raise ValueError("No puede haber tiempos repetidos.")

    if not puntos:
        raise ValueError(
            "Debe ingresar al menos un punto para reconstruir."
        )

    if len(set(puntos)) != len(puntos):
        raise ValueError(
            "No puede haber tiempos de evaluación repetidos."
        )

    if any(p < min(x) or p > max(x) for p in puntos):
        raise ValueError(
            "Los puntos a reconstruir deben estar dentro del intervalo conocido."
        )

    if reales is not None and len(reales) != len(puntos):
        raise ValueError(
            "Debe haber un valor real por cada punto faltante."
        )

    # Ordenar los puntos conocidos.
    pares = sorted(zip(x, y))
    x = [p[0] for p in pares]
    y = [p[1] for p in pares]

    # Ejecutar cada método y medir su tiempo individual.
    tiempos_ms = {}

    inicio = time.perf_counter()
    valores_lagrange = lagrange(x, y, puntos)
    tiempos_ms["lagrange"] = (
        time.perf_counter() - inicio
    ) * 1000

    inicio = time.perf_counter()
    valores_newton = newton(x, y, puntos)
    tiempos_ms["newton"] = (
        time.perf_counter() - inicio
    ) * 1000

    inicio = time.perf_counter()
    valores_splines = splines_cubicos(x, y, puntos)
    tiempos_ms["splines"] = (
        time.perf_counter() - inicio
    ) * 1000

    resultados = {
        "lagrange": valores_lagrange,
        "newton": valores_newton,
        "splines": valores_splines
    }

    # Construir tabla comparativa.
    comparacion = []

    for i, tiempo in enumerate(puntos):
        fila = {
            "tiempo": tiempo,
            "lagrange": valores_lagrange[i],
            "newton": valores_newton[i],
            "splines": valores_splines[i]
        }

        if reales is not None:
            real = float(reales[i])
            fila["real"] = real

            fila["error_lagrange"] = abs(
                real - valores_lagrange[i]
            )
            fila["error_newton"] = abs(
                real - valores_newton[i]
            )
            fila["error_splines"] = abs(
                real - valores_splines[i]
            )

        comparacion.append(fila)

    # Crear puntos intermedios para dibujar las curvas.
    cantidad = 100
    minimo = x[0]
    maximo = x[-1]

    puntos_grafica = [
        minimo + i * (maximo - minimo) / (cantidad - 1)
        for i in range(cantidad)
    ]

    curvas = {
        "lagrange": {
            "x": puntos_grafica,
            "y": lagrange(x, y, puntos_grafica)
        },
        "newton": {
            "x": puntos_grafica,
            "y": newton(x, y, puntos_grafica)
        },
        "splines": {
            "x": puntos_grafica,
            "y": splines_cubicos(x, y, puntos_grafica)
        }
    }

    return {
        "resultados": resultados,
        "comparacion": comparacion,
        "curvas": curvas,
        "tiempos_ms": tiempos_ms
    }
