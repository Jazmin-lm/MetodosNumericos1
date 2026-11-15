
from flask import Flask, render_template, request, jsonify
from backend.metodos.sistemas_lineales import ejecutar_metodos
app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
