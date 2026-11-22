
import math


# ==========================================
# VALIDACIONES GENERALES
# ==========================================

def validar_parametros(tolerancia, max_iter):
    if not isinstance(tolerancia, (int, float)):
        raise ValueError("La tolerancia debe ser numérica.")

    if not math.isfinite(tolerancia) or tolerancia <= 0:
        raise ValueError("La tolerancia debe ser positiva y finita.")

    if not isinstance(max_iter, int) or isinstance(max_iter, bool):
        raise ValueError("El máximo de iteraciones debe ser entero.")

    if max_iter < 1:
        raise ValueError("El máximo de iteraciones debe ser mayor que cero.")


def validar_funcion(f):
    if not callable(f):
        raise ValueError("Debe proporcionarse una función válida.")


def evaluar_funcion(f, x):
    resultado = f(x)

    if not isinstance(resultado, (int, float)):
        raise ValueError("La función debe devolver un valor numérico.")

    if not math.isfinite(resultado):
        raise ValueError("La función produjo un resultado no finito.")

    return float(resultado)


def validar_numero(valor, nombre):
    if not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser numérico.")

    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito.")


# ==========================================
# ESTRUCTURA DE RESULTADOS
# ==========================================

def crear_resultado(
    solucion=None,
    convergio=False,
    iteraciones=0,
    error_abs=None,
    error_rel=None,
    residual=None,
    historial=None,
    mensaje=""
):
    return {
        "solucion": solucion,
        "convergio": convergio,
        "iteraciones": iteraciones,
        "error_abs": error_abs,
        "error_rel": error_rel,
        "residual": residual,
        "historial": historial or [],
        "mensaje": mensaje
    }


def registrar_iteracion(
    historial,
    iteracion,
    aproximacion,
    error_abs,
    error_rel,
    residual
):
    historial.append({
        "iteracion": iteracion,
        "aproximacion": aproximacion,
        "error_abs": error_abs,
        "error_rel": error_rel,
        "residual": residual
    })


# ==========================================
# 1. MÉTODO DE BISECCIÓN
# ==========================================

def metodo_biseccion(f, a, b, tolerancia=1e-6, max_iter=100):

    validar_funcion(f)
    validar_parametros(tolerancia, max_iter)
    validar_numero(a, "El extremo a")
    validar_numero(b, "El extremo b")

    if a >= b:
        raise ValueError("El extremo a debe ser menor que b.")

    fa = evaluar_funcion(f, a)
    fb = evaluar_funcion(f, b)

    historial = []

    if fa == 0:
        registrar_iteracion(historial, 0, a, 0.0, 0.0, 0.0)
        return crear_resultado(
            a, True, 0, 0.0, 0.0, 0.0,
            historial, "La raíz coincide con el extremo a."
        )

    if fb == 0:
        registrar_iteracion(historial, 0, b, 0.0, 0.0, 0.0)
        return crear_resultado(
            b, True, 0, 0.0, 0.0, 0.0,
            historial, "La raíz coincide con el extremo b."
        )

    if fa * fb > 0:
        raise ValueError(
            "El intervalo no presenta un cambio de signo. "
            "No se puede garantizar una raíz mediante bisección."
        )

    anterior = None

    for k in range(1, max_iter + 1):

        medio = (a + b) / 2
        fm = evaluar_funcion(f, medio)

        error_abs = (
            abs(medio - anterior)
            if anterior is not None else None
        )

        error_rel = (
            error_abs / abs(medio)
            if error_abs is not None and medio != 0 else None
        )

        residual = abs(fm)

        registrar_iteracion(
            historial, k, medio,
            error_abs, error_rel, residual
        )

        if residual <= tolerancia or (b - a) / 2 <= tolerancia:
            return crear_resultado(
                medio, True, k, error_abs,
                error_rel, residual, historial,
                "El método de bisección convergió."
            )

        if fa * fm < 0:
            b = medio
            fb = fm
        else:
            a = medio
            fa = fm

        anterior = medio

    ultimo = historial[-1]

    return crear_resultado(
        ultimo["aproximacion"],
        False,
        max_iter,
        ultimo["error_abs"],
        ultimo["error_rel"],
        ultimo["residual"],
        historial,
        "Se alcanzó el máximo de iteraciones sin converger."
    )


# ==========================================
# 2. MÉTODO DE NEWTON-RAPHSON
# ==========================================

