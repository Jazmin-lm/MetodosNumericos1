
from extensions import db


class DetalleReconstruccion(db.Model):
    __tablename__ = "detalle_reconstruccion"

    id = db.Column(db.Integer, primary_key=True)

    reconstruccion_id = db.Column(
        db.Integer,
        db.ForeignKey("reconstruccion.id"),
        nullable=False,
        index=True
    )

    metodo = db.Column(
        db.String(50),
        nullable=False
    )

    valores_reconstruidos_json = db.Column(
        db.JSON,
        nullable=False
    )

    metricas_json = db.Column(db.JSON)

    tiempo_ms = db.Column(db.Float)

    convergio = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    observacion = db.Column(db.Text)

    reconstruccion = db.relationship(
        "Reconstruccion",
        back_populates="detalles"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "reconstruccion_id",
            "metodo",
            name="uq_reconstruccion_metodo"
        ),
    )
