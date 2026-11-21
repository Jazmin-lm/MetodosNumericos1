
import math
from time import perf_counter


# =====================================================
# 1. VALIDACIÓN DE SISTEMAS
# =====================================================

def validar_sistema(A, b):
    n = len(A)

    if n == 0 or len(b) != n:
        raise ValueError("Las dimensiones de A y b no coinciden.")

    if any(len(fila) != n for fila in A):
        raise ValueError("La matriz A debe ser cuadrada.")

    for fila in A:
        for valor in fila:
            if not math.isfinite(float(valor)):
                raise ValueError("La matriz contiene valores no finitos.")

    for valor in b:
        if not math.isfinite(float(valor)):
            raise ValueError("El vector b contiene valores no finitos.")

    return True


def validar_parametros(tolerancia, max_iter):
    if not math.isfinite(tolerancia) or tolerancia <= 0:
        raise ValueError("La tolerancia debe ser positiva.")

    if not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("El máximo de iteraciones debe ser un entero positivo.")


# =====================================================
# 2. OPERACIONES MATEMÁTICAS AUXILIARES
# =====================================================

def producto_matriz_vector(A, x):
    return [
        sum(A[i][j] * x[j] for j in range(len(x)))
        for i in range(len(A))
    ]


def producto_punto(x, y):
    return sum(x[i] * y[i] for i in range(len(x)))


def norma_infinito(vector):
    return max((abs(valor) for valor in vector), default=0.0)


def residuo_vector(A, x, b):
    Ax = producto_matriz_vector(A, x)
    return [b[i] - Ax[i] for i in range(len(b))]


def calcular_residuo(A, x, b):
    return norma_infinito(residuo_vector(A, x, b))


def error_absoluto(x, referencia):
    return norma_infinito([
        x[i] - referencia[i]
        for i in range(len(x))
    ])


def error_relativo(x, referencia):
    denominador = norma_infinito(referencia)

    if denominador == 0:
        return error_absoluto(x, referencia)

    return error_absoluto(x, referencia) / denominador


def verificar_diagonal(A):
    for i in range(len(A)):
        if abs(A[i][i]) < 1e-14:
            raise ValueError(
                "La matriz tiene un elemento diagonal nulo o demasiado pequeño."
            )


# =====================================================
# 3. FACTORIZACIÓN LU CON PIVOTEO PARCIAL
# =====================================================

def factorizar_lu(A):
    n = len(A)

    U = [fila[:] for fila in A]
    L = [[0.0] * n for _ in range(n)]
    pivotes = list(range(n))

    for i in range(n):
        L[i][i] = 1.0

    for k in range(n):

        pivote = max(
            range(k, n),
            key=lambda i: abs(U[i][k])
        )

        if abs(U[pivote][k]) < 1e-14:
            raise ValueError("La matriz es singular o casi singular.")

        if pivote != k:

            U[k], U[pivote] = U[pivote], U[k]
            pivotes[k], pivotes[pivote] = pivotes[pivote], pivotes[k]

            for j in range(k):
                L[k][j], L[pivote][j] = (
                    L[pivote][j],
                    L[k][j]
                )

        for i in range(k + 1, n):

            factor = U[i][k] / U[k][k]
            L[i][k] = factor

            for j in range(k, n):
                U[i][j] -= factor * U[k][j]

    return L, U, pivotes


def resolver_lu(A, b):
    L, U, pivotes = factorizar_lu(A)
    n = len(b)

    pb = [b[pivotes[i]] for i in range(n)]

    # Sustitución hacia adelante: Ly = Pb
    y = [0.0] * n

    for i in range(n):
        y[i] = pb[i] - sum(
            L[i][j] * y[j]
            for j in range(i)
        )

    # Sustitución hacia atrás: Ux = y
    x = [0.0] * n

    for i in range(n - 1, -1, -1):

        if abs(U[i][i]) < 1e-14:
            raise ValueError("No se puede resolver el sistema mediante LU.")

        x[i] = (
            y[i] - sum(
                U[i][j] * x[j]
                for j in range(i + 1, n)
            )
        ) / U[i][i]

    return x


# =====================================================
# 4. REFERENCIA DIRECTA: ELIMINACIÓN DE GAUSS
# =====================================================

def resolver_referencia(A, b):
    M = [A[i][:] + [b[i]] for i in range(len(b))]
    n = len(b)

    for k in range(n):

        pivote = max(
            range(k, n),
            key=lambda i: abs(M[i][k])
        )

        if abs(M[pivote][k]) < 1e-14:
            raise ValueError("El sistema no tiene solución única.")

        M[k], M[pivote] = M[pivote], M[k]

        for i in range(k + 1, n):

            factor = M[i][k] / M[k][k]

            for j in range(k, n + 1):
                M[i][j] -= factor * M[k][j]

    x = [0.0] * n

    for i in range(n - 1, -1, -1):
        x[i] = (
            M[i][n] - sum(
                M[i][j] * x[j]
                for j in range(i + 1, n)
            )
        ) / M[i][i]

    return x


