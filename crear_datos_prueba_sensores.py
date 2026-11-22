import math

from app import app
from extensions import db

from models import (
    Sensor,
    Senal,
    PuntoSenal,
    PuntoReferencia,
)


def obtener_o_crear_sensor(
    codigo,
    nombre,
    tipo,
    ubicacion,
    unidad,
    descripcion
):
    sensor = Sensor.query.filter_by(
        codigo=codigo
    ).first()

    if sensor is None:
        sensor = Sensor(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            ubicacion=ubicacion,
            unidad_medida=unidad,
            descripcion=descripcion,
            activo=True
        )

        db.session.add(sensor)
        db.session.flush()

    return sensor


def obtener_o_crear_senal(
    sensor,
    nombre,
    descripcion
):
    senal = Senal.query.filter_by(
        sensor_id=sensor.id,
        nombre=nombre
    ).first()

    if senal is None:
        senal = Senal(
            sensor_id=sensor.id,
            nombre=nombre,
            descripcion=descripcion,
            origen="DATOS_DEMO",
            estado="REGISTRADA"
        )

        db.session.add(senal)
        db.session.flush()

    return senal


def agregar_puntos(
    senal,
    funcion,
    tiempos_conocidos,
    tiempos_referencia,
    fuente
):
    """
    Agrega mediciones conocidas y referencias ocultas.

    Es idempotente: no duplica puntos que ya existen.
    """

    agregados = 0
    referencias_agregadas = 0

    for tiempo in tiempos_conocidos:

        tiempo = float(tiempo)

        existente = PuntoSenal.query.filter_by(
            senal_id=senal.id,
            tiempo=tiempo
        ).first()

        if existente is None:
            valor = float(funcion(tiempo))

            db.session.add(
                PuntoSenal(
                    senal_id=senal.id,
                    tiempo=tiempo,
                    valor=valor,
                    observacion="Medición conocida de datos de prueba"
                )
            )

            agregados += 1

    for tiempo in tiempos_referencia:

        tiempo = float(tiempo)

        existente = PuntoReferencia.query.filter_by(
            senal_id=senal.id,
            tiempo=tiempo
        ).first()

        if existente is None:
            valor_real = float(funcion(tiempo))

            db.session.add(
                PuntoReferencia(
                    senal_id=senal.id,
                    tiempo=tiempo,
                    valor_real=valor_real,
                    fuente=fuente,
                    observacion=(
                        "Valor real oculto para evaluar "
                        "la precisión de la reconstrucción."
                    )
                )
            )

            referencias_agregadas += 1

    return agregados, referencias_agregadas


