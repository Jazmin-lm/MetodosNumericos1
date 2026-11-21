
from backend.metodos.sistemas_lineales import ejecutar_escenario

escenarios = [
    "NORMAL",
    "ESTRES",
    "MAL_CONDICIONADO"
]

for tipo in escenarios:

    print("\n" + "=" * 55)
    print("ESCENARIO:", tipo)
    print("=" * 55)

    resultado = ejecutar_escenario(tipo)

    print("Matriz A:")
    for fila in resultado["A"]:
        print(fila)

    print("\nVector b:")
    print(resultado["b"])

    print("\nSolución exacta:")
    print(resultado["solucion_exacta"])

    print("\nNúmero de condición:")
    print(resultado["numero_condicion"])

    print("\nCOMPARACIÓN DE MÉTODOS")

    for metodo, datos in resultado["resultados"].items():

        print("\nMétodo:", metodo)
        print("Convergió:", datos["convergio"])
        print("Solución:", datos["solucion"])
        print("Iteraciones:", datos.get("iteraciones"))
        print("Residuo:", datos.get("residual"))
        print("Error absoluto:", datos.get("error_absoluto"))
        print("Error relativo:", datos.get("error_relativo"))
        print("Tiempo (ms):", datos.get("tiempo_ms"))
