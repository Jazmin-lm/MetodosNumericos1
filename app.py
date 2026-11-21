from flask import Flask, render_template, request, jsonify
from datetime import datetime
import math

# Importación de métodos numéricos
from backend.metodos.sistemas_lineales import (
    ejecutar_metodos,
    ejecutar_escenario
)
# Importación de configuración y extensiones
from config import Config
from extensions import db, migrate

app = Flask(__name__)

# Configuración de la aplicación
app.config.from_object(Config)

# Inicialización de PostgreSQL y migraciones
db.init_app(app)
migrate.init_app(app, db)

# Importar modelos para que Flask-Migrate los detecte
from models import *


# ==============================
# RUTAS PRINCIPALES
# ==============================

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/detencion")
def detencion():
    return render_template("detencion.html")


@app.route("/deterioro")
def deterioro():
    return render_template("deterioro.html")


@app.route("/oscilaciones")
def oscilaciones():
    return render_template("oscilaciones.html")


@app.route("/sensores")
def sensores():
    return render_template("sensores.html")


@app.route("/historial")
def historial():
    return render_template("historial.html")


# ==============================
# EJECUCIÓN DE MÉTODOS NUMÉRICOS
# ==============================

@app.route("/ejecutar-sistema", methods=["POST"])
def ejecutar_sistema():
    try:
        datos = request.get_json()

        A = datos["A"]
        b = datos["b"]
        tolerancia = float(datos["tolerancia"])
        max_iter = int(datos["max_iter"])
        x0 = [float(datos["x0"])] * len(b)

        resultados = ejecutar_metodos(
            A, b, tolerancia, max_iter, x0
        )

        return jsonify({
            "exito": True,
            "resultados": resultados
        })

    except Exception as e:
        return jsonify({
            "exito": False,
            "error": str(e)
        }), 400


# ==============================
# VERIFICACIÓN DE POSTGRESQL
# ==============================

@app.route("/verificar-db")
def verificar_db():
    try:
        with db.engine.connect() as conexion:
            conexion.exec_driver_sql("SELECT 1")

        return jsonify({
            "mensaje": "Conexión con PostgreSQL exitosa"
        }), 200

    except Exception as error:
        return jsonify({
            "mensaje": "Error al conectar con PostgreSQL",
            "detalle": str(error)
        }), 500

# ==========================================
# API: ESCENARIOS DE SISTEMAS LINEALES
# ==========================================

@app.route("/api/sistemas-lineales/escenarios", methods=["GET"])
def listar_escenarios_sistemas():
    try:
        escenarios = (
            Escenario.query
            .join(CasoEstudio)
            .filter(CasoEstudio.modulo == "deterioro")
            .order_by(Escenario.id.asc())
            .all()
        )

        resultado = []

        for escenario in escenarios:
            parametros = escenario.parametros_json or {}

            resultado.append({
                "id": escenario.id,
                "tipo": escenario.tipo,
                "descripcion": parametros.get(
                    "descripcion",
                    "Escenario de prueba"
                ),
                "fuente_datos": escenario.fuente_datos
            })

        return jsonify(resultado), 200

    except Exception:
        app.logger.exception("Error al listar escenarios de sistemas lineales")

        return jsonify({
            "error": "No se pudieron cargar los escenarios."
        }), 500
        # ==========================================
# API: EJECUTAR SISTEMAS LINEALES
# ==========================================

