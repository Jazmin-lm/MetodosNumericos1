"""
Módulo 1: Detención de Emergencia de Cabinas (SIMTELE-RISK).
Modelado dinámico por EDO de primer orden resuelto con RK2 (Heun) y RK4.
"""

import math
from typing import Dict, Any, List


def simular_detencion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta la simulación numérica comparando RK2 y RK4.
    Retorna resumen de métricas, historial de iteraciones y conclusiones.
    """
    try:
        m_base = float(parametros.get("masa_kg", 1100.0))
        v0 = float(parametros.get("velocidad_inicial_ms", 5.0))
        angulo_deg = float(parametros.get("angulo_deg", 5.0))
        f_freno = float(parametros.get("fuerza_freno_n", 2500.0))
        dt = float(parametros.get("dt", 0.05))
        pert_pct = float(parametros.get("perturbacion_pct", 0.0))
        escenario = str(parametros.get("escenario", "NORMAL"))

        if m_base <= 0 or dt <= 0 or v0 <= 0:
            raise ValueError("La masa, el paso dt y la velocidad inicial deben ser mayores que cero.")

        # Aplicar perturbación porcentual sobre la masa
        m = m_base * (1.0 + pert_pct / 100.0)
        g = 9.81
        c = 15.0  # Coeficiente de amortiguamiento / fricción viscosa (kg/s)
        theta_rad = math.radians(angulo_deg)

        def aceleracion(v: float) -> float:
            # m * dv/dt = -F_freno - c*v - m*g*sin(theta)
            return (-f_freno - c * v - m * g * math.sin(theta_rad)) / m

        t = 0.0
        v_rk2 = v0
        v_rk4 = v0
        x_rk4 = 0.0
        iteracion = 0
        max_iter = 2000
        max_error_abs = 0.0

        iteraciones: List[Dict[str, Any]] = []

        while v_rk4 > 0.0 and iteracion < max_iter:
            v2_vis = max(0.0, v_rk2)
            v4_vis = max(0.0, v_rk4)
            err_abs = abs(v4_vis - v2_vis)
            if err_abs > max_error_abs:
                max_error_abs = err_abs

            iteraciones.append({
                "iteracion": iteracion,
                "tiempo_s": round(t, 4),
                "vel_rk2_ms": round(v2_vis, 5),
                "vel_rk4_ms": round(v4_vis, 5),
                "pos_rk4_m": round(x_rk4, 4),
                "error_abs": round(err_abs, 6),
            })

            # Paso RK2 (Heun)
            k1_2 = aceleracion(v_rk2)
            k2_2 = aceleracion(v_rk2 + dt * k1_2)
            v_rk2 = v_rk2 + 0.5 * dt * (k1_2 + k2_2)

            # Paso RK4 clásico
            k1 = aceleracion(v_rk4)
            k2 = aceleracion(v_rk4 + 0.5 * dt * k1)
            k3 = aceleracion(v_rk4 + 0.5 * dt * k2)
            k4 = aceleracion(v_rk4 + dt * k3)
            v_next = v_rk4 + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

            if v_next >= 0.0:
                x_rk4 += 0.5 * (v_rk4 + v_next) * dt
                t += dt
                v_rk4 = v_next
            else:
                # Interpolación lineal en el subpaso final cuando v cruza por cero
                denominador = (v_rk4 - v_next)
                fraccion = (v_rk4 / denominador) if denominador != 0 else 0.0
                dt_final = dt * max(0.0, min(1.0, fraccion))
                x_rk4 += 0.5 * v_rk4 * dt_final
                t += dt_final
                v_rk4 = 0.0

            iteracion += 1

        # Registrar estado final en reposo
        err_final = abs(0.0 - max(0.0, v_rk2))
        max_error_abs = max(max_error_abs, err_final)
        iteraciones.append({
            "iteracion": iteracion,
            "tiempo_s": round(t, 4),
            "vel_rk2_ms": round(max(0.0, v_rk2), 5),
            "vel_rk4_ms": 0.0,
            "pos_rk4_m": round(x_rk4, 4),
            "error_abs": round(err_final, 6),
        })

        tiempo_det = t if t > 0 else 1e-6
        desacel_media = v0 / tiempo_det
        error_rel_pct = (max_error_abs / v0) * 100.0 if v0 > 0 else 0.0
        limite_anden_m = 6.5
        seguro = x_rk4 <= limite_anden_m

        conclusion_numerica = (
            f"En el escenario {escenario} con Δt = {dt} s, RK4 completó {iteracion} pasos con una "
            f"discrepancia máxima frente a RK2 de {error_rel_pct:.4f}%. "
            + (
                "Al emplear un paso de integración amplio o perturbaciones, el error de truncamiento local es mayor."
                if dt >= 0.2 or abs(pert_pct) > 0
                else "El paso temporal mantiene estabilidad numérica y bajo error relativo."
            )
        )

        conclusion_problema = (
            f"La cabina se detiene en {tiempo_det:.2f} s recorriendo {x_rk4:.2f} m "
            f"(desaceleración media de {desacel_media:.2f} m/s²). "
            + (
                f"ALERTA: La distancia supera el margen de seguridad en andén ({limite_anden_m:.1f} m)."
                if not seguro
                else f"OPERACIÓN SEGURA: La distancia se mantiene dentro del margen de {limite_anden_m:.1f} m."
            )
        )

        return {
            "ok": True,
            "escenario": escenario,
            "resumen": {
                "tiempo_detencion_s": round(tiempo_det, 3),
                "distancia_frenado_m": round(x_rk4, 3),
                "desaceleracion_media_ms2": round(desacel_media, 3),
                "error_relativo_max_pct": round(error_rel_pct, 5),
                "iteraciones_totales": iteracion,
                "seguro_en_anden": seguro,
                "limite_anden_m": limite_anden_m,
            },
            "iteraciones": iteraciones,
            "conclusion_numerica": conclusion_numerica,
            "conclusion_problema": conclusion_problema,
        }

    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }