
import math


def calcular_metricas(valores_reales, valores_estimados):
    """
    Calcula métricas de error entre valores reales y estimados.

    Incluye:
    - MAE
    - RMSE
    - Error absoluto máximo
    - Error relativo medio
    - Error porcentual medio
    - Error relativo máximo
    - Error porcentual máximo

    Los errores relativos no se calculan para referencias iguales a cero.
    """

    if len(valores_reales) != len(valores_estimados):
        raise ValueError(
            "Los valores reales y estimados deben tener igual tamaño."
        )

    if not valores_reales:
        return None

    errores_absolutos = []
    errores_relativos = []

    for real, estimado in zip(valores_reales, valores_estimados):
        real = float(real)
        estimado = float(estimado)

        if not math.isfinite(real) or not math.isfinite(estimado):
            raise ValueError(
                "Se encontraron valores no finitos."
            )

        error_absoluto = abs(real - estimado)
        errores_absolutos.append(error_absoluto)

        # El error relativo no está definido si el valor real es cero.
        if real != 0:
            error_relativo = error_absoluto / abs(real)
            errores_relativos.append(error_relativo)

    mae = sum(errores_absolutos) / len(errores_absolutos)

    rmse = math.sqrt(
        sum(error ** 2 for error in errores_absolutos)
        / len(errores_absolutos)
    )

    error_relativo_medio = (
        sum(errores_relativos) / len(errores_relativos)
        if errores_relativos else None
    )

    error_relativo_maximo = (
        max(errores_relativos)
        if errores_relativos else None
    )

    return {
        "cantidad_puntos": len(errores_absolutos),
        "mae": mae,
        "rmse": rmse,
        "error_maximo": max(errores_absolutos),

        "cantidad_puntos_relativos": len(errores_relativos),
        "cantidad_referencias_cero": (
            len(errores_absolutos) - len(errores_relativos)
        ),

        "error_relativo_medio": error_relativo_medio,
        "error_porcentual_medio": (
            error_relativo_medio * 100
            if error_relativo_medio is not None else None
        ),

        "error_relativo_maximo": error_relativo_maximo,
        "error_porcentual_maximo": (
            error_relativo_maximo * 100
            if error_relativo_maximo is not None else None
        )
    }


def calcular_metricas_metodos(valores_reales, resultados):
    """
    Calcula las métricas para Lagrange, Newton y splines.

    Si no existen referencias reales, devuelve un diccionario vacío.
    """

    if valores_reales is None:
        return {}

    return {
        metodo: calcular_metricas(valores_reales, valores)
        for metodo, valores in resultados.items()
    }
