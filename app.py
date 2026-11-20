from flask import Flask, render_template, request, jsonify

# Importación de métodos numéricos
from backend.metodos.sistemas_lineales import ejecutar_metodos

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


# ==============================
# INICIAR APLICACIÓN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
