
from extensions import db


class Sensor(db.Model):
    __tablename__ = "sensor"

    id = db.Column(db.Integer, primary_key=True)

    codigo = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    ubicacion = db.Column(db.String(150))
    unidad_medida = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.Text)

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    senales = db.relationship(
        "Senal",
        back_populates="sensor",
        cascade="all, delete-orphan"
    )
