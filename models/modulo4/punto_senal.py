
from extensions import db


class PuntoSenal(db.Model):
    __tablename__ = "punto_senal"

    id = db.Column(db.Integer, primary_key=True)

    senal_id = db.Column(
        db.Integer,
        db.ForeignKey("senal.id"),
        nullable=False,
        index=True
    )

    tiempo = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)

    observacion = db.Column(db.Text)

    senal = db.relationship(
        "Senal",
        back_populates="puntos"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "senal_id",
            "tiempo",
            name="uq_punto_senal_tiempo"
        ),
    )
