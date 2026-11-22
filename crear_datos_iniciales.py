from app import app
from extensions import db
from models import CasoEstudio, Escenario

with app.app_context():

    # ==========================================
    # 1. REGISTRAR CASOS DE ESTUDIO
    # ==========================================

    casos = [
        ("Detención de emergencia", "1.0", "detencion"),
        ("Deterioro mecánico", "1.0", "deterioro"),
        ("Oscilaciones por viento", "1.0", "oscilaciones"),
        ("Reconstrucción de sensores", "1.0", "sensores")
    ]

    for nombre, version, modulo in casos:

        existe = CasoEstudio.query.filter_by(
            nombre=nombre
        ).first()

        if not existe:
            nuevo = CasoEstudio(
                nombre=nombre,
                modelo_version=version,
                modulo=modulo
            )
            db.session.add(nuevo)

        else:
            existe.modulo = modulo

    db.session.flush()

    # ==========================================
    # 2. BUSCAR EL CASO DE DETERIORO MECÁNICO
    # ==========================================

    caso_deterioro = CasoEstudio.query.filter_by(
        nombre="Deterioro mecánico"
    ).first()

    # ==========================================
    # 3. DEFINIR LOS TRES ESCENARIOS
    # ==========================================

    escenarios = [
        {
            "tipo": "NORMAL",
            "parametros_json": {
                "descripcion": "Condiciones habituales de deterioro.",
                "factor_deterioro": 1.0,
                "perturbacion_relativa": 0.0,
                "condicion_objetivo": None
            },
            "fuente_datos": "Datos de prueba - escenario normal"
        },
        {
            "tipo": "ESTRES",
            "parametros_json": {
                "descripcion": "Condiciones exigentes con perturbaciones.",
                "factor_deterioro": 1.5,
                "perturbacion_relativa": 0.05,
                "condicion_objetivo": None
            },
            "fuente_datos": "Datos de prueba - escenario de estres"
        },
        {
            "tipo": "MAL_CONDICIONADO",
            "parametros_json": {
                "descripcion": "Problema numérico sensible a perturbaciones.",
                "factor_deterioro": 1.0,
                "perturbacion_relativa": 0.01,
                "condicion_objetivo": 100000000
            },
            "fuente_datos": "Datos de prueba - escenario mal condicionado"
        },
    {
        "tipo": "BUSQUEDA_RAICES",
        "parametros_json": {
            "descripcion": "Predicción del tiempo necesario para alcanzar el umbral de deterioro.",
            "metodos": [
                "BISECCION",
                "NEWTON_RAPHSON",
                "SECANTE"
            ],
            "modelo": "D(t) = D0 + alpha*t + beta*t^2",
            "fuente": "Mediciones registradas de los componentes mecánicos"
        },
        "fuente_datos": "Mediciones de deterioro de componentes mecánicos"
    }

    ]

    # ==========================================
    # 4. REGISTRAR O ACTUALIZAR ESCENARIOS
    # ==========================================

    for datos in escenarios:

        existe = Escenario.query.filter_by(
            caso_id=caso_deterioro.id,
            tipo=datos["tipo"]
        ).first()

        if not existe:

            nuevo_escenario = Escenario(
                caso_id=caso_deterioro.id,
                tipo=datos["tipo"],
                parametros_json=datos["parametros_json"],
                fuente_datos=datos["fuente_datos"]
            )

            db.session.add(nuevo_escenario)

        else:

            existe.parametros_json = datos["parametros_json"]
            existe.fuente_datos = datos["fuente_datos"]


    # ==========================================
    # 5. ESCENARIOS DEL MODULO DE SENSORES
    # ==========================================

    caso_sensores = CasoEstudio.query.filter_by(
        modulo="sensores"
    ).first()

    escenarios_sensores = [
        {
            "tipo": "NORMAL",
            "parametros_json": {
                "descripcion": "Señal con mediciones regulares y perturbación baja.",
                "nivel_ruido": 0.0,
                "tipo_prueba": "interpolacion"
            },
            "fuente_datos": "Datos de prueba - sensores normal"
        },
        {
            "tipo": "ESTRES",
            "parametros_json": {
                "descripcion": "Señal con mediciones perturbadas.",
                "nivel_ruido": 0.05,
                "tipo_prueba": "interpolacion"
            },
            "fuente_datos": "Datos de prueba - sensores estres"
        },
        {
            "tipo": "MAL_CONDICIONADO",
            "parametros_json": {
                "descripcion": "Señal de Runge para analizar sensibilidad numérica.",
                "nivel_ruido": 0.0,
                "tipo_prueba": "runge"
            },
            "fuente_datos": "Función de Runge - prueba de interpolación"
        }
    ]

    for datos in escenarios_sensores:
        existente = Escenario.query.filter_by(
            caso_id=caso_sensores.id,
            tipo=datos["tipo"]
        ).first()

        if existente:
            existente.parametros_json = datos["parametros_json"]
            existente.fuente_datos = datos["fuente_datos"]
        else:
            db.session.add(Escenario(
                caso_id=caso_sensores.id,
                tipo=datos["tipo"],
                parametros_json=datos["parametros_json"],
                fuente_datos=datos["fuente_datos"]
            ))

    # ==========================================
    # 5. GUARDAR CAMBIOS
    # ==========================================

    db.session.commit()

    print("Casos de estudio registrados correctamente.")
    print("Escenarios del modulo de deterioro registrados correctamente.")
