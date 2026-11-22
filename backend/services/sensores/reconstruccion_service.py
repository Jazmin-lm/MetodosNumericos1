import math
import time

from extensions import db

from models import (
    CasoEstudio,
    Escenario,
    Senal,
    PuntoSenal,
    PuntoReferencia,
    Reconstruccion,
    DetalleReconstruccion,
    Simulacion,
    EjecucionMetodo,
    IteracionResultado,
    ResultadoResumen,
)

from backend.modulos.sensores import reconstruir_senal

from backend.services.sensores.preparacion_service import (
    preparar_datos_reconstruccion,
)

from backend.services.sensores.metricas_service import (
    calcular_metricas_metodos,
)


def _normalizar_json(valor):
    """
    Convierte estructuras y números a valores compatibles con JSON.
    Los valores NaN e infinitos se convierten en None.
    """

    if isinstance(valor, dict):
        return {
            str(clave): _normalizar_json(contenido)
            for clave, contenido in valor.items()
        }

    if isinstance(valor, (list, tuple)):
        return [
            _normalizar_json(item)
            for item in valor
        ]

    if isinstance(valor, float):
        if not math.isfinite(valor):
            return None

    return valor


def _validar_lista_numerica(valores, nombre):
    if not isinstance(valores, list) or not valores:
        raise ValueError(
            f"{nombre} debe ser una lista no vacía."
        )

    resultado = []

    for valor in valores:
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError(
                f"{nombre} contiene valores no numéricos."
            )

        if not math.isfinite(numero):
            raise ValueError(
                f"{nombre} contiene valores no válidos."
            )

        resultado.append(numero)

    return resultado


def _obtener_escenario(escenario_id):
    """
    Obtiene el escenario seleccionado.
    Si no se seleccionó uno, utiliza NORMAL.
    """

    if escenario_id not in (None, ""):

        try:
            escenario_id = int(escenario_id)
        except (TypeError, ValueError):
            raise ValueError(
                "El identificador del escenario no es válido."
            )

        escenario = db.session.get(
            Escenario,
            escenario_id
        )

        if not escenario:
            raise ValueError(
                "El escenario seleccionado no existe."
            )

        if not escenario.caso or escenario.caso.modulo != "sensores":
            raise ValueError(
                "El escenario no pertenece al módulo de sensores."
            )

        return escenario

    caso = CasoEstudio.query.filter_by(
        modulo="sensores"
    ).first()

    if not caso:
        raise ValueError(
            "No existe el caso de sensores. "
            "Ejecuta crear_datos_iniciales.py."
        )

    escenario = Escenario.query.filter_by(
        caso_id=caso.id,
        tipo="NORMAL"
    ).first()

    if not escenario:
        raise ValueError(
            "No existe el escenario NORMAL de sensores. "
            "Ejecuta crear_datos_iniciales.py."
        )

    return escenario


def _obtener_referencias(senal_id):
    """
    Devuelve las referencias reales de una señal como diccionario:
    {tiempo: valor_real}.
    """

    puntos = PuntoReferencia.query.filter_by(
        senal_id=senal_id
    ).all()

    referencias = {}

    for punto in puntos:
        tiempo = float(punto.tiempo)
        valor = float(punto.valor_real)

        if math.isfinite(tiempo) and math.isfinite(valor):
            referencias[tiempo] = valor

    return referencias


