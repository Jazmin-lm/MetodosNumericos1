def validar_datos(x, y):
    if len(x) != len(y):
        raise ValueError("Las listas de tiempos y valores deben tener el mismo tamaño.")

    if len(x) < 2:
        raise ValueError("Se necesitan al menos dos puntos conocidos.")

    if len(set(x)) != len(x):
        raise ValueError("No puede haber tiempos repetidos.")

    puntos = sorted(zip(x, y))
    return [p[0] for p in puntos], [p[1] for p in puntos]


def lagrange(x, y, puntos_evaluar):
    x, y = validar_datos(x, y)
    resultados = []

    for xp in puntos_evaluar:
        resultado = 0.0

        for i in range(len(x)):
            termino = y[i]

            for j in range(len(x)):
                if i != j:
                    termino *= (xp - x[j]) / (x[i] - x[j])

            resultado += termino

        resultados.append(resultado)

    return resultados


def newton(x, y, puntos_evaluar):
    x, y = validar_datos(x, y)
    n = len(x)

    diferencias = y[:]

    for nivel in range(1, n):
        for i in range(n - 1, nivel - 1, -1):
            diferencias[i] = (
                diferencias[i] - diferencias[i - 1]
            ) / (x[i] - x[i - nivel])

    resultados = []

    for xp in puntos_evaluar:
        resultado = diferencias[n - 1]

        for i in range(n - 2, -1, -1):
            resultado = diferencias[i] + (xp - x[i]) * resultado

        resultados.append(resultado)

    return resultados


def splines_cubicos(x, y, puntos_evaluar):
    x, y = validar_datos(x, y)
    n = len(x)

    h = [x[i + 1] - x[i] for i in range(n - 1)]

    # Sistema tridiagonal para spline natural.
    a = [0.0] * n
    b = [1.0] * n
    c = [0.0] * n
    d = [0.0] * n

    for i in range(1, n - 1):
        a[i] = h[i - 1]
        b[i] = 2 * (h[i - 1] + h[i])
        c[i] = h[i]
        d[i] = 6 * (
            (y[i + 1] - y[i]) / h[i]
            - (y[i] - y[i - 1]) / h[i - 1]
        )

    # Eliminación hacia adelante.
    for i in range(1, n):
        factor = a[i] / b[i - 1]
        b[i] -= factor * c[i - 1]
        d[i] -= factor * d[i - 1]

    # Sustitución hacia atrás.
    m = [0.0] * n
    m[-1] = d[-1] / b[-1]

    for i in range(n - 2, -1, -1):
        m[i] = (d[i] - c[i] * m[i + 1]) / b[i]

    resultados = []

    for xp in puntos_evaluar:
        if xp < x[0] or xp > x[-1]:
            raise ValueError(
                "Los splines solo se evalúan dentro del intervalo conocido."
            )

        i = n - 2
        for j in range(n - 1):
            if x[j] <= xp <= x[j + 1]:
                i = j
                break

        hi = h[i]
        izquierda = x[i + 1] - xp
        derecha = xp - x[i]

        valor = (
            m[i] * izquierda**3 / (6 * hi)
            + m[i + 1] * derecha**3 / (6 * hi)
            + (y[i] - m[i] * hi**2 / 6) * izquierda / hi
            + (y[i + 1] - m[i + 1] * hi**2 / 6) * derecha / hi
        )

        resultados.append(valor)

    return resultados