@app.route("/api/sistemas-lineales/ejecutar", methods=["POST"])
def ejecutar_sistemas_lineales():

    datos = request.get_json(silent=True) or {}

    # --------------------------------------
    # 1. Validar los datos recibidos
    # --------------------------------------

    if datos.get("escenario_id") is None:
        return jsonify({
            "error": "Debes seleccionar un escenario."
        }), 400

    try:
        escenario_id = int(datos["escenario_id"])
        tolerancia = float(datos.get("tolerancia", 1e-6))
        max_iter = int(datos.get("max_iter", 100))

        if not math.isfinite(tolerancia) or tolerancia <= 0:
            return jsonify({
                "error": "La tolerancia debe ser un número positivo y válido."
            }), 400

        if max_iter < 1:
            return jsonify({
                "error": "El máximo de iteraciones debe ser al menos 1."
            }), 400

    except (ValueError, TypeError, OverflowError):
        return jsonify({
            "error": "Verifica los valores numéricos enviados."
        }), 400

    # --------------------------------------
    # 2. Buscar el escenario seleccionado
    # --------------------------------------

    escenario = db.session.get(Escenario, escenario_id)

    if not escenario:
        return jsonify({
            "error": "El escenario seleccionado no existe."
        }), 404

    if escenario.caso.modulo != "deterioro":
        return jsonify({
            "error": "El escenario no pertenece al módulo de deterioro."
        }), 400

    try:

        # --------------------------------------
        # 3. Ejecutar los cuatro métodos
        # --------------------------------------

        resultado = ejecutar_escenario(
            escenario.tipo,
            tolerancia,
            max_iter
        )

        resultados_metodos = resultado["resultados"]

        # --------------------------------------
        # 4. Crear el registro de simulación
        # --------------------------------------

        simulacion = Simulacion(
            escenario_id=escenario.id,
            usuario_equipo=(
                str(datos.get("usuario_equipo") or "").strip() or None
            ),
            estado="COMPLETADA"
        )

        db.session.add(simulacion)
        db.session.flush()

        # --------------------------------------
        # 5. Guardar cada método ejecutado
        # --------------------------------------

        for nombre_metodo, datos_metodo in resultados_metodos.items():

            ejecucion = EjecucionMetodo(
                simulacion_id=simulacion.id,
                metodo=nombre_metodo,
                tolerancia=tolerancia,
                paso=None,
                max_iter=(
                    None if nombre_metodo.upper() == "LU"
                    else max_iter
                ),
                convergio=datos_metodo.get("convergio"),
                tiempo_ms=datos_metodo.get("tiempo_ms")
            )

            db.session.add(ejecucion)
            db.session.flush()

            # --------------------------------------
            # 6. Guardar el historial de iteraciones
            # --------------------------------------

            historial = datos_metodo.get("historial", [])

            for registro in historial:

                iteracion = IteracionResultado(
                    ejecucion_id=ejecucion.id,
                    numero=registro.get("iteracion"),
                    aproximacion_json=registro.get("aproximacion"),
                    residual=registro.get("residual"),
                    error_abs=registro.get("error"),
                    error_rel=None
                )

                db.session.add(iteracion)

            # --------------------------------------
            # 7. Guardar el resumen de cada método
            # --------------------------------------

            metricas = {
                "residual": datos_metodo.get("residual"),
                "error_absoluto": datos_metodo.get("error_absoluto"),
                "error_relativo": datos_metodo.get("error_relativo"),
                "numero_condicion": resultado.get("numero_condicion")
            }

            if datos_metodo.get("convergio"):
                interpretacion = (
                    f"El método {nombre_metodo} alcanzó la convergencia "
                    f"con la tolerancia establecida."
                )
            else:
                interpretacion = (
                    f"El método {nombre_metodo} no alcanzó la convergencia "
                    f"con el máximo de iteraciones establecido."
                )

            resumen = ResultadoResumen(
                ejecucion_id=ejecucion.id,
                referencia="Solución exacta de referencia",
                valor_json=datos_metodo.get("solucion"),
                metrica_error_json=metricas,
                interpretacion=interpretacion
            )

            db.session.add(resumen)

        # --------------------------------------
        # 8. Confirmar todos los registros
        # --------------------------------------

        db.session.commit()

        # --------------------------------------
        # 9. Devolver los resultados al frontend
        # --------------------------------------

        return jsonify({
            "exito": True,
            "mensaje": "Simulación ejecutada y guardada correctamente.",
            "simulacion_id": simulacion.id,
            "escenario": resultado.get("escenario"),
            "matriz": resultado.get("A"),
            "vector_b": resultado.get("b"),
            "solucion_exacta": resultado.get("solucion_exacta"),
            "numero_condicion": resultado.get("numero_condicion"),
            "resultados": resultados_metodos
        }), 200

    except Exception:
        db.session.rollback()

        app.logger.exception(
            "Error al ejecutar o guardar los sistemas lineales"
        )

        return jsonify({
            "exito": False,
            "error": "Ocurrió un error al ejecutar o guardar la simulación."
        }), 500
