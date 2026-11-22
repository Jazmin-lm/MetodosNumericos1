
from datetime import datetime, timezone

from extensions import db


class Senal(db.Model):
    __tablename__ = "senal"

    id = db.Column(db.Integer, primary_key=True)

    sensor_id = db.Column(
        db.Integer,
        db.ForeignKey("sensor.id"),
        nullable=False,
        index=True
    )

    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

    origen = db.Column(
        db.String(50),
        nullable=False,
        default="REGISTRO_MANUAL"
    )

    fecha_creacion = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="REGISTRADA"
    )

    sensor = db.relationship(
        "Sensor",
        back_populates="senales"
    )

    puntos = db.relationship(
        "PuntoSenal",
        back_populates="senal",
        cascade="all, delete-orphan",
        order_by="PuntoSenal.tiempo"
    )

    puntos_referencia = db.relationship(
        "PuntoReferencia",
        back_populates="senal",
        cascade="all, delete-orphan",
        order_by="PuntoReferencia.tiempo"
    )

    reconstrucciones = db.relationship(
        "Reconstruccion",
        back_populates="senal",
        cascade="all, delete-orphan"
    )
