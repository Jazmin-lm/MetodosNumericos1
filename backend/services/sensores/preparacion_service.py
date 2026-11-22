
import math

from backend.metodos.interpolacion import lagrange


def _runge(tiempo, minimo, maximo):
    """
    Función de Runge:
        f(u) = 1 / (1 + 25u²)

    El tiempo se transforma desde [minimo, maximo] hasta [-1, 1].
    """
    amplitud = maximo - minimo

    if amplitud == 0:
        raise ValueError(
            "No se puede generar la función de Runge "
            "porque el intervalo de tiempos es nulo."
        )

    u = 2.0 * (tiempo - minimo) / amplitud - 1.0

    return 1.0 / (1.0 + 25.0 * u ** 2)


def _validar_puntos(puntos):
    if not puntos or len(puntos) < 2:
        raise ValueError(
            "Se necesitan al menos dos mediciones conocidas."
        )

    datos = []

    for punto in puntos:
        tiempo = float(punto.tiempo)
        valor = float(punto.valor)

        if not math.isfinite(tiempo) or not math.isfinite(valor):
            raise ValueError(
                "La señal contiene tiempos o mediciones no válidos."
            )

        datos.append({
            "tiempo": tiempo,
            "valor": valor
        })

    datos.sort(key=lambda item: item["tiempo"])

    tiempos = [item["tiempo"] for item in datos]

    if len(set(tiempos)) != len(tiempos):
        raise ValueError(
            "La señal contiene tiempos repetidos."
        )

    return datos


def _generar_nodos_equidistantes(minimo, maximo, cantidad):
    return [
        minimo + indice * (maximo - minimo) / (cantidad - 1)
        for indice in range(cantidad)
    ]


def _generar_nodos_chebyshev(minimo, maximo, cantidad):
    """
    Genera nodos de Chebyshev de primera especie
    y los transforma al intervalo [minimo, maximo].
    """
    nodos = []

    for indice in range(cantidad):
        u = math.cos(
            (2 * indice + 1) * math.pi / (2 * cantidad)
        )

        tiempo = (
            (minimo + maximo) / 2
            + ((maximo - minimo) / 2) * u
        )

        nodos.append(tiempo)

    return sorted(nodos)


def _calcular_error_maximo(valores_reales, valores_aproximados):
    errores = [
        abs(real - aproximado)
        for real, aproximado in zip(
            valores_reales,
            valores_aproximados
        )
    ]

    return max(errores) if errores else 0.0


