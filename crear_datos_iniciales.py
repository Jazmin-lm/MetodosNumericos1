
from app import app
from extensions import db
from models import CasoEstudio

with app.app_context():

    casos = [
        ("Detención de emergencia", "1.0"),
        ("Deterioro mecánico", "1.0"),
        ("Oscilaciones por viento", "1.0"),
        ("Reconstrucción de sensores", "1.0")
    ]

    for nombre, version in casos:
        existe = CasoEstudio.query.filter_by(
            nombre=nombre
        ).first()

        if not existe:
            nuevo = CasoEstudio(
                nombre=nombre,
                modelo_version=version
            )
            db.session.add(nuevo)

    db.session.commit()

    print("Casos de estudio registrados correctamente")
