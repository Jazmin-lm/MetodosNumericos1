
from datetime import datetime, timezone
from extensions import db

class CasoEstudio(db.Model):
    __tablename__ = "caso_estudio"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo_version = db.Column(db.String(20), nullable=False)

    modulo = db.Column(db.String(30), nullable=False)

    escenarios = db.relationship(
        "Escenario",
        back_populates="caso",
        cascade="all, delete-orphan"
    )


class Escenario(db.Model):
    __tablename__ = "escenario"

    id = db.Column(db.Integer, primary_key=True)
    caso_id = db.Column(
        db.Integer,
        db.ForeignKey("caso_estudio.id"),
        nullable=False
    )
    tipo = db.Column(db.String(30), nullable=False)
    parametros_json = db.Column(db.JSON, nullable=False)
    fuente_datos = db.Column(db.Text)

    caso = db.relationship("CasoEstudio", back_populates="escenarios")

    simulaciones = db.relationship(
        "Simulacion",
        back_populates="escenario"
    )


class Simulacion(db.Model):
    __tablename__ = "simulacion"

    id = db.Column(db.Integer, primary_key=True)
    escenario_id = db.Column(
        db.Integer,
        db.ForeignKey("escenario.id"),
        nullable=False
    )
    fecha = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    usuario_equipo = db.Column(db.String(100))
    estado = db.Column(db.String(30), nullable=False)

    escenario = db.relationship(
        "Escenario",
        back_populates="simulaciones"
    )

    ejecuciones = db.relationship(
        "EjecucionMetodo",
        back_populates="simulacion"
    )


class EjecucionMetodo(db.Model):
    __tablename__ = "ejecucion_metodo"

    id = db.Column(db.Integer, primary_key=True)
    simulacion_id = db.Column(
        db.Integer,
        db.ForeignKey("simulacion.id"),
        nullable=False
    )
    metodo = db.Column(db.String(100), nullable=False)
    tolerancia = db.Column(db.Float)
    paso = db.Column(db.Float)
    max_iter = db.Column(db.Integer)
    convergio = db.Column(db.Boolean)
    tiempo_ms = db.Column(db.Float)

    simulacion = db.relationship(
        "Simulacion",
        back_populates="ejecuciones"
    )

    iteraciones = db.relationship(
        "IteracionResultado",
        back_populates="ejecucion"
    )

    resumenes = db.relationship(
        "ResultadoResumen",
        back_populates="ejecucion"
    )


class IteracionResultado(db.Model):
    __tablename__ = "iteracion_resultado"

    id = db.Column(db.Integer, primary_key=True)
    ejecucion_id = db.Column(
        db.Integer,
        db.ForeignKey("ejecucion_metodo.id"),
        nullable=False
    )
    numero = db.Column(db.Integer, nullable=False)
    aproximacion_json = db.Column(db.JSON)
    residual = db.Column(db.Float)
    error_abs = db.Column(db.Float)
    error_rel = db.Column(db.Float)

    ejecucion = db.relationship(
        "EjecucionMetodo",
        back_populates="iteraciones"
    )


class ResultadoResumen(db.Model):
    __tablename__ = "resultado_resumen"

    id = db.Column(db.Integer, primary_key=True)
    ejecucion_id = db.Column(
        db.Integer,
        db.ForeignKey("ejecucion_metodo.id"),
        nullable=False
    )
    referencia = db.Column(db.Text)
    valor_json = db.Column(db.JSON)
    metrica_error_json = db.Column(db.JSON)
    interpretacion = db.Column(db.Text)

    ejecucion = db.relationship(
        "EjecucionMetodo",
        back_populates="resumenes"
    )
