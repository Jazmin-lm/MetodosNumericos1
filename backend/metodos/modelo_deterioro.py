
import numpy as np


def validar_mediciones(tiempos, deterioros):
    """
    Comprueba que existan suficientes mediciones válidas
    para construir un modelo cuadrático.
    """

    if len(tiempos) != len(deterioros):
        raise ValueError(
            "Los tiempos y deterioros deben tener la misma cantidad de datos."
        )

    if len(tiempos) < 3:
        raise ValueError(
            "Se necesitan al menos 3 mediciones para ajustar un modelo cuadrático."
        )

    tiempos = np.asarray(tiempos, dtype=float)
    deterioros = np.asarray(deterioros, dtype=float)

    if not np.all(np.isfinite(tiempos)):
        raise ValueError("Los tiempos contienen valores inválidos.")

    if not np.all(np.isfinite(deterioros)):
        raise ValueError("Los deterioros contienen valores inválidos.")

    if len(np.unique(tiempos)) < 3:
        raise ValueError(
            "Se necesitan al menos 3 tiempos diferentes."
        )

    return tiempos, deterioros


def ajustar_modelo_cuadratico(tiempos, deterioros):
    """
    Ajusta el modelo:

        D(t) = D0 + alpha*t + beta*t^2

    utilizando mínimos cuadrados.
    """

    tiempos, deterioros = validar_mediciones(
        tiempos,
        deterioros
    )

    # Matriz del modelo cuadrático
    matriz = np.column_stack([
        np.ones(len(tiempos)),
        tiempos,
        tiempos ** 2
    ])

    # Comprobar que el ajuste sea posible
    if np.linalg.matrix_rank(matriz) < 3:
        raise ValueError(
            "Las mediciones no permiten construir un modelo cuadrático."
        )

    # Calcular coeficientes por mínimos cuadrados
    coeficientes, _, _, _ = np.linalg.lstsq(
        matriz,
        deterioros,
        rcond=None
    )

    D0, alpha, beta = coeficientes

    if not np.all(np.isfinite(coeficientes)):
        raise ValueError(
            "No fue posible obtener coeficientes válidos."
        )

    # Valores estimados por el modelo
    estimaciones = matriz @ coeficientes

    # Error cuadrático medio
    error_cuadratico = float(
        np.mean((deterioros - estimaciones) ** 2)
    )

    # Función de deterioro
    def funcion(t):
        return D0 + alpha * t + beta * t ** 2

    # Derivada de la función
    def derivada(t):
        return alpha + 2 * beta * t

    return {
        "D0": float(D0),
        "alpha": float(alpha),
        "beta": float(beta),
        "modelo": "D(t) = D0 + alpha*t + beta*t^2",
        "error_cuadratico": error_cuadratico,
        "tiempo_minimo": float(np.min(tiempos)),
        "tiempo_maximo": float(np.max(tiempos)),
        "valores_estimados": estimaciones.tolist(),
        "funcion": funcion,
        "derivada": derivada
    }