def ejecutar_carga():
    # ==================================================
    # TIEMPOS DE PRUEBA
    # ==================================================

    tiempos_conocidos = [
        0, 1, 3, 4, 6, 8, 10
    ]

    tiempos_referencia = [
        2, 5, 7, 9
    ]

    # ==================================================
    # DEFINICIÓN DE SENSORES Y SEÑALES
    # ==================================================

    pruebas = [

        # ----------------------------------------------
        # 1. TEMPERATURA - SEÑAL SINUSOIDAL ORIGINAL
        # ----------------------------------------------

        {
            "codigo": "SEN-PRUEBA-001",
            "sensor": "Sensor de temperatura de prueba",
            "tipo": "Temperatura",
            "ubicacion": "Laboratorio de pruebas",
            "unidad": "°C",
            "descripcion": "Sensor de temperatura para pruebas.",
            "senal": "Señal sinusoidal de prueba",
            "descripcion_senal": (
                "Señal sinusoidal con mediciones conocidas "
                "y valores de referencia ocultos."
            ),
            "funcion": lambda t: math.sin(t),
            "conocidos": [0, 1, 3, 4, 6, 7],
            "referencias": [2, 5],
            "fuente": "Función sinusoidal de referencia"
        },

        # ----------------------------------------------
        # 2. VIBRACIÓN - SEÑAL OSCILATORIA AMORTIGUADA
        # ----------------------------------------------

        {
            "codigo": "SEN-VIB-002",
            "sensor": "Sensor de vibración industrial",
            "tipo": "Vibración",
            "ubicacion": "Motor industrial",
            "unidad": "mm/s",
            "descripcion": "Sensor para analizar vibraciones.",
            "senal": "Vibración amortiguada",
            "descripcion_senal": (
                "Oscilación amortiguada para evaluar "
                "la reconstrucción de señales dinámicas."
            ),
            "funcion": lambda t: (
                1.8 * math.exp(-0.18 * t)
                * math.sin(1.25 * t)
            ),
            "conocidos": tiempos_conocidos,
            "referencias": tiempos_referencia,
            "fuente": "Función de vibración amortiguada"
        },

        # ----------------------------------------------
        # 3. PRESIÓN - POLINOMIO CÚBICO
        # ----------------------------------------------

        {
            "codigo": "SEN-PRES-003",
            "sensor": "Sensor de presión industrial",
            "tipo": "Presión",
            "ubicacion": "Tubería de laboratorio",
            "unidad": "kPa",
            "descripcion": "Sensor para pruebas de presión.",
            "senal": "Variación cúbica de presión",
            "descripcion_senal": (
                "Señal polinómica cúbica para comprobar "
                "la precisión de la interpolación."
            ),
            "funcion": lambda t: (
                95 + 1.8 * t - 0.12 * t ** 2
                + 0.008 * t ** 3
            ),
            "conocidos": tiempos_conocidos,
            "referencias": tiempos_referencia,
            "fuente": "Función polinómica cúbica"
        },

        # ----------------------------------------------
        # 4. CAUDAL - SEÑAL PERIÓDICA
        # ----------------------------------------------

        {
            "codigo": "SEN-FLUJO-004",
            "sensor": "Sensor de caudal",
            "tipo": "Caudal",
            "ubicacion": "Conducto de laboratorio",
            "unidad": "L/s",
            "descripcion": "Sensor para medir caudal.",
            "senal": "Variación periódica del caudal",
            "descripcion_senal": (
                "Señal periódica con tendencia creciente."
            ),
            "funcion": lambda t: (
                12 + 2.5 * math.sin(0.65 * t)
                + 0.15 * t
            ),
            "conocidos": tiempos_conocidos,
            "referencias": tiempos_referencia,
            "fuente": "Función periódica de caudal"
        },

        # ----------------------------------------------
        # 5. HUMEDAD - SEÑAL DE RESPUESTA GRADUAL
        # ----------------------------------------------

        {
            "codigo": "SEN-HUM-005",
            "sensor": "Sensor de humedad ambiental",
            "tipo": "Humedad",
            "ubicacion": "Cámara ambiental",
            "unidad": "%",
            "descripcion": "Sensor para pruebas de humedad.",
            "senal": "Respuesta gradual de humedad",
            "descripcion_senal": (
                "Señal creciente con oscilaciones "
                "para evaluar reconstrucciones."
            ),
            "funcion": lambda t: (
                48
                + 12 * (1 - math.exp(-0.22 * t))
                + 1.5 * math.sin(0.8 * t)
            ),
            "conocidos": tiempos_conocidos,
            "referencias": tiempos_referencia,
            "fuente": "Función de respuesta de humedad"
        }
    ]

    total_sensores = 0
    total_senales = 0
    total_puntos = 0
    total_referencias = 0

    # ==================================================
    # REGISTRAR LOS DATOS
    # ==================================================

    for prueba in pruebas:

        sensor = obtener_o_crear_sensor(
            codigo=prueba["codigo"],
            nombre=prueba["sensor"],
            tipo=prueba["tipo"],
            ubicacion=prueba["ubicacion"],
            unidad=prueba["unidad"],
            descripcion=prueba["descripcion"]
        )

        senal = obtener_o_crear_senal(
            sensor=sensor,
            nombre=prueba["senal"],
            descripcion=prueba["descripcion_senal"]
        )

        puntos, referencias = agregar_puntos(
            senal=senal,
            funcion=prueba["funcion"],
            tiempos_conocidos=prueba["conocidos"],
            tiempos_referencia=prueba["referencias"],
            fuente=prueba["fuente"]
        )

        total_sensores += 1
        total_senales += 1
        total_puntos += puntos
        total_referencias += referencias

        print(
            f"\nSensor: {sensor.codigo}"
            f"\n  Señal: {senal.nombre}"
            f"\n  ID señal: {senal.id}"
            f"\n  Mediciones nuevas: {puntos}"
            f"\n  Referencias nuevas: {referencias}"
        )

    db.session.commit()

    # ==================================================
    # RESUMEN
    # ==================================================

    print("\n============================================")
    print("CARGA DE DATOS DE PRUEBA FINALIZADA")
    print("============================================")
    print(f"Sensores revisados: {total_sensores}")
    print(f"Señales revisadas: {total_senales}")
    print(f"Mediciones nuevas: {total_puntos}")
    print(f"Referencias nuevas: {total_referencias}")
    print("============================================")
    print("No se duplicaron sensores ni señales existentes.")
    print("============================================\n")


if __name__ == "__main__":

    with app.app_context():

        try:
            ejecutar_carga()

        except Exception:
            db.session.rollback()
            raise