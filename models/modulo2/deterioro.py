from extensions import db


class ComponenteMecanico(db.Model):
    __tablename__ = "componente_mecanico"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    ubicacion = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    unidad_indicador = db.Column(db.String(20), nullable=False)
    umbral_inspeccion = db.Column(db.Float)

    mediciones = db.relationship(
        "MedicionDeterioro",
        back_populates="componente",
        cascade="all, delete-orphan"
    )


class MedicionDeterioro(db.Model):
    __tablename__ = "medicion_deterioro"

    id = db.Column(db.Integer, primary_key=True)

    componente_id = db.Column(
        db.Integer,
        db.ForeignKey("componente_mecanico.id"),
        nullable=False
    )

    tiempo = db.Column(db.Float, nullable=False)
    deterioro = db.Column(db.Float, nullable=False)
    fecha_medicion = db.Column(db.DateTime)
    observacion = db.Column(db.Text)

    componente = db.relationship(
        "ComponenteMecanico",
        back_populates="mediciones"
    )
class AnalisisRaices(db.Model):
    __tablename__ = "analisis_raices"

    id = db.Column(db.Integer, primary_key=True)

    simulacion_id = db.Column(
        db.Integer,
        db.ForeignKey("simulacion.id"),
        nullable=False
    )

    componente_id = db.Column(
        db.Integer,
        db.ForeignKey("componente_mecanico.id"),
        nullable=False
    )

    umbral = db.Column(db.Float, nullable=False)

    parametros_modelo = db.Column(db.JSON, nullable=False)

    componente = db.relationship("ComponenteMecanico")
    simulacion = db.relationship("Simulacion")