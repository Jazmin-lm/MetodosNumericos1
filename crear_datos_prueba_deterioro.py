
from datetime import datetime

from app import app
from extensions import db
from models import ComponenteMecanico, MedicionDeterioro


datos_prueba = [
    # CASOS ORIGINALES
    {
        "codigo": "CMP-PRB-001",
        "nombre": "Rodamiento auxiliar",
        "tipo": "Rodamiento",
        "ubicacion": "Estación inferior",
        "descripcion": "Componente de prueba para deterioro progresivo.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 30.0,
        "mediciones": [(1, 5), (2, 8), (3, 12), (4, 17), (5, 23)]
    },
    {
        "codigo": "CMP-PRB-002",
        "nombre": "Polea motriz",
        "tipo": "Polea",
        "ubicacion": "Estación motriz",
        "descripcion": "Componente de prueba para deterioro moderado.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 40.0,
        "mediciones": [(1, 4), (2, 6), (3, 9), (4, 13), (5, 18)]
    },
    {
        "codigo": "CMP-PRB-003",
        "nombre": "Cable tractor",
        "tipo": "Cable",
        "ubicacion": "Línea de transporte",
        "descripcion": "Componente de prueba para deterioro acelerado.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 50.0,
        "mediciones": [(1, 8), (2, 10), (3, 13), (4, 17), (5, 22)]
    },

    # CASO 4: DETERIORO BAJO Y ESTABLE
    {
        "codigo": "CMP-PRB-004",
        "nombre": "Eje secundario",
        "tipo": "Eje",
        "ubicacion": "Estación de transmisión",
        "descripcion": "Componente con deterioro bajo y crecimiento lento.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 35.0,
        "mediciones": [
            (1, 2), (2, 2.5), (3, 3), (4, 3.2), (5, 3.5)
        ]
    },

    # CASO 5: DETERIORO ACELERADO
    {
        "codigo": "CMP-PRB-005",
        "nombre": "Engranaje principal",
        "tipo": "Engranaje",
        "ubicacion": "Sistema de transmisión",
        "descripcion": "Componente con deterioro progresivo acelerado.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 45.0,
        "mediciones": [
            (1, 6), (2, 9), (3, 15), (4, 24), (5, 36)
        ]
    },

    # CASO 6: PRÓXIMO AL UMBRAL
    {
        "codigo": "CMP-PRB-006",
        "nombre": "Freno de seguridad",
        "tipo": "Freno",
        "ubicacion": "Sistema de frenado",
        "descripcion": "Componente próximo a alcanzar su umbral de inspección.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 40.0,
        "mediciones": [
            (1, 10), (2, 16), (3, 23), (4, 31), (5, 39)
        ]
    },

    # CASO 7: UMBRAL SUPERADO
    {
        "codigo": "CMP-PRB-007",
        "nombre": "Cable de suspensión",
        "tipo": "Cable",
        "ubicacion": "Sistema de suspensión",
        "descripcion": "Componente cuyo deterioro ya superó el umbral establecido.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 50.0,
        "mediciones": [
            (1, 12), (2, 20), (3, 29), (4, 40), (5, 52)
        ]
    },

    # CASO 8: INTERVALOS IRREGULARES
    {
        "codigo": "CMP-PRB-008",
        "nombre": "Rodillo de retorno",
        "tipo": "Rodillo",
        "ubicacion": "Sistema de transporte",
        "descripcion": "Componente con mediciones tomadas en intervalos irregulares.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 55.0,
        "mediciones": [
            (1, 4), (2.5, 8), (4, 15), (7, 26), (10, 42)
        ]
    },

    # CASO 9: PEQUEÑAS FLUCTUACIONES
    {
        "codigo": "CMP-PRB-009",
        "nombre": "Soporte estructural",
        "tipo": "Soporte",
        "ubicacion": "Estructura lateral",
        "descripcion": "Componente con pequeñas fluctuaciones en sus mediciones.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 45.0,
        "mediciones": [
            (1, 28), (2, 27), (3, 29), (4, 28), (5, 30)
        ]
    }
]


with app.app_context():

    try:
        creados = 0
        existentes = 0

        for dato in datos_prueba:

            componente = ComponenteMecanico.query.filter_by(
                codigo=dato["codigo"]
            ).first()

            if componente is None:

                componente = ComponenteMecanico(
                    codigo=dato["codigo"],
                    nombre=dato["nombre"],
                    tipo=dato["tipo"],
                    ubicacion=dato["ubicacion"],
                    descripcion=dato["descripcion"],
                    unidad_indicador=dato["unidad_indicador"],
                    umbral_inspeccion=dato["umbral_inspeccion"]
                )

                db.session.add(componente)
                db.session.flush()

                for tiempo, deterioro in dato["mediciones"]:

                    medicion = MedicionDeterioro(
                        componente_id=componente.id,
                        tiempo=float(tiempo),
                        deterioro=float(deterioro),
                        fecha_medicion=datetime.now(),
                        observacion="Dato de prueba generado automáticamente"
                    )

                    db.session.add(medicion)

                creados += 1
                print(f"Creado: {componente.codigo} - {componente.nombre}")

            else:
                existentes += 1
                print(f"Ya existe: {componente.codigo}. No se duplicó.")

        db.session.commit()

        print("\n====================================")
        print("     RESUMEN DE DATOS DE PRUEBA")
        print("====================================")
        print(f"Componentes nuevos: {creados}")
        print(f"Componentes existentes: {existentes}")
        print(f"Total de casos contemplados: {len(datos_prueba)}")
        print("Datos registrados correctamente.")

    except Exception as error:
        db.session.rollback()
        print(f"Error al registrar los datos: {error}")