def metodo_newton_raphson(
    f,
    df,
    x0,
    tolerancia=1e-6,
    max_iter=100
):

    validar_funcion(f)
    validar_funcion(df)
    validar_parametros(tolerancia, max_iter)
    validar_numero(x0, "La aproximación inicial")

    historial = []
    x = float(x0)

    fx = evaluar_funcion(f, x)

    if abs(fx) <= tolerancia:
        registrar_iteracion(historial, 0, x, 0.0, 0.0, abs(fx))
        return crear_resultado(
            x, True, 0, 0.0, 0.0, abs(fx),
            historial, "La aproximación inicial ya es una raíz."
        )

    for k in range(1, max_iter + 1):

        derivada = evaluar_funcion(df, x)

        if abs(derivada) < 1e-14:
            return crear_resultado(
                x, False, k - 1,
                residual=abs(fx),
                historial=historial,
                mensaje="La derivada es cero o demasiado pequeña."
            )

        nuevo = x - fx / derivada
        validar_numero(nuevo, "La nueva aproximación")

        f_nuevo = evaluar_funcion(f, nuevo)

        error_abs = abs(nuevo - x)

        error_rel = (
            error_abs / abs(nuevo)
            if nuevo != 0 else None
        )

        residual = abs(f_nuevo)

        registrar_iteracion(
            historial, k, nuevo,
            error_abs, error_rel, residual
        )

        if residual <= tolerancia:
            return crear_resultado(
                nuevo, True, k,
                error_abs, error_rel, residual,
                historial,
                "El método de Newton-Raphson convergió."
            )

        x = nuevo
        fx = f_nuevo

    ultimo = historial[-1]

    return crear_resultado(
        ultimo["aproximacion"],
        False,
        max_iter,
        ultimo["error_abs"],
        ultimo["error_rel"],
        ultimo["residual"],
        historial,
        "Se alcanzó el máximo de iteraciones sin converger."
    )


# ==========================================
# 3. MÉTODO DE LA SECANTE
# ==========================================

def metodo_secante(
    f,
    x0,
    x1,
    tolerancia=1e-6,
    max_iter=100
):

    validar_funcion(f)
    validar_parametros(tolerancia, max_iter)
    validar_numero(x0, "La primera aproximación")
    validar_numero(x1, "La segunda aproximación")

    if x0 == x1:
        raise ValueError(
            "Las aproximaciones iniciales deben ser diferentes."
        )

    historial = []

    x_anterior = float(x0)
    x_actual = float(x1)

    f_anterior = evaluar_funcion(f, x_anterior)
    f_actual = evaluar_funcion(f, x_actual)

    if abs(f_anterior) <= tolerancia:
        registrar_iteracion(
            historial, 0, x_anterior, 0.0, 0.0,
            abs(f_anterior)
        )
        return crear_resultado(
            x_anterior, True, 0, 0.0, 0.0,
            abs(f_anterior), historial,
            "La primera aproximación ya es una raíz."
        )

    if abs(f_actual) <= tolerancia:
        registrar_iteracion(
            historial, 0, x_actual, 0.0, 0.0,
            abs(f_actual)
        )
        return crear_resultado(
            x_actual, True, 0, 0.0, 0.0,
            abs(f_actual), historial,
            "La segunda aproximación ya es una raíz."
        )

    for k in range(1, max_iter + 1):

        denominador = f_actual - f_anterior

        if abs(denominador) < 1e-14:
            return crear_resultado(
                x_actual, False, k - 1,
                residual=abs(f_actual),
                historial=historial,
                mensaje="El denominador es cero o demasiado pequeño."
            )

        nuevo = (
            x_actual
            - f_actual * (x_actual - x_anterior) / denominador
        )

        validar_numero(nuevo, "La nueva aproximación")

        f_nuevo = evaluar_funcion(f, nuevo)

        error_abs = abs(nuevo - x_actual)

        error_rel = (
            error_abs / abs(nuevo)
            if nuevo != 0 else None
        )

        residual = abs(f_nuevo)

        registrar_iteracion(
            historial, k, nuevo,
            error_abs, error_rel, residual
        )

        if residual <= tolerancia:
            return crear_resultado(
                nuevo, True, k,
                error_abs, error_rel, residual,
                historial,
                "El método de la secante convergió."
            )

        x_anterior = x_actual
        f_anterior = f_actual

        x_actual = nuevo
        f_actual = f_nuevo

    ultimo = historial[-1]

    return crear_resultado(
        ultimo["aproximacion"],
        False,
        max_iter,
        ultimo["error_abs"],
        ultimo["error_rel"],
        ultimo["residual"],
        historial,
        "Se alcanzó el máximo de iteraciones sin converger."
    )