def _generar_conclusiones(
    escenario,
    metricas,
    analisis_mal_condicionado,
    hay_referencias
):
    """
    Genera conclusiones numéricas y conclusiones relacionadas
    con el problema de reconstrucción.
    """

    # ----------------------------------------------
    # CONCLUSIÓN NUMÉRICA
    # ----------------------------------------------

    if metricas:
        metricas_validas = {
            metodo: datos
            for metodo, datos in metricas.items()
            if datos and datos.get("rmse") is not None
        }

        if metricas_validas:
            mejor_metodo = min(
                metricas_validas,
                key=lambda metodo: metricas_validas[metodo]["rmse"]
            )

            mejor_rmse = metricas_validas[mejor_metodo]["rmse"]

            conclusion_numerica = (
                f"El método con menor RMSE fue {mejor_metodo.upper()}, "
                f"con un RMSE de {mejor_rmse:.8f}. "
                "La comparación se realizó utilizando los valores "
                "reales de referencia disponibles."
            )
        else:
            conclusion_numerica = (
                "No fue posible determinar el método más preciso "
                "mediante RMSE."
            )
    else:
        conclusion_numerica = (
            "No existen valores reales de referencia para calcular "
            "MAE, RMSE y errores relativos. Los resultados representan "
            "estimaciones numéricas, no una validación contra valores reales."
        )

    # ----------------------------------------------
    # CONCLUSIÓN DEL PROBLEMA
    # ----------------------------------------------

    tipo = str(escenario).upper()

    if tipo == "NORMAL":
        conclusion_problema = (
            "La reconstrucción se realizó utilizando las mediciones "
            "originales de la señal, sin introducir perturbaciones "
            "artificiales."
        )

    elif tipo == "ESTRES":
        conclusion_problema = (
            "La reconstrucción se realizó con mediciones perturbadas "
            "por ruido determinista. Este escenario permite estudiar "
            "cómo las alteraciones de las mediciones afectan la estimación."
        )

    elif tipo == "MAL_CONDICIONADO":
        conclusion_problema = (
            "Se utilizó una función sintética de Runge para estudiar "
            "la estabilidad de la interpolación. Los resultados no "
            "representan mediciones físicas del sensor."
        )

    else:
        conclusion_problema = (
            "La reconstrucción se completó utilizando el escenario "
            "seleccionado."
        )

    if not hay_referencias:
        conclusion_problema += (
            " No hay referencias reales suficientes para verificar "
            "la precisión de la reconstrucción."
        )

    # ----------------------------------------------
    # CONCLUSIÓN DE ESTABILIDAD
    # ----------------------------------------------

    if analisis_mal_condicionado:
        factor = analisis_mal_condicionado.get("factor_amplificacion")
        error_equidistante = analisis_mal_condicionado.get(
            "error_maximo_equidistante"
        )
        error_chebyshev = analisis_mal_condicionado.get(
            "error_maximo_chebyshev"
        )

        if all(
            valor is not None
            for valor in (
                factor,
                error_equidistante,
                error_chebyshev
            )
        ):
            conclusion_problema += (
                " Análisis de estabilidad: "
                f"factor de amplificación {float(factor):.6g}; "
                "error máximo con nodos equidistantes "
                f"{float(error_equidistante):.8g}; "
                "error máximo con nodos de Chebyshev "
                f"{float(error_chebyshev):.8g}."
            )
        else:
            conclusion_problema += (
                " Se realizó el análisis de estabilidad, "
                "pero algunos indicadores no están disponibles."
            )

    return {
        "numerica": conclusion_numerica,
        "problema": conclusion_problema
    }


