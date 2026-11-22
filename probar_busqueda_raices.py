
from backend.metodos.busqueda_raices import (
    metodo_biseccion,
    metodo_newton_raphson,
    metodo_secante
)

# Función de prueba
def f(x):
    return x**2 - 25

def df(x):
    return 2*x


# Bisección
resultado_b = metodo_biseccion(
    f, 0, 10
)

# Newton-Raphson
resultado_n = metodo_newton_raphson(
    f, df, 4
)

# Secante
resultado_s = metodo_secante(
    f, 4, 6
)


# Mostrar resultados
resultados = {
    "Bisección": resultado_b,
    "Newton-Raphson": resultado_n,
    "Secante": resultado_s
}

for nombre, resultado in resultados.items():

    print("\n", nombre)
    print("Raíz:", resultado["solucion"])
    print("Convergió:", resultado["convergio"])
    print("Iteraciones:", resultado["iteraciones"])
    print("Error absoluto:", resultado["error_abs"])
    print("Residuo:", resultado["residual"])
    print("Mensaje:", resultado["mensaje"])
