
from backend.metodos.modelo_deterioro import ajustar_modelo_cuadratico

# Mediciones de prueba
tiempos = [0, 1, 2, 3, 4]
deterioros = [2, 3.5, 6, 9.5, 14]

# Ajustar modelo
resultado = ajustar_modelo_cuadratico(
    tiempos,
    deterioros
)

print("MODELO DE DETERIORO")
print("-------------------------")

print("D0:", resultado["D0"])
print("Alpha:", resultado["alpha"])
print("Beta:", resultado["beta"])

print("Modelo:", resultado["modelo"])

print("Error cuadrático:", resultado["error_cuadratico"])

print("\nPredicción en t = 5:")
print(resultado["funcion"](5))

print("\nDerivada en t = 5:")
print(resultado["derivada"](5))
