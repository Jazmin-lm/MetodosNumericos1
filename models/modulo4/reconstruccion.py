
from datetime import datetime, timezone

from extensions import db


class Reconstruccion(db.Model):
    __tablename__ = "reconstruccion"

    id = db.Column(db.Integer, primary_key=True)

    senal_id = db.Column(
        db.Integer,
        db.ForeignKey("senal.id"),
        nullable=False,
        index=True
    )

    escenario_id = db.Column(
        db.Integer,
        db.ForeignKey("escenario.id"),
        nullable=True
    )

    simulacion_id = db.Column(
        db.Integer,
        db.ForeignKey("simulacion.id"),
        nullable=True
    )

    fecha = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="COMPLETADA"
    )

    parametros_json = db.Column(db.JSON)
    metricas_globales_json = db.Column(db.JSON)

    observacion = db.Column(db.Text)

    senal = db.relationship(
        "Senal",
        back_populates="reconstrucciones"
    )

    escenario = db.relationship("Escenario")
    simulacion = db.relationship("Simulacion")

    detalles = db.relationship(
        "DetalleReconstruccion",
        back_populates="reconstruccion",
        cascade="all, delete-orphan"
    )