# ==========================================
# API: COMPONENTES MECÁNICOS
# ==========================================

@app.route("/api/componentes", methods=["GET"])
def listar_componentes():
    componentes = ComponenteMecanico.query.order_by(
        ComponenteMecanico.id.desc()
    ).all()

    mediciones = MedicionDeterioro.query.order_by(
        MedicionDeterioro.tiempo.asc()
    ).all()

    ultima_medicion = {}

    for medicion in mediciones:
        ultima_medicion[medicion.componente_id] = medicion

    resultado = []

    for componente in componentes:
        medicion = ultima_medicion.get(componente.id)

        resultado.append({
            "id": componente.id,
            "codigo": componente.codigo,
            "nombre": componente.nombre,
            "tipo": componente.tipo,
            "ubicacion": componente.ubicacion,
            "descripcion": componente.descripcion,
            "unidad_indicador": componente.unidad_indicador,
            "umbral_inspeccion": componente.umbral_inspeccion,
            "ultimo_deterioro": (
                medicion.deterioro if medicion else None
            ),
            "ultimo_tiempo": (
                medicion.tiempo if medicion else None
            )
        })

    return jsonify(resultado)


# ==========================================
# API: REGISTRAR COMPONENTE
# ==========================================

@app.route("/api/componentes", methods=["POST"])
def registrar_componente():
    datos = request.get_json(silent=True) or {}

    campos_obligatorios = [
        "codigo",
        "nombre",
        "tipo",
        "unidad_indicador",
        "umbral_inspeccion"
    ]

    for campo in campos_obligatorios:
        if datos.get(campo) is None or str(datos[campo]).strip() == "":
            return jsonify({
                "error": f"El campo {campo} es obligatorio."
            }), 400

    codigo = str(datos["codigo"]).strip()

    existente = ComponenteMecanico.query.filter_by(
        codigo=codigo
    ).first()

    if existente:
        return jsonify({
            "error": "Ya existe un componente con ese código."
        }), 409

    try:
        umbral = float(datos["umbral_inspeccion"])

        if umbral < 0:
            return jsonify({
                "error": "El umbral no puede ser negativo."
            }), 400

        nuevo = ComponenteMecanico(
            codigo=codigo,
            nombre=str(datos["nombre"]).strip(),
            tipo=str(datos["tipo"]).strip(),
            ubicacion=str(datos.get("ubicacion") or "").strip(),
            descripcion=str(datos.get("descripcion") or "").strip(),
            unidad_indicador=str(datos["unidad_indicador"]).strip(),
            umbral_inspeccion=umbral
        )

        db.session.add(nuevo)
        db.session.commit()

        return jsonify({
            "mensaje": "Componente registrado correctamente.",
            "id": nuevo.id
        }), 201

    except ValueError:
        return jsonify({
            "error": "El umbral debe ser un número válido."
        }), 400

    except Exception:
        db.session.rollback()
        app.logger.exception("Error al registrar componente")

        return jsonify({
            "error": "Ocurrió un error al guardar el componente."
        }), 500


# ==========================================
# API: RESUMEN DEL PANEL PRINCIPAL
# ==========================================