def _analizar_mal_condicionamiento(
    minimo,
    maximo,
    cantidad_nodos
):
    """
    Compara interpolación de Runge con nodos equidistantes
    y nodos de Chebyshev.

    También perturba ligeramente las mediciones para estudiar
    la sensibilidad de la interpolación de Lagrange.
    """

    # Malla densa para evaluar el comportamiento de las curvas.
    cantidad_prueba = 300

    puntos_prueba = [
        minimo + indice * (maximo - minimo) / (cantidad_prueba - 1)
        for indice in range(cantidad_prueba)
    ]

    valores_reales = [
        _runge(tiempo, minimo, maximo)
        for tiempo in puntos_prueba
    ]

    # --------------------------------------------------
    # 1. NODOS EQUIDISTANTES
    # --------------------------------------------------

    x_equidistantes = _generar_nodos_equidistantes(
        minimo,
        maximo,
        cantidad_nodos
    )

    y_equidistantes = [
        _runge(tiempo, minimo, maximo)
        for tiempo in x_equidistantes
    ]

    interpolacion_equidistante = lagrange(
        x_equidistantes,
        y_equidistantes,
        puntos_prueba
    )

    error_equidistante = _calcular_error_maximo(
        valores_reales,
        interpolacion_equidistante
    )

    # --------------------------------------------------
    # 2. NODOS DE CHEBYSHEV
    # --------------------------------------------------

    x_chebyshev = _generar_nodos_chebyshev(
        minimo,
        maximo,
        cantidad_nodos
    )

    y_chebyshev = [
        _runge(tiempo, minimo, maximo)
        for tiempo in x_chebyshev
    ]

    interpolacion_chebyshev = lagrange(
        x_chebyshev,
        y_chebyshev,
        puntos_prueba
    )

    error_chebyshev = _calcular_error_maximo(
        valores_reales,
        interpolacion_chebyshev
    )

    # --------------------------------------------------
    # 3. PRUEBA DE SENSIBILIDAD A PERTURBACIONES
    # --------------------------------------------------

    # Se modifica cada medición en una cantidad pequeña.
    escala = max(
        max(y_equidistantes) - min(y_equidistantes),
        1.0
    )

    perturbacion_maxima_entrada = escala * 1e-6

    y_perturbados = [
        valor + perturbacion_maxima_entrada
        * math.sin((indice + 1) * 2.399963229728653)
        for indice, valor in enumerate(y_equidistantes)
    ]

    interpolacion_perturbada = lagrange(
        x_equidistantes,
        y_perturbados,
        puntos_prueba
    )

    cambios_salida = [
        abs(nuevo - original)
        for nuevo, original in zip(
            interpolacion_perturbada,
            interpolacion_equidistante
        )
    ]

    cambio_maximo_salida = max(cambios_salida)

    if perturbacion_maxima_entrada > 0:
        factor_amplificacion = (
            cambio_maximo_salida / perturbacion_maxima_entrada
        )
    else:
        factor_amplificacion = 0.0

    return {
        "funcion": "f(u) = 1 / (1 + 25u^2)",
        "cantidad_nodos": cantidad_nodos,
        "intervalo": [minimo, maximo],

        "nodos_equidistantes": x_equidistantes,
        "nodos_chebyshev": x_chebyshev,

        "error_maximo_equidistante": error_equidistante,
        "error_maximo_chebyshev": error_chebyshev,

        "perturbacion_maxima_entrada": perturbacion_maxima_entrada,
        "cambio_maximo_salida": cambio_maximo_salida,
        "factor_amplificacion": factor_amplificacion,

        "conclusion": (
            "Los nodos de Chebyshev reducen el error máximo "
            "respecto a los nodos equidistantes."
            if error_chebyshev < error_equidistante
            else
            "En esta configuración los nodos de Chebyshev "
            "no redujeron el error máximo."
        )
    }