# =====================================================
# 5. MÉTODO DE JACOBI
# =====================================================

def resolver_jacobi(A, b, tolerancia=1e-6,
                    max_iter=100, x0=None):

    n = len(b)
    verificar_diagonal(A)

    x = list(x0) if x0 is not None else [0.0] * n
    historial = []

    escala = max(1.0, norma_infinito(b))

    for k in range(1, max_iter + 1):

        nuevo = [0.0] * n

        for i in range(n):

            suma = sum(
                A[i][j] * x[j]
                for j in range(n)
                if j != i
            )

            nuevo[i] = (b[i] - suma) / A[i][i]

        error = norma_infinito([
            nuevo[i] - x[i]
            for i in range(n)
        ])

        residual = calcular_residuo(A, nuevo, b)

        historial.append({
            "iteracion": k,
            "aproximacion": nuevo[:],
            "error": error,
            "residual": residual
        })

        x = nuevo

        if residual <= tolerancia * escala:
            return {
                "solucion": x,
                "iteraciones": k,
                "error": error,
                "convergio": True,
                "historial": historial
            }

    return {
        "solucion": x,
        "iteraciones": max_iter,
        "error": error,
        "convergio": False,
        "historial": historial
    }


# =====================================================
# 6. MÉTODO DE GAUSS-SEIDEL
# =====================================================

def resolver_gauss_seidel(A, b, tolerancia=1e-6,
                          max_iter=100, x0=None):

    n = len(b)
    verificar_diagonal(A)

    x = list(x0) if x0 is not None else [0.0] * n
    historial = []

    escala = max(1.0, norma_infinito(b))

    for k in range(1, max_iter + 1):

        anterior = x[:]

        for i in range(n):

            suma = sum(
                A[i][j] * x[j]
                for j in range(n)
                if j != i
            )

            x[i] = (b[i] - suma) / A[i][i]

        error = norma_infinito([
            x[i] - anterior[i]
            for i in range(n)
        ])

        residual = calcular_residuo(A, x, b)

        historial.append({
            "iteracion": k,
            "aproximacion": x[:],
            "error": error,
            "residual": residual
        })

        if residual <= tolerancia * escala:
            return {
                "solucion": x,
                "iteraciones": k,
                "error": error,
                "convergio": True,
                "historial": historial
            }

    return {
        "solucion": x,
        "iteraciones": max_iter,
        "error": error,
        "convergio": False,
        "historial": historial
    }


# =====================================================
# 7. VALIDACIÓN SPD
# =====================================================

def verificar_spd(A, tolerancia=1e-12):

    n = len(A)

    # Comprobar simetría
    for i in range(n):
        for j in range(n):

            if abs(A[i][j] - A[j][i]) > tolerancia:
                return False

    # Comprobar mediante factorización de Cholesky
    L = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1):

            suma = sum(
                L[i][k] * L[j][k]
                for k in range(j)
            )

            if i == j:

                valor = A[i][i] - suma

                if valor <= tolerancia:
                    return False

                L[i][j] = math.sqrt(valor)

            else:

                L[i][j] = (
                    A[i][j] - suma
                ) / L[j][j]

    return True


# =====================================================
# 8. GRADIENTE CONJUGADO
# =====================================================

def resolver_gradiente_conjugado(
    A, b, tolerancia=1e-6, max_iter=100, x0=None
):

    n = len(b)

    if not verificar_spd(A):
        raise ValueError(
            "Gradiente conjugado requiere una matriz SPD."
        )

    x = list(x0) if x0 is not None else [0.0] * n

    r = residuo_vector(A, x, b)
    p = r[:]

    rr = producto_punto(r, r)
    historial = []

    escala = max(1.0, norma_infinito(b))

    if math.sqrt(rr) <= tolerancia * escala:
        return {
            "solucion": x,
            "iteraciones": 0,
            "error": 0.0,
            "convergio": True,
            "historial": historial
        }

    for k in range(1, max_iter + 1):

        Ap = producto_matriz_vector(A, p)
        denominador = producto_punto(p, Ap)

        if denominador <= 0:
            raise ValueError(
                "Se detectó una dirección no válida para gradiente conjugado."
            )

        alfa = rr / denominador

        x = [
            x[i] + alfa * p[i]
            for i in range(n)
        ]

        r = [
            r[i] - alfa * Ap[i]
            for i in range(n)
        ]

        nuevo_rr = producto_punto(r, r)
        error = math.sqrt(nuevo_rr)
        residual = calcular_residuo(A, x, b)

        historial.append({
            "iteracion": k,
            "aproximacion": x[:],
            "error": error,
            "residual": residual
        })

        if residual <= tolerancia * escala:
            return {
                "solucion": x,
                "iteraciones": k,
                "error": error,
                "convergio": True,
                "historial": historial
            }

        if rr == 0:
            break

        beta = nuevo_rr / rr

        p = [
            r[i] + beta * p[i]
            for i in range(n)
        ]

        rr = nuevo_rr

    return {
        "solucion": x,
        "iteraciones": k,
        "error": error,
        "convergio": False,
        "historial": historial
    }


