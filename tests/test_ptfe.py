"""Comprueba que los parámetros reproducen los valores del marco teórico.

Ejecutar desde la raíz del repositorio:  python3 -m tests.test_ptfe
"""
import math
import warnings

from ablation.materials import ptfe as P


def cerca(valor, esperado, tol_rel, etiqueta):
    err = abs(valor - esperado) / abs(esperado)
    estado = "OK " if err <= tol_rel else "FALLA"
    print(f"[{estado}] {etiqueta}: {valor:.4g} (esperado {esperado:.4g}, error {100*err:.1f} %)")
    return err <= tol_rel


def main():
    ok = []
    # Sólido (Sec. 6.4.2 y 2.3)
    ok.append(cerca(P.lambda_s(300.0), 0.259, 0.01, "lambda_s(300 K) [W/(m K)]"))
    ok.append(cerca(P.lambda_s(323.0), 0.266, 0.01, "lambda_s(323 K) [W/(m K)]"))
    ok.append(cerca(math.sqrt(P.v2_efectiva()), 868.0, 0.005, "s_ef del sólido [m/s]"))
    ok.append(cerca(P.tau0_chester(), 4.9e-13, 0.02, "tau0,s a 294 K [s]"))
    ok.append(cerca(3 * P.a_s.valor / math.sqrt(P.v2_efectiva()), 4.2e-10, 0.02,
                    "camino libre medio del sólido [m]"))
    ok.append(cerca(P.velocidad_onda_termica(P.a_s.valor, P.tau0_s.valor), 403.0, 0.01,
                    "Ch,sólido con tau0 adoptado [m/s]"))
    # Fundido (Sec. 2.3)
    T330 = 330.0 + 273.15
    ok.append(cerca(P.rho_m(T330), 1572.0, 0.002, "rho_m(330 °C) [kg/m3]"))
    ok.append(cerca(1.0 / P.kappa_T_m(T330), 0.215e9, 0.01, "K_T,m(330 °C) [Pa]"))
    ok.append(cerca(P.expansion_m(T330), 1.51e-3, 0.01, "alpha_v,m(330 °C) [1/K]"))
    ok.append(cerca(P.velocidad_sonido_fundido_baja_frecuencia(T330), 393.0, 0.01,
                    "velocidad longitudinal del fundido, baja frecuencia [m/s]"))
    # Cinética (Sec. 3.2)
    ok.append(cerca(P.tasa_despolimerizacion(696.65), 2.53e-7, 0.05,
                    "k Madorsky a 696.65 K [1/s] (medido 2.53e-7)"))
    ok.append(cerca(P.tasa_despolimerizacion(786.15), 2.09e-4, 0.07,
                    "k Madorsky a 786.15 K [1/s] (medido 2.09e-4)"))
    ratio = P.tasa_despolimerizacion(1760, "wu_tabla_5_2") / P.tasa_despolimerizacion(1760)
    ok.append(cerca(ratio, 3.2, 0.03, "cociente Wu/Madorsky a 1760 K"))
    # Kissinger con el pico TGA de Henri et al. (2020): 574.2 °C a 15 °C/min
    Tp = 574.2 + 273.15
    k_req = (15.0 / 60.0) * P.KINETICA["madorsky"]["Bp"].valor / Tp**2
    ok.append(cerca(k_req, 0.014, 0.03, "k exigido por Kissinger [1/s]"))
    # Energética (Sec. 3.2 y 3.4)
    cp_wu_800 = 904.2 + 0.653 * 800.0          # cp_m de Wu et al. (Tabla 2.1)
    ok.append(cerca(cp_wu_800 - P.HP_PENDIENTE, P.cp_gas(800.0), 0.01,
                    "Kirchhoff con cp_m de Wu: cp_gas implícito vs JANAF [J/(kg K)]"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # cp_m por encima de 640 K: extrapolación declarada
        implicito = P.cp_m(800.0) - P.HP_PENDIENTE
    print(f"[INFO] Kirchhoff con cp_m adoptado: cp_gas implícito {implicito:.0f} J/(kg K) "
          f"vs JANAF {P.cp_gas(800.0):.0f}: la pendiente lineal de Hp no es consistente "
          f"con el cp_m adoptado (ver docstring de Hp)")
    q800 = P.Q_estrella(1760.0)
    q600 = P.Q_estrella(1760.0, T_ref=P.Tm.valor)
    ok.append(cerca(q800, 3.45e6, 0.02,
                    "Q*(1760 K), conjunto Sec. 6.4.2 [J/kg] (depende de cp_gas por verificar)"))
    ok.append(cerca(q600, q800, 0.01, "Q*(1760 K) con T_ref = Tm vs T_ref = 800 K"))
    # Q* hasta 800-1000 K usado en la Sec. 3.4 (con Hm y cp_m de Wu daba 2.2-2.5 MJ/kg)
    print(f"[INFO] Q*(800 K) = {P.Q_estrella(800.0)/1e6:.2f} MJ/kg, "
          f"Q*(1000 K) = {P.Q_estrella(1000.0)/1e6:.2f} MJ/kg con el conjunto adoptado")
    print(f"\n{sum(ok)}/{len(ok)} comprobaciones dentro de tolerancia")
    return all(ok)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