@app.route("/api/dashboard/deterioro", methods=["GET"])
def dashboard_deterioro():
    componentes = ComponenteMecanico.query.all()

    mediciones = MedicionDeterioro.query.order_by(
        MedicionDeterioro.tiempo.asc()
    ).all()

    ultima_medicion = {}

    for medicion in mediciones:
        ultima_medicion[medicion.componente_id] = medicion

    requieren_inspeccion = 0

    for componente in componentes:
        medicion = ultima_medicion.get(componente.id)

        if (
            medicion
            and medicion.deterioro >= componente.umbral_inspeccion
        ):
            requieren_inspeccion += 1

    fecha_ultima = None

    fechas = [
        m.fecha_medicion
        for m in mediciones
        if m.fecha_medicion is not None
    ]

    if fechas:
        fecha_ultima = max(fechas).strftime("%d/%m/%Y")

    return jsonify({
        "total_componentes": len(componentes),
        "total_mediciones": len(mediciones),
        "requieren_inspeccion": requieren_inspeccion,
        "ultima_actualizacion": fecha_ultima or "--",
        "componentes": [
            {
                "id": c.id,
                "codigo": c.codigo,
                "nombre": c.nombre,
                "tipo": c.tipo,
                "ubicacion": c.ubicacion,
                "unidad_indicador": c.unidad_indicador,
                "umbral_inspeccion": c.umbral_inspeccion,
                "ultimo_deterioro": (
                    ultima_medicion[c.id].deterioro
                    if c.id in ultima_medicion else None
                )
            }
            for c in componentes
        ],
        "mediciones": [
            {
                "componente_id": m.componente_id,
                "tiempo": m.tiempo,
                "deterioro": m.deterioro
            }
            for m in mediciones
        ]
    })

# ==========================================
# API: LISTAR MEDICIONES
# ==========================================

@app.route("/api/mediciones", methods=["GET"])
def listar_mediciones():

    mediciones = MedicionDeterioro.query.order_by(
        MedicionDeterioro.fecha_medicion.desc(),
        MedicionDeterioro.id.desc()
    ).all()

    resultado = []

    for medicion in mediciones:
        componente = ComponenteMecanico.query.get(
            medicion.componente_id
        )

        resultado.append({
            "id": medicion.id,
            "componente_id": medicion.componente_id,
            "codigo": componente.codigo,
            "componente": componente.nombre,
            "tiempo": medicion.tiempo,
            "deterioro": medicion.deterioro,
            "fecha_medicion": (
                medicion.fecha_medicion.strftime("%d/%m/%Y %H:%M")
                if medicion.fecha_medicion else "--"
            ),
            "observacion": medicion.observacion or ""
        })

    return jsonify(resultado)


# ==========================================
# API: REGISTRAR MEDICIÓN
# ==========================================

@app.route("/api/mediciones", methods=["POST"])
def registrar_medicion():

    datos = request.get_json(silent=True) or {}

    campos = ["componente_id", "tiempo", "deterioro"]

    for campo in campos:
        if datos.get(campo) is None or str(datos[campo]).strip() == "":
            return jsonify({
                "error": f"El campo {campo} es obligatorio."
            }), 400

    try:
        componente_id = int(datos["componente_id"])
        tiempo = float(datos["tiempo"])
        deterioro = float(datos["deterioro"])

        if tiempo < 0 or deterioro < 0:
            return jsonify({
                "error": "El tiempo y el deterioro no pueden ser negativos."
            }), 400

        componente = db.session.get(
            ComponenteMecanico,
            componente_id
        )

        if not componente:
            return jsonify({
                "error": "El componente seleccionado no existe."
            }), 404

        nueva_medicion = MedicionDeterioro(
            componente_id=componente_id,
            tiempo=tiempo,
            deterioro=deterioro,
            fecha_medicion=datetime.now(),
            observacion=str(
                datos.get("observacion") or ""
            ).strip()
        )

        db.session.add(nueva_medicion)
        db.session.commit()

        return jsonify({
            "mensaje": "Medición registrada correctamente.",
            "id": nueva_medicion.id
        }), 201

    except (ValueError, TypeError):
        return jsonify({
            "error": "Verifica que los valores numéricos sean válidos."
        }), 400

    except Exception:
        db.session.rollback()
        app.logger.exception("Error al registrar medición")

        return jsonify({
            "error": "Ocurrió un error al guardar la medición."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
