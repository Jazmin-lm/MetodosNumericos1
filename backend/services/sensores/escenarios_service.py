
from models import CasoEstudio, Escenario


def listar_escenarios_sensores():
    caso = CasoEstudio.query.filter_by(
        modulo="sensores"
    ).first()

    if not caso:
        return []

    escenarios = (
        Escenario.query
        .filter_by(caso_id=caso.id)
        .order_by(Escenario.id.asc())
        .all()
    )

    return [
        {
            "id": escenario.id,
            "tipo": escenario.tipo,
            "descripcion": (
                escenario.parametros_json or {}
            ).get("descripcion", "Escenario de sensores"),
            "parametros": escenario.parametros_json or {},
            "fuente_datos": escenario.fuente_datos,
        }
        for escenario in escenarios
    ]


def obtener_escenario_sensor(escenario_id):
    escenario = Escenario.query.get(escenario_id)

    if not escenario:
        raise ValueError("El escenario no existe.")

    if escenario.caso.modulo != "sensores":
        raise ValueError("El escenario no pertenece al módulo de sensores.")

    return escenario