def preparar_datos_reconstruccion(
    puntos,
    escenario,
    puntos_evaluar,
    referencias=None
):
    """
    Prepara los datos de entrada para la reconstrucción.

    NORMAL:
        Utiliza las mediciones originales.

    ESTRES:
        Introduce una perturbación determinista en las mediciones
        conocidas, según el nivel_ruido del escenario.

    MAL_CONDICIONADO:
        Genera nodos sintéticos de Runge y analiza la diferencia
        entre nodos equidistantes y nodos de Chebyshev.

    No modifica los puntos almacenados en la base de datos.
    """

    datos_originales = _validar_puntos(puntos)

    parametros = escenario.parametros_json or {}
    tipo_escenario = str(escenario.tipo).upper()

    x_original = [
        item["tiempo"]
        for item in datos_originales
    ]

    y_original = [
        item["valor"]
        for item in datos_originales
    ]

    minimo = x_original[0]
    maximo = x_original[-1]

    evaluar = [float(valor) for valor in puntos_evaluar]

    if not evaluar:
        raise ValueError(
            "Debe indicar al menos un tiempo para reconstruir."
        )

    if any(not math.isfinite(valor) for valor in evaluar):
        raise ValueError(
            "Los tiempos de evaluación contienen valores no válidos."
        )

    if len(set(evaluar)) != len(evaluar):
        raise ValueError(
            "No puede haber tiempos de evaluación repetidos."
        )

    if any(valor < minimo or valor > maximo for valor in evaluar):
        raise ValueError(
            f"Los tiempos de evaluación deben estar entre "
            f"{minimo} y {maximo}."
        )

    analisis_mal_condicionado = None

    # --------------------------------------------------
    # ESCENARIO NORMAL
    # --------------------------------------------------

    if tipo_escenario == "NORMAL":

        x = x_original[:]
        y = y_original[:]

        valores_reales = [
            (referencias or {}).get(tiempo)
            for tiempo in evaluar
        ]

        descripcion_preparacion = (
            "Se utilizaron las mediciones originales de la señal."
        )

    # --------------------------------------------------
    # ESCENARIO DE ESTRÉS
    # --------------------------------------------------

    elif tipo_escenario == "ESTRES":

        nivel_ruido = float(
            parametros.get("nivel_ruido", 0.05)
        )

        if not math.isfinite(nivel_ruido) or nivel_ruido < 0:
            raise ValueError(
                "El nivel de ruido del escenario ESTRES no es válido."
            )

        escala = max(
            max(y_original) - min(y_original),
            max(abs(valor) for valor in y_original),
            1.0
        )

        x = x_original[:]
        y = []

        for indice, valor in enumerate(y_original):
            perturbacion = (
                nivel_ruido
                * escala
                * math.sin((indice + 1) * 2.399963229728653)
            )

            y.append(valor + perturbacion)

        valores_reales = [
            (referencias or {}).get(tiempo)
            for tiempo in evaluar
        ]

        descripcion_preparacion = (
            "Se aplicó ruido determinista a las mediciones "
            f"conocidas. Nivel de ruido: {nivel_ruido}."
        )

    # --------------------------------------------------
    # ESCENARIO MAL CONDICIONADO - RUNGE
    # --------------------------------------------------

    elif tipo_escenario == "MAL_CONDICIONADO":

        cantidad_nodos = max(
            11,
            len(datos_originales)
        )

        x = _generar_nodos_equidistantes(
            minimo,
            maximo,
            cantidad_nodos
        )

        y = [
            _runge(tiempo, minimo, maximo)
            for tiempo in x
        ]

        valores_reales = [
            _runge(tiempo, minimo, maximo)
            for tiempo in evaluar
        ]

        analisis_mal_condicionado = (
            _analizar_mal_condicionamiento(
                minimo,
                maximo,
                cantidad_nodos
            )
        )

        descripcion_preparacion = (
            "Se generaron nodos sintéticos de la función de Runge. "
            "Se compararon nodos equidistantes y de Chebyshev "
            "y se midió la sensibilidad ante pequeñas perturbaciones."
        )

    else:
        raise ValueError(
            f"El escenario '{escenario.tipo}' no está implementado."
        )

    # --------------------------------------------------
    # VALIDACIÓN FINAL
    # --------------------------------------------------

    if len(x) != len(y) or len(x) < 2:
        raise ValueError(
            "Los datos preparados no tienen una estructura válida."
        )

    if any(
        not math.isfinite(valor)
        for valor in x + y
    ):
        raise ValueError(
            "La preparación produjo valores no finitos."
        )

    puntos_conocidos = [
        {
            "tiempo": float(tiempo),
            "valor": float(valor)
        }
        for tiempo, valor in zip(x, y)
    ]

    hay_referencias = (
        len(valores_reales) == len(evaluar)
        and all(valor is not None for valor in valores_reales)
    )

    if hay_referencias:
        valores_reales = [
            float(valor)
            for valor in valores_reales
        ]
    else:
        valores_reales = None

    return {
        "x": x,
        "y": y,
        "puntos_evaluar": evaluar,
        "valores_reales": valores_reales,
        "puntos_conocidos": puntos_conocidos,
        "tipo_escenario": tipo_escenario,
        "descripcion": descripcion_preparacion,
        "hay_referencias": hay_referencias,
        "analisis_mal_condicionado": analisis_mal_condicionado
    }
