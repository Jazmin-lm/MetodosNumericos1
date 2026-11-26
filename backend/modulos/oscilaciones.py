"""
SIMTELE-RISK | Módulo 3: Oscilaciones por viento
Modelo masa-resorte-amortiguador resuelto con RK2 y RK4.
Incluye integración compuesta, Romberg, validación y sensibilidad.
Los parámetros son sintéticos y de uso académico.
"""
from dataclasses import dataclass, asdict
import math


@dataclass
class Caso:
    nombre: str
    descripcion: str
    m: float
    c: float
    k: float
    F0: float
    omega: float
    phi: float
    x0: float
    v0: float
    T: float
    N: int


CASOS = {
    "normal": Caso("NORMAL", "Parámetros nominales: fuerza moderada y amortiguamiento suficiente.",
                   800, 900, 12000, 500, 1.8, 0, .02, 0, 20, 512),
    "stress": Caso("ESTRÉS", "Mayor fuerza y frecuencia de excitación, con menor amortiguamiento.",
                   800, 420, 12000, 1800, 3.2, 0, .02, 0, 20, 512),
    "ill": Caso("MAL CONDICIONADO", "Excitación cercana a la frecuencia natural y amortiguamiento reducido.",
                800, 100, 12000, 500, .995 * math.sqrt(12000 / 800), 0, .02, 0, 20, 1024),
}


def _fuerza(t, p):
    return p.F0 * math.sin(p.omega * t + p.phi)


def _derivada(t, y, p):
    x, v = y
    return v, (_fuerza(t, p) - p.c * v - p.k * x) / p.m


def _suma(y, ks, h):
    return tuple(y[i] + h * sum(peso * k[i] for peso, k in ks) for i in range(2))


def integrar(p, metodo="RK4", n=None):
    n = int(n or p.N)
    h = p.T / n
    t = 0.0
    y = (p.x0, p.v0)
    salida = [{"t": 0.0, "x": y[0], "v": y[1]}]
    for i in range(n):
        k1 = _derivada(t, y, p)
        if metodo.upper() == "RK2":
            k2 = _derivada(t + h / 2, _suma(y, [(0.5, k1)], h), p)
            y = _suma(y, [(1.0, k2)], h)
        else:
            k2 = _derivada(t + h / 2, _suma(y, [(0.5, k1)], h), p)
            k3 = _derivada(t + h / 2, _suma(y, [(0.5, k2)], h), p)
            k4 = _derivada(t + h, _suma(y, [(1.0, k3)], h), p)
            y = _suma(y, [(1/6, k1), (1/3, k2), (1/3, k3), (1/6, k4)], h)
        t = (i + 1) * h
        salida.append({"t": t, "x": y[0], "v": y[1]})
    return salida


def trapecio(valores, h):
    return h * (valores[0] / 2 + sum(valores[1:-1]) + valores[-1] / 2)


def simpson_13(valores, h):
    n = len(valores) - 1
    if n % 2:
        raise ValueError("Simpson 1/3 requiere un número par de subintervalos.")
    return h / 3 * (valores[0] + valores[-1]
                    + 4 * sum(valores[1:-1:2])
                    + 2 * sum(valores[2:-1:2]))


def romberg(valores, h):
    n = len(valores) - 1
    niveles = int(math.log2(n)) + 1
    if 2 ** (niveles - 1) != n:
        raise ValueError("Romberg requiere un número de pasos potencia de dos.")
    tabla = [[0.0] * niveles for _ in range(niveles)]
    for nivel in range(niveles):
        salto = 2 ** (niveles - 1 - nivel)
        muestra = valores[::salto]
        tabla[nivel][0] = trapecio(muestra, h * salto)
        for orden in range(1, nivel + 1):
            tabla[nivel][orden] = (
                tabla[nivel][orden - 1]
                + (tabla[nivel][orden - 1] - tabla[nivel - 1][orden - 1]) / (4 ** orden - 1)
            )
    return tabla[-1][-1], tabla


def referencia_libre(p, t):
    """Solución analítica subamortiguada cuando la fuerza externa es cero."""
    w0 = math.sqrt(p.k / p.m)
    zeta = p.c / (2 * math.sqrt(p.m * p.k))
    if zeta >= 1:
        raise ValueError("La validación analítica libre requiere régimen subamortiguado.")
    wd = w0 * math.sqrt(1 - zeta * zeta)
    a = zeta * w0
    c1 = p.x0
    c2 = (p.v0 + a * c1) / wd
    return math.exp(-a * t) * (c1 * math.cos(wd * t) + c2 * math.sin(wd * t))