def ejecutar_reconstruccion(
    senal_id,
    puntos_evaluar,
    escenario_id=None,
    observacion=None,
    usuario=None
):
    """
    Ejecuta la reconstrucción de una señal usando:

    - Lagrange
    - Newton
    - Splines cúbicos

    Aplica el escenario seleccionado y guarda los resultados
    en las tablas propias del módulo 4 y en las tablas generales.
    """

    inicio_total = time.perf_counter()

    try:
        # ==================================================
        # 1. VALIDAR IDENTIFICADOR Y OBTENER SEÑAL
        # ==================================================

        try:
            senal_id = int(senal_id)
        except (TypeError, ValueError):
            raise ValueError(
                "El identificador de la señal no es válido."
            )

        senal = db.session.get(
            Senal,
            senal_id
        )

        if not senal:
            raise ValueError(
                "La señal seleccionada no existe."
            )

        # ==================================================
        # 2. OBTENER MEDICIONES ORIGINALES
        # ==================================================

        puntos = (
            PuntoSenal.query
            .filter_by(senal_id=senal.id)
            .order_by(PuntoSenal.tiempo.asc())
            .all()
        )

        if len(puntos) < 2:
            raise ValueError(
                "La señal necesita al menos dos mediciones conocidas."
            )

        # ==================================================
        # 3. VALIDAR PUNTOS DE EVALUACIÓN
        # ==================================================

        evaluar = _validar_lista_numerica(
            puntos_evaluar,
            "Los puntos a reconstruir"
        )

        if len(set(evaluar)) != len(evaluar):
            raise ValueError(
                "No puede haber tiempos de evaluación repetidos."
            )

        # ==================================================
        # 4. OBTENER ESCENARIO
        # ==================================================

        escenario = _obtener_escenario(
            escenario_id
        )

        # ==================================================
        # 5. OBTENER REFERENCIAS
        # ==================================================

        referencias = _obtener_referencias(
            senal.id
        )

        # ==================================================
        # 6. PREPARAR LOS DATOS SEGÚN EL ESCENARIO
        # ==================================================

        datos_preparados = preparar_datos_reconstruccion(
            puntos=puntos,
            escenario=escenario,
            puntos_evaluar=evaluar,
            referencias=referencias
        )

        x = datos_preparados["x"]
        y = datos_preparados["y"]

        evaluar = datos_preparados["puntos_evaluar"]
        valores_reales = datos_preparados["valores_reales"]

        hay_referencias = (
            valores_reales is not None
        )

        # ==================================================
        # 7. EJECUTAR LOS TRES MÉTODOS
        # ==================================================

        resultado = reconstruir_senal({
            "x": x,
            "y": y,
            "puntos_evaluar": evaluar,
            "valores_reales": valores_reales
        })

        resultados = resultado["resultados"]
        tiempos = resultado.get("tiempos_ms", {})

        metricas = calcular_metricas_metodos(
            valores_reales,
            resultados
        )
        analisis_mal_condicionado = (
            datos_preparados.get("analisis_mal_condicionado")
        )

        conclusiones = _generar_conclusiones(
            escenario=escenario.tipo,
            metricas=metricas,
            analisis_mal_condicionado=analisis_mal_condicionado,
            hay_referencias=hay_referencias
        )

        # ==================================================
        # 8. VALIDAR RESULTADOS NUMÉRICOS
        # ==================================================

        for metodo, valores in resultados.items():

            if len(valores) != len(evaluar):
                raise ValueError(
                    f"El método {metodo} devolvió una cantidad "
                    "incorrecta de resultados."
                )

            for valor in valores:
                if not math.isfinite(float(valor)):
                    raise ValueError(
                        f"El método {metodo} produjo "
                        "un resultado no finito."
                    )

        # ==================================================
        # 9. CREAR SIMULACIÓN GENERAL
        # ==================================================

        simulacion = Simulacion(
            escenario_id=escenario.id,
            usuario_equipo=(
                str(usuario).strip()
                if usuario
                else "Módulo 4 - Sensores"
            ),
            estado="COMPLETADA"
        )

        db.session.add(simulacion)
        db.session.flush()

        # ==================================================
        # 10. CREAR RECONSTRUCCIÓN DEL MÓDULO 4
        # ==================================================

        nombres = {
            "lagrange": "LAGRANGE",
            "newton": "NEWTON",
            "splines": "SPLINES_CUBICOS"
        }

        parametros_reconstruccion = {
            "puntos_evaluar": evaluar,
            "cantidad_puntos_conocidos": len(x),
            "metodos": list(nombres.values()),
            "escenario": escenario.tipo,
            "parametros_escenario": (
                escenario.parametros_json or {}
            ),
            "preparacion": datos_preparados["descripcion"],
            "tipo_escenario": datos_preparados["tipo_escenario"],
            "hay_referencias": hay_referencias,
            "analisis_mal_condicionado": analisis_mal_condicionado,
            "conclusiones": conclusiones
        }

        reconstruccion = Reconstruccion(
            senal_id=senal.id,
            escenario_id=escenario.id,
            simulacion_id=simulacion.id,
            estado="COMPLETADA",
            parametros_json=_normalizar_json(
                parametros_reconstruccion
            ),
            metricas_globales_json=_normalizar_json(
                metricas
            ),
            observacion=observacion
        )

        db.session.add(reconstruccion)
        db.session.flush()

        # ==================================================
        # 11. GUARDAR CADA MÉTODO
        # ==================================================

        for clave, nombre_metodo in nombres.items():

            valores = resultados[clave]
            tiempo_metodo = tiempos.get(clave)
            metrica = metricas.get(clave)

            # ----------------------------------------------
            # EJECUCIÓN GENERAL
            # ----------------------------------------------

            ejecucion = EjecucionMetodo(
                simulacion_id=simulacion.id,
                metodo=nombre_metodo,
                tolerancia=None,
                paso=None,
                max_iter=len(evaluar),
                convergio=True,
                tiempo_ms=tiempo_metodo
            )

            db.session.add(ejecucion)
            db.session.flush()

            # ----------------------------------------------
            # DETALLE DEL MÓDULO 4
            # ----------------------------------------------

            detalle = DetalleReconstruccion(
                reconstruccion_id=reconstruccion.id,
                metodo=nombre_metodo,
                valores_reconstruidos_json={
                    "tiempos": evaluar,
                    "valores": valores
                },
                metricas_json=_normalizar_json(
                    metrica or {}
                ),
                tiempo_ms=tiempo_metodo,
                convergio=True
            )

            db.session.add(detalle)

            # ----------------------------------------------
            # ITERACIONES / PUNTOS EVALUADOS
            # ----------------------------------------------

            for indice, tiempo in enumerate(evaluar):

                estimado = float(valores[indice])

                real = (
                    float(valores_reales[indice])
                    if hay_referencias
                    else None
                )

                residual = None
                error_abs = None
                error_rel = None

                if real is not None:

                    residual = real - estimado
                    error_abs = abs(residual)

                    if real != 0:
                        error_rel = error_abs / abs(real)

                iteracion = IteracionResultado(
                    ejecucion_id=ejecucion.id,
                    numero=indice + 1,
                    aproximacion_json={
                        "tiempo": tiempo,
                        "valor_estimado": estimado,
                        "valor_real": real
                    },
                    residual=residual,
                    error_abs=error_abs,
                    error_rel=error_rel
                )

                db.session.add(iteracion)

            # ----------------------------------------------
            # RESUMEN DEL MÉTODO
            # ----------------------------------------------

            resumen = ResultadoResumen(
                ejecucion_id=ejecucion.id,
                referencia=(
                    "Valores reales de referencia"
                    if hay_referencias
                    else "No hay valores reales de referencia"
                ),
                valor_json={
                    "tiempos": evaluar,
                    "valores": valores,
                    "valores_reales": valores_reales
                },
                metrica_error_json=_normalizar_json(
                    metrica or {}
                ),
                interpretacion=(
                    f"Resultado del método {nombre_metodo} "
                    f"en la reconstrucción de la señal {senal.nombre} "
                    f"bajo el escenario {escenario.tipo}."
                )
            )

            db.session.add(resumen)

        # ==================================================
        # 12. RESUMEN GENERAL DE LA SIMULACIÓN
        # ==================================================

        tiempo_total = (
            time.perf_counter() - inicio_total
        ) * 1000

        ejecucion_resumen = EjecucionMetodo(
            simulacion_id=simulacion.id,
            metodo="RESUMEN_COMPLETO",
            tolerancia=None,
            paso=None,
            max_iter=None,
            convergio=True,
            tiempo_ms=tiempo_total
        )

        db.session.add(ejecucion_resumen)
        db.session.flush()

        resumen_completo = ResultadoResumen(
            ejecucion_id=ejecucion_resumen.id,
            referencia="Reconstrucción completa de señal",
            valor_json=_normalizar_json({
                "senal_id": senal.id,
                "senal": senal.nombre,
                "escenario": escenario.tipo,
                "puntos_conocidos": {
                    "tiempos": x,
                    "valores": y
                },
                "puntos_evaluados": evaluar,
                "resultado": resultado,
                "preparacion": datos_preparados["descripcion"],
                "analisis_mal_condicionado": analisis_mal_condicionado,
                "conclusiones": conclusiones
            }),
            metrica_error_json=_normalizar_json(
                metricas
            ),
            interpretacion=(
                "Reconstrucción de señal ejecutada mediante "
                "Lagrange, Newton y splines cúbicos."
            )
        )

        db.session.add(resumen_completo)

        # ==================================================
        # 13. CONFIRMAR TRANSACCIÓN
        # ==================================================

        db.session.commit()

        # ==================================================
        # 14. DEVOLVER RESULTADOS A LA API Y AL FRONTEND
        # ==================================================

        return {
            "simulacion_id": simulacion.id,
            "reconstruccion_id": reconstruccion.id,
            "senal_id": senal.id,
            "escenario": escenario.tipo,
            "estado": reconstruccion.estado,
            "tiempo_ms": tiempo_total,

            "resultado": _normalizar_json(resultado),
            "metricas": _normalizar_json(metricas),

            # Análisis y conclusiones para la interfaz
            "analisis_mal_condicionado": _normalizar_json(
                analisis_mal_condicionado
            ),
            "conclusiones": conclusiones,

            # Datos utilizados para construir las gráficas
            "datos_entrada": {
                "puntos_conocidos": (
                    datos_preparados["puntos_conocidos"]
                ),
                "descripcion": datos_preparados["descripcion"],
                "tipo_escenario": datos_preparados["tipo_escenario"],
                "analisis_mal_condicionado": _normalizar_json(
                    analisis_mal_condicionado
                )
            }
        }

    except Exception:
        db.session.rollback()
        raise