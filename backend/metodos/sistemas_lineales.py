
def validar_sistema(A, b):
    n = len(A)

    if n == 0 or len(b) != n:
        raise ValueError("Las dimensiones de A y b no coinciden.")

    if any(len(fila) != n for fila in A):
        raise ValueError("La matriz A debe ser cuadrada.")

    if any(abs(A[i][i]) < 1e-14 for i in range(n)):
        raise ValueError("Hay un cero en la diagonal de A.")

def residuo(A, x, b):
    return max(
        abs(sum(A[i][j] * x[j] for j in range(len(x))) - b[i])
        for i in range(len(x))
    )

def resolver_directo(A, b):
    """Eliminación de Gauss con pivoteo parcial."""
    M = [fila[:] + [b[i]] for i, fila in enumerate(A)]
    n = len(b)

    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(M[i][k]))

        if abs(M[p][k]) < 1e-14:
            raise ValueError("El sistema no tiene solución única.")

        M[k], M[p] = M[p], M[k]

        for i in range(k + 1, n):
            factor = M[i][k] / M[k][k]
            for j in range(k, n + 1):
                M[i][j] -= factor * M[k][j]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (
            M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
        ) / M[i][i]

    return x

def resolver_lu(A, b):
    """Factorización LU de Doolittle, sin pivoteo."""
    n = len(b)
    L = [[0.0] * n for _ in range(n)]
    U = [[0.0] * n for _ in range(n)]

    for i in range(n):
        L[i][i] = 1.0

    for j in range(n):
        for i in range(j + 1):
            U[i][j] = A[i][j] - sum(
                L[i][k] * U[k][j] for k in range(i)
            )

        if abs(U[j][j]) < 1e-14:
            raise ValueError("No se pudo realizar la factorización LU.")

        for i in range(j + 1, n):
            L[i][j] = (
                A[i][j] - sum(L[i][k] * U[k][j] for k in range(j))
            ) / U[j][j]

    y = [0.0] * n
    for i in range(n):
        y[i] = b[i] - sum(L[i][j] * y[j] for j in range(i))

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (
            y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))
        ) / U[i][i]

    return x

def resolver_jacobi(A, b, tolerancia=1e-6, max_iter=100, x0=None):
    n = len(b)
    x = list(x0) if x0 is not None else [0.0] * n

    for k in range(1, max_iter + 1):
        nuevo = [0.0] * n

        for i in range(n):
            suma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            nuevo[i] = (b[i] - suma) / A[i][i]

        error = max(abs(nuevo[i] - x[i]) for i in range(n))
        x = nuevo

        if error < tolerancia:
            return x, k, error

    return x, max_iter, error

def resolver_gauss_seidel(A, b, tolerancia=1e-6, max_iter=100, x0=None):
    n = len(b)
    x = list(x0) if x0 is not None else [0.0] * n

    for k in range(1, max_iter + 1):
        anterior = x[:]

        for i in range(n):
            suma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b[i] - suma) / A[i][i]

        error = max(abs(x[i] - anterior[i]) for i in range(n))

        if error < tolerancia:
            return x, k, error

    return x, max_iter, error

def resolver_gradiente_conjugado(A, b, tolerancia=1e-6, max_iter=100, x0=None):
    n = len(b)
    x = list(x0) if x0 is not None else [0.0] * n

    def producto(M, v):
        return [sum(M[i][j] * v[j] for j in range(n)) for i in range(n)]

    def producto_punto(u, v):
        return sum(u[i] * v[i] for i in range(n))

    Ax = producto(A, x)
    r = [b[i] - Ax[i] for i in range(n)]
    p = r[:]
    rr = producto_punto(r, r)

    for k in range(1, max_iter + 1):
        Ap = producto(A, p)
        denominador = producto_punto(p, Ap)

        if abs(denominador) < 1e-20:
            break

        alfa = rr / denominador
        x = [x[i] + alfa * p[i] for i in range(n)]
        r = [r[i] - alfa * Ap[i] for i in range(n)]

        nuevo_rr = producto_punto(r, r)
        error = nuevo_rr ** 0.5

        if error < tolerancia:
            return x, k, error

        beta = nuevo_rr / rr
        p = [r[i] + beta * p[i] for i in range(n)]
        rr = nuevo_rr

    return x, k, error

def ejecutar_metodos(A, b, tolerancia=1e-6, max_iter=100, x0=None):
    validar_sistema(A, b)

    if tolerancia <= 0 or max_iter < 1:
        raise ValueError("La tolerancia debe ser positiva y las iteraciones mayores que cero.")

    referencia = resolver_directo(A, b)
    resultados = {}

    resultados["Referencia directa"] = {
        "solucion": referencia,
        "residual": residuo(A, referencia, b)
    }

    resultados["LU"] = {
        "solucion": resolver_lu(A, b)
    }

    for nombre, metodo in [
        ("Jacobi", resolver_jacobi),
        ("Gauss-Seidel", resolver_gauss_seidel),
        ("Gradiente conjugado", resolver_gradiente_conjugado)
    ]:
        solucion, iteraciones, error = metodo(
            A, b, tolerancia, max_iter, x0
        )

        resultados[nombre] = {
            "solucion": solucion,
            "iteraciones": iteraciones,
            "error": error
        }

    for datos in resultados.values():
        datos["residual"] = residuo(A, datos["solucion"], b)
        datos["error_referencia"] = max(
            abs(datos["solucion"][i] - referencia[i])
            for i in range(len(b))
        )

    return resultados