def validar_parametros(datos):
    claves = ("m", "c", "k", "F0", "omega", "phi", "x0", "v0", "T", "N")
    p = {clave: datos.get(clave) for clave in claves}
    for clave in claves:
        if clave not in p:
            raise ValueError(f"Falta el parámetro {clave}.")
        try:
            p[clave] = float(p[clave])
        except (TypeError, ValueError):
            raise ValueError(f"El parámetro {clave} debe ser numérico.")
        if not math.isfinite(p[clave]):
            raise ValueError(f"El parámetro {clave} debe ser finito.")
    if p["m"] <= 0 or p["k"] <= 0 or p["c"] < 0 or p["T"] <= 0:
        raise ValueError("La masa, rigidez y tiempo deben ser positivos; el amortiguamiento no puede ser negativo.")
    if p["N"] < 32 or not p["N"].is_integer() or p["N"] > 8192:
        raise ValueError("N debe ser un entero entre 32 y 8192.")
    if int(p["N"]) % 2:
        raise ValueError("N debe ser par para aplicar Simpson 1/3.")
    if int(p["N"]) & (int(p["N"]) - 1):
        raise ValueError("N debe ser potencia de dos para aplicar Romberg.")
    p["N"] = int(p["N"])
    return Caso("PERSONALIZADO", "Parámetros definidos por el usuario.", **p)


def _max_abs(valores):
    return max(abs(v) for v in valores)


def ejecutar(datos):
    p = validar_parametros(datos)
    rk2 = integrar(p, "RK2")
    rk4 = integrar(p, "RK4")
    referencia = integrar(p, "RK4", p.N * 4)
    h = p.T / p.N
    xs = [q["x"] for q in rk4]
    vs = [q["v"] for q in rk4]
    cuadrados = [x * x for x in xs]
    error_ref = max(abs(rk4[i]["x"] - referencia[i * 4]["x"]) for i in range(p.N + 1))
    error_24 = max(abs(rk2[i]["x"] - rk4[i]["x"]) for i in range(p.N + 1))
    itrap = trapecio(cuadrados, h)
    isimp = simpson_13(cuadrados, h)
    iromb, tabla = romberg(cuadrados, h)

    perturbado = Caso(**asdict(p))
    perturbado.m *= 1.01
    perturbado.c *= 1.01
    perturbado.k *= 1.01
    trayectoria_perturbada = integrar(perturbado, "RK4")
    delta = max(abs(rk4[i]["x"] - trayectoria_perturbada[i]["x"]) for i in range(p.N + 1))
    max_x = _max_abs(xs)
    max_v = _max_abs(vs)
    amplification = delta / (0.01 * max(max_x, 1e-12))

    # Validación independiente de la implementación: vibración libre, F0 = 0.
    libre = Caso(**asdict(p))
    libre.F0 = 0.0
    trayectoria_libre = integrar(libre, "RK4")
    error_analitico = max(abs(q["x"] - referencia_libre(libre, q["t"])) for q in trayectoria_libre)

    # Se devuelve la trayectoria completa para que la gráfica y el CSV
    # conserven todos los puntos calculados por RK4.
    puntos = rk4

    return {
        "ok": True,
        "escenario": p.nombre,
        "descripcion": p.descripcion,
        "parametros": asdict(p),
        "paso_h": h,
        "subintervalos": p.N,
        "metricas": {
            "maximo_abs_desplazamiento_m": max_x,
            "maxima_abs_velocidad_m_s": max_v,
            "integral_trapecio": itrap,
            "integral_simpson": isimp,
            "integral_romberg": iromb,
            "error_max_RK2_vs_RK4_m": error_24,
            "error_max_RK4_vs_refinado_m": error_ref,
            "validacion_analitica_libre_m": error_analitico,
            "diferencia_maxima_sensibilidad_m": delta,
            "indicador_sensibilidad": amplification,
        },
        "comparacion": [
            {"metodo": "Trapecio compuesto", "resultado": itrap, "error": abs(itrap - iromb)},
            {"metodo": "Simpson 1/3 compuesto", "resultado": isimp, "error": abs(isimp - iromb)},
            {"metodo": "Romberg", "resultado": iromb, "error": 0.0},
        ],
        "tabla_romberg": tabla,
        "puntos": puntos,
        "iteraciones": [
            {"t": rk4[i]["t"], "x": rk4[i]["x"], "v": rk4[i]["v"],
             "fuerza": _fuerza(rk4[i]["t"], p)}
            for i in sorted(set(
                round(j * p.N / (min(100, p.N + 1) - 1))
                for j in range(min(100, p.N + 1))
            ))
        ],
        "sensibilidad": {
            "perturbacion": "+1% simultáneo en masa, amortiguamiento y rigidez",
            "diferencia_maxima_trayectorias_m": delta,
            "indicador_relativo": amplification,
        },
        "conclusiones": {
            "numerica": (
                f"Con N={p.N} y paso h={h:.6g} s, la diferencia máxima entre RK4 "
                f"y la referencia refinada fue {error_ref:.4e} m. La diferencia máxima "
                f"entre RK2 y RK4 fue {error_24:.4e} m. La validación analítica de vibración "
                f"libre presentó un error máximo de {error_analitico:.4e} m."
            ),
            "fisica": (
                "La masa determina la inercia, el amortiguamiento disipa energía y la rigidez "
                "ejerce una fuerza restauradora. Una excitación cercana a la frecuencia natural "
                "y un amortiguamiento bajo pueden aumentar la amplitud."
            ),
        },
    }