# =====================================================
# 9. NÚMERO DE CONDICIÓN
# =====================================================

def norma_matriz_infinito(A):
    return max(
        sum(abs(valor) for valor in fila)
        for fila in A
    )


def calcular_condicion(A):

    n = len(A)
    norma_A = norma_matriz_infinito(A)

    inversa = [[0.0] * n for _ in range(n)]

    for j in range(n):

        columna = [0.0] * n
        columna[j] = 1.0

        solucion = resolver_lu(A, columna)

        for i in range(n):
            inversa[i][j] = solucion[i]

    norma_inversa = norma_matriz_infinito(inversa)

    return norma_A * norma_inversa


# =====================================================
# 10. GENERACIÓN DE ESCENARIOS
# =====================================================

def generar_sistema_escenario(tipo):

    x_exacta = [1.0, 2.0, 3.0, 4.0]

    
    matrices = {

        "NORMAL": [
            [10.0, -1.0, 0.0, -1.0],
            [-1.0, 10.0, -1.0, 0.0],
            [0.0, -1.0, 10.0, -1.0],
            [-1.0, 0.0, -1.0, 10.0]
        ],

        "ESTRES": [
            [10.0, -2.0, -1.0, -1.0],
            [-2.0, 10.0, -2.0, -1.0],
            [-1.0, -2.0, 10.0, -2.0],
            [-1.0, -1.0, -2.0, 10.0]
        ],

        "MAL_CONDICIONADO": [
            [0.2525250025, 0.2475249975, 0.2524749975, 0.2474749975],
            [0.2475249975, 0.2525250025, 0.2474749975, 0.2524749975],
            [0.2524749975, 0.2474749975, 0.2525250025, 0.2475249975],
            [0.2474749975, 0.2524749975, 0.2475249975, 0.2525250025]
        ]
    }

    tipo = tipo.upper()

    if tipo not in matrices:
        raise ValueError("El escenario seleccionado no existe.")

    A = matrices[tipo]

    validar_sistema(A, [0.0] * 4)

    if not verificar_spd(A):
        raise ValueError(
            "La matriz generada no cumple la condición SPD."
        )

    b = producto_matriz_vector(A, x_exacta)

    condicion = calcular_condicion(A)

    return {
        "escenario": tipo,
        "A": A,
        "b": b,
        "solucion_exacta": x_exacta,
        "numero_condicion": condicion
    }


# =====================================================
# 11. EJECUCIÓN COMPARATIVA
# =====================================================

def ejecutar_metodos(
    A, b,
    tolerancia=1e-6,
    max_iter=100,
    x0=None,
    solucion_referencia=None
):

    validar_sistema(A, b)
    validar_parametros(tolerancia, max_iter)

    verificar_diagonal(A)

    if solucion_referencia is not None:
        if len(solucion_referencia) != len(b):
            raise ValueError(
                "La solución de referencia tiene dimensiones incorrectas."
            )

        referencia = list(solucion_referencia)

    else:
        referencia = resolver_referencia(A, b)

    resultados = {}

    metodos = {
        "Jacobi": resolver_jacobi,
        "Gauss-Seidel": resolver_gauss_seidel,
        "LU": resolver_lu,
        "Gradiente conjugado": resolver_gradiente_conjugado
    }

    for nombre, metodo in metodos.items():

        inicio = perf_counter()

        try:

            if nombre == "LU":

                solucion = metodo(A, b)

                resultado = {
                    "solucion": solucion,
                    "iteraciones": 1,
                    "error": 0.0,
                    "convergio": True,
                    "historial": []
                }

            else:

                resultado = metodo(
                    A, b,
                    tolerancia,
                    max_iter,
                    x0
                )

                solucion = resultado["solucion"]

            tiempo = (perf_counter() - inicio) * 1000

            resultado["residual"] = calcular_residuo(
                A, solucion, b
            )

            resultado["error_absoluto"] = error_absoluto(
                solucion, referencia
            )

            resultado["error_relativo"] = error_relativo(
                solucion, referencia
            )

            resultado["tiempo_ms"] = tiempo

            resultados[nombre] = resultado

        except (ValueError, ZeroDivisionError) as error:

            resultados[nombre] = {
                "solucion": None,
                "convergio": False,
                "error": str(error),
                "residual": None,
                "tiempo_ms": None
            }

    return {
        "solucion_referencia": referencia,
        "numero_condicion": calcular_condicion(A),
        "resultados": resultados
    }


# =====================================================
# 12. EJECUCIÓN COMPLETA DE UN ESCENARIO
# =====================================================

def ejecutar_escenario(
    tipo,
    tolerancia=1e-6,
    max_iter=100
):

    sistema = generar_sistema_escenario(tipo)

    comparacion = ejecutar_metodos(
        sistema["A"],
        sistema["b"],
        tolerancia=tolerancia,
        max_iter=max_iter,
        solucion_referencia=sistema["solucion_exacta"]
    )

    return {
        **sistema,
        **comparacion
    }
