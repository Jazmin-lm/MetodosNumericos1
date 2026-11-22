
from models import Reconstruccion


def _serializar_ejecuciones(simulacion):
    if not simulacion:
        return []

    resultado = []

    for ejecucion in simulacion.ejecuciones:
        resultado.append({
            "id": ejecucion.id,
            "metodo": ejecucion.metodo,
            "convergio": ejecucion.convergio,
            "tiempo_ms": ejecucion.tiempo_ms,
            "iteraciones": [
                {
                    "numero": item.numero,
                    "aproximacion": item.aproximacion_json,
                    "residual": item.residual,
                    "error_abs": item.error_abs,
                    "error_rel": item.error_rel
                }
                for item in sorted(
                    ejecucion.iteraciones,
                    key=lambda item: item.numero
                )
            ],
            "resumenes": [
                {
                    "referencia": item.referencia,
                    "valor": item.valor_json,
                    "metricas": item.metrica_error_json,
                    "interpretacion": item.interpretacion
                }
                for item in ejecucion.resumenes
            ]
        })

    return resultado


def listar_historial_sensores(limite=50):
    limite = max(1, min(int(limite), 200))

    reconstrucciones = (
        Reconstruccion.query
        .join(Reconstruccion.senal)
        .order_by(Reconstruccion.fecha.desc())
        .limit(limite)
        .all()
    )

    resultado = []

    for reconstruccion in reconstrucciones:
        simulacion = reconstruccion.simulacion

        resultado.append({
            "id": reconstruccion.id,
            "simulacion_id": reconstruccion.simulacion_id,
            "senal_id": reconstruccion.senal_id,
            "senal": reconstruccion.senal.nombre,
            "sensor": reconstruccion.senal.sensor.nombre,
            "escenario": (
                reconstruccion.escenario.tipo
                if reconstruccion.escenario
                else None
            ),
            "fecha": (
                reconstruccion.fecha.isoformat()
                if reconstruccion.fecha
                else None
            ),
            "estado": reconstruccion.estado,
            "metricas": (
                reconstruccion.metricas_globales_json or {}
            ),
            "detalles": [
                {
                    "metodo": detalle.metodo,
                    "valores": detalle.valores_reconstruidos_json,
                    "metricas": detalle.metricas_json,
                    "tiempo_ms": detalle.tiempo_ms,
                    "convergio": detalle.convergio
                }
                for detalle in reconstruccion.detalles
            ],
            "ejecuciones_generales": _serializar_ejecuciones(
                simulacion
            )
        })

    return resultado


def obtener_reconstruccion(reconstruccion_id):
    reconstruccion = Reconstruccion.query.get(
        reconstruccion_id
    )

    if not reconstruccion:
        return None

    simulacion = reconstruccion.simulacion

    return {
        "id": reconstruccion.id,
        "simulacion_id": reconstruccion.simulacion_id,
        "senal_id": reconstruccion.senal_id,
        "senal": reconstruccion.senal.nombre,
        "sensor": reconstruccion.senal.sensor.nombre,
        "escenario": (
            reconstruccion.escenario.tipo
            if reconstruccion.escenario
            else None
        ),
        "fecha": (
            reconstruccion.fecha.isoformat()
            if reconstruccion.fecha
            else None
        ),
        "estado": reconstruccion.estado,
        "parametros": (
            reconstruccion.parametros_json or {}
        ),
        "metricas": (
            reconstruccion.metricas_globales_json or {}
        ),
        "detalles": [
            {
                "metodo": detalle.metodo,
                "valores": detalle.valores_reconstruidos_json,
                "metricas": detalle.metricas_json,
                "tiempo_ms": detalle.tiempo_ms,
                "convergio": detalle.convergio
            }
            for detalle in reconstruccion.detalles
        ],
        "ejecuciones_generales": _serializar_ejecuciones(
            simulacion
        )
    }


def obtener_datos_repeticion(reconstruccion_id):
    """
    Recupera los parámetros originales necesarios para repetir
    una reconstrucción guardada.
    """

    reconstruccion = Reconstruccion.query.get(
        reconstruccion_id
    )

    if not reconstruccion:
        return None

    parametros = reconstruccion.parametros_json or {}

    puntos_evaluar = parametros.get("puntos_evaluar")

    if not puntos_evaluar:
        raise ValueError(
            "La reconstrucción guardada no contiene "
            "los puntos de evaluación originales."
        )

    return {
        "senal_id": reconstruccion.senal_id,
        "escenario_id": reconstruccion.escenario_id,
        "puntos_evaluar": puntos_evaluar,
        "observacion": (
            "Repetición de la reconstrucción "
            f"#{reconstruccion.id}"
        )
    }
