
from extensions import db


class PuntoReferencia(db.Model):
    __tablename__ = "punto_referencia"

    id = db.Column(db.Integer, primary_key=True)

    senal_id = db.Column(
        db.Integer,
        db.ForeignKey("senal.id"),
        nullable=False,
        index=True
    )

    tiempo = db.Column(db.Float, nullable=False)
    valor_real = db.Column(db.Float, nullable=False)

    fuente = db.Column(db.String(150))
    observacion = db.Column(db.Text)

    senal = db.relationship(
        "Senal",
        back_populates="puntos_referencia"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "senal_id",
            "tiempo",
            name="uq_punto_referencia_tiempo"
        ),
    )
