
from datetime import datetime

from app import app
from extensions import db
from models import ComponenteMecanico, MedicionDeterioro


datos_prueba = [
    {
        "codigo": "CMP-PRB-001",
        "nombre": "Rodamiento auxiliar",
        "tipo": "Rodamiento",
        "ubicacion": "Estación inferior",
        "descripcion": "Componente de prueba para deterioro progresivo.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 30.0,
        "mediciones": [
            (1, 5), (2, 8), (3, 12), (4, 17), (5, 23)
        ]
    },
    {
        "codigo": "CMP-PRB-002",
        "nombre": "Polea motriz",
        "tipo": "Polea",
        "ubicacion": "Estación motriz",
        "descripcion": "Componente de prueba para deterioro moderado.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 40.0,
        "mediciones": [
            (1, 4), (2, 6), (3, 9), (4, 13), (5, 18)
        ]
    },
    {
        "codigo": "CMP-PRB-003",
        "nombre": "Cable tractor",
        "tipo": "Cable",
        "ubicacion": "Línea de transporte",
        "descripcion": "Componente de prueba para deterioro acelerado.",
        "unidad_indicador": "%",
        "umbral_inspeccion": 50.0,
        "mediciones": [
            (1, 8), (2, 10), (3, 13), (4, 17), (5, 22)
        ]
    }
]


with app.app_context():

    try:
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

                print(f"Creado: {componente.codigo}")

            else:
                print(f"Ya existe: {componente.codigo}. No se duplicó.")

        db.session.commit()

        print("\nDatos de prueba registrados correctamente.")

    except Exception as error:
        db.session.rollback()
        print(f"Error al registrar los datos: {error}")
