"""Parámetros iniciales del PTFE para el modelo termoablativo.

Fuente única de verdad: cada número usado por el solver sale de este archivo.
Unidades SI; temperaturas en K. Las secciones citadas ("Sec. x.y") remiten al
marco teórico de la tesis (marco_teorico20).

Conjunto adoptado: Sec. 6.4.2 del marco teórico. Se DESCARTAN explícitamente
los valores de la Tabla 3.1 de Wu et al. (2025): lambda = 1.0/0.8 W/(m K),
rho = 1700/500 kg/m3, c = 500/800 J/(kg K), Bp = 3.7e4 K, porque implican una
difusividad ~10 veces la medida y una densidad del fundido sin sentido físico.
"""

import math
import warnings

from ..parameters import Correlacion, Param

R_GAS = 8.314462618          # J/(mol K)
M_C2F4 = 0.10002             # kg/mol, unidad repetitiva C2F4 (monómero)
KGF_CM2_A_PA = 98066.5       # 1 kgf/cm2 en Pa

# ---------------------------------------------------------------------------
# Temperaturas de referencia
# ---------------------------------------------------------------------------
T0 = Param("T0, temperatura inicial", 298.15, "K", "Escenario", "supuesto", cierre="escenario")

Tm = Param(
    "Tm, temperatura de fusión nominal", 600.0, "K",
    "Wu et al. (2025); Starkweather et al. (1982): 602 K refundido, 619 K virgen",
    "acotado", cierre="fisica", rango=(600.0, 619.0),
    nota="La fusión real se distribuye en 513-633 K (Blumm et al., 2010).",
)

# ---------------------------------------------------------------------------
# Sólido semicristalino (298-600 K)
# ---------------------------------------------------------------------------
RHO_S_PUNTOS = ((295.0, 2161.0), (423.0, 2041.0))   # Blumm et al. (2010)

rho_s_corr = Correlacion(
    "rho_s(T)", "interpolación lineal entre 2161 kg/m3 (295 K) y 2041 kg/m3 (423 K)",
    "kg/m3", 295.0, 600.0, "Blumm et al. (2010)", "acotado", cierre="fisica",
    nota="Extrapolación lineal declarada entre 423 y 600 K.",
)

cp_s_corr = Correlacion(
    "cp_s(T)", "514.97 + 1.563 T", "J/(kg K)", 298.0, 600.0,
    "Ou et al. (2022); dentro de ±4 % de Blumm et al. (2010)", "acotado", cierre="fisica",
)

a_s = Param(
    "a_s, difusividad térmica del sólido", 1.22e-7, "m2/s",
    "Blumm et al. (2010); Price & Jarratt (2002)", "acotado", cierre="fisica",
    rango=(1.07e-7, 1.35e-7),
    nota="Constante en T: las mediciones varían -2 a -7 % entre 323 y 505 K.",
)

C_L = Param(
    "C_L, velocidad longitudinal (294 K, 5 MHz)", 1312.0, "m/s",
    "Rae & Brown (2016)", "anclado", cierre="fisica", rango=(1312.0, 1410.0),
    nota="Incertidumbre experimental ±5 m/s; rango entre fuentes 1312-1410 m/s.",
)

C_T = Param(
    "C_T, velocidad transversal (294 K, 5 MHz)", 518.0, "m/s",
    "Rae & Brown (2016)", "anclado", cierre="fisica", rango=(517.0, 519.0),
)

Hm = Param(
    "Hm, entalpía de fusión", 40.6e3, "J/kg",
    "Blumm et al. (2010)", "acotado", cierre="fisica", rango=(40.6e3, 58.6e3),
    nota="Variante: 58.6 kJ/kg (Wu et al., 2025), compatible con ~60 % de cristalinidad.",
)

H_transicion_II_IV = Param(
    "Entalpía de las transiciones sólido-sólido (19-35 °C)", 7.76e3, "J/kg",
    "Blumm et al. (2010)", "anclado", cierre="fisica",
    nota="Se desprecia en el modelo (~0.3 % de Q*).",
)

# ---------------------------------------------------------------------------
# Fundido (cerca de Tm)
# ---------------------------------------------------------------------------
rho_m_corr = Correlacion(
    "rho_m(T)", "1/V0, V0 = 0.3200 + 9.586e-4 T(°C) cm3/g", "kg/m3",
    603.15, 643.15, "Zoller (1978) vía Starkweather et al. (1982)", "anclado", cierre="fisica",
    nota="Fuera de 330-370 °C es extrapolación declarada.",
)

kappa_m_corr = Correlacion(
    "kappa_T,m(T)", "2.06e-5 exp(9.38e-3 T(°C)) cm2/kgf", "1/Pa",
    603.15, 643.15, "Zoller (1978) vía Starkweather et al. (1982)", "anclado", cierre="fisica",
)

cp_m_corr = Correlacion(
    "cp_m(T)", "1065 + 0.653 T", "J/(kg K)", 600.0, 640.0,
    "Pendiente de Wu et al. (2025), anclada a ~1.47 J/(g K) en Tm (Blumm et al., 2010)",
    "acotado", cierre="fisica", nota="Por encima de ~640 K es extrapolación declarada.",
)

lambda_m = Param(
    "lambda_m, conductividad del fundido", 0.245, "W/(m K)",
    "Wu et al. (2025), función lambda_a(Tm); origen probable Arai (1979)",
    "supuesto", cierre="escenario", rango=(0.135, 0.36),
    nota="Sin medición primaria verificada: entra al análisis de sensibilidad.",
)

s_ef_m = Param(
    "s_ef,m, velocidad efectiva del fundido a frecuencia térmica", 291.0, "m/s",
    "Estimación de la tesis (Sec. 2.3)", "estimado", cierre="fisica", rango=(227.0, 510.0),
)

# ---------------------------------------------------------------------------
# Tiempos de relajación térmica (Sec. 2.3 y 6.3)
# ---------------------------------------------------------------------------
tau0_s = Param(
    "tau0,s, tiempo de relajación del sólido (~530 K)", 7.5e-13, "s",
    "Tesis: Chester (1963) generalizado, entradas de Rae & Brown (2016)",
    "estimado", cierre="fisica", rango=(2.2e-13, 4.8e-12),
)

tau0_m = Param(
    "tau0,m, tiempo de relajación del fundido", 1.8e-12, "s",
    "Tesis: modelo de dos canales (Sec. 2.3)", "estimado", cierre="fisica",
    rango=(2.5e-13, 2.3e-12),
)

# ---------------------------------------------------------------------------
# Cinética de despolimerización (Sec. 3.1-3.2)
# ---------------------------------------------------------------------------
KINETICA = {
    "madorsky": dict(
        Ap=Param("Ap (Madorsky)", 4.7e18, "1/s", "Madorsky et al. (1953)", "anclado", cierre="fisica"),
        Bp=Param("Bp (Madorsky)", 40511.0, "K",
                 "Madorsky et al. (1953): Ea = 80.5 kcal/mol", "anclado", cierre="fisica",
                 nota="Medida entre 697 y 786 K; el modelo la extrapola hasta ~2000 K."),
    ),
    "wu_tabla_5_2": dict(
        Ap=Param("Ap (Wu, Tabla 5.2)", 3.1e19, "1/s", "Wu et al. (2025), Tabla 5.2", "acotado", cierre="calibrado"),
        Bp=Param("Bp (Wu, Tabla 5.2)", 41769.0, "K", "Wu et al. (2025), Tabla 5.2", "acotado", cierre="calibrado"),
    ),
}
KINETICA_CENTRAL = "madorsky"

# Hp(T) = 1.774e6 - 279.2 T hasta 800 K (Kemp, 1968, vía Wu et al., 2025);
# por encima, forma de Hess: Hp(800) + integral(cp_gas - cp_m) dT (Sec. 3.2).
HP0 = 1.774e6
HP_PENDIENTE = 279.2
T_HP_LINEAL_MAX = 800.0

# cp del C2F4 gaseoso, J/(mol K). Solo 800 K está citado en la tesis
# (NIST-JANAF, Chase 1998). Los demás puntos son PROVISIONALES: verificar contra
# la tabla JANAF del C2F4 antes de usar resultados por encima de 800 K.
CP_GAS_C2F4 = (
    (298.15, 80.5),
    (500.0, 101.0),
    (800.0, 115.6),
    (1000.0, 121.0),
    (1500.0, 127.6),
    (2000.0, 130.5),
    (3000.0, 132.5),
)
cp_gas_estatus = Param(
    "cp del C2F4 gaseoso (tabla)", 115.6, "J/(mol K)",
    "NIST-JANAF (Chase, 1998); puntos distintos de 800 K provisionales",
    "por_verificar", cierre="fisica",
)

# ---------------------------------------------------------------------------
# Óptica y escenario láser (Sec. 3.4 y 2.4)
# ---------------------------------------------------------------------------
beta_ef = Param(
    "beta_ef, fracción absorbida efectiva", 0.8, "-",
    "Supuesto de escenario (Sec. 2.4)", "supuesto", cierre="escenario", rango=(0.7, 0.9),
)

alpha_1064_cota = Param(
    "alpha a 1064 nm, cota superior en PTFE sinterizado", 2.0e2, "1/m",
    "Estimada de Huber, Heitz & Bäuerle (2004)", "estimado", cierre="fisica", rango=(1.0e2, 3.0e2),
    nota="Equivale a 1-3 cm^-1. El 0.22 cm^-1 de Wu et al. no está medido a 1064 nm.",
)

n_refraccion = Param(
    "n, índice de refracción", 1.35, "-", "Literatura general (Sec. 3.4)",
    "acotado", cierre="fisica", rango=(1.35, 1.37),
)

F_umbral_1064 = Param(
    "Fluencia umbral de ablación a 1064 nm (PTFE sinterizado, 5 ns)", 3.0e4, "J/m2",
    "Huber, Heitz & Bäuerle (2004)", "anclado", cierre="referencia",
    nota="3 J/cm^2; régimen fuera de la ventana del modelo continuo.",
)

rho0 = Param(
    "rho0, densidad de referencia para la recesión", 2161.0, "kg/m3",
    "Sólido virgen, Blumm et al. (2010)", "acotado", cierre="fisica", rango=(1933.0, 2161.0),
    nota="Variante 1933 kg/m3 (Wu et al., 2025): ~12 % de diferencia en v.",
)

# ---------------------------------------------------------------------------
# Ventana de validez del modelo continuo (Sec. 2.4)
# ---------------------------------------------------------------------------
piel_minima = Param(
    "Espesor mínimo de la piel de reacción", 1.0e-9, "m",
    "Criterio declarado de la tesis (~8 unidades CF2)", "supuesto", cierre="escenario",
)
I0_max_ventana = Param(
    "Intensidad máxima de validez", 2.0e10, "W/m2",
    "Tesis (Sec. 2.4)", "estimado", cierre="fisica", rango=(2.0e10, 3.0e10),
)


# ===========================================================================
# Funciones de propiedades
# ===========================================================================
def _validar(T, corr):
    if not corr.T_min <= T <= corr.T_max:
        warnings.warn(
            f"{corr.nombre} evaluada en T = {T:.1f} K, fuera de su intervalo "
            f"{corr.T_min:.0f}-{corr.T_max:.0f} K (extrapolación)",
            stacklevel=3,
        )


def rho_s(T):
    _validar(T, rho_s_corr)
    (T1, r1), (T2, r2) = RHO_S_PUNTOS
    return r1 + (r2 - r1) * (T - T1) / (T2 - T1)


def cp_s(T):
    _validar(T, cp_s_corr)
    return 514.97 + 1.563 * T


def lambda_s(T):
    """Conductividad del sólido, impuesta para cumplir a = lambda/(rho cp)."""
    return a_s.valor * rho_s(T) * cp_s(T)


def rho_m(T):
    _validar(T, rho_m_corr)
    V0_cm3_g = 0.3200 + 9.586e-4 * (T - 273.15)
    return 1000.0 / V0_cm3_g


def kappa_T_m(T):
    """Compresibilidad isotérmica del fundido a presión nula, 1/Pa."""
    _validar(T, kappa_m_corr)
    return 2.06e-5 * math.exp(9.38e-3 * (T - 273.15)) / KGF_CM2_A_PA


def expansion_m(T):
    """Coeficiente de expansión volumétrica del fundido, 1/K."""
    _validar(T, rho_m_corr)
    return 9.586e-4 / (0.3200 + 9.586e-4 * (T - 273.15))


def cp_m(T):
    _validar(T, cp_m_corr)
    return 1065.0 + 0.653 * T


def a_m(T):
    return lambda_m.valor / (rho_m(T) * cp_m(T))


# ---------------------------------------------------------------------------
# Cinética y energética de la despolimerización
# ---------------------------------------------------------------------------
def tasa_despolimerizacion(T, kinetica=KINETICA_CENTRAL):
    """Constante de primer orden k = Ap exp(-Bp/T), 1/s."""
    k = KINETICA[kinetica]
    return k["Ap"].valor * math.exp(-k["Bp"].valor / T)


def _cp_gas_molar(T):
    tabla = CP_GAS_C2F4
    if T <= tabla[0][0]:
        return tabla[0][1]
    for (T1, c1), (T2, c2) in zip(tabla, tabla[1:]):
        if T <= T2:
            return c1 + (c2 - c1) * (T - T1) / (T2 - T1)
    return tabla[-1][1]


def cp_gas(T):
    """cp del C2F4 gaseoso, J/(kg K)."""
    return _cp_gas_molar(T) / M_C2F4


def _integral_cp_gas(T1, T2):
    """Integral exacta de cp_gas (lineal por tramos) entre T1 y T2, J/kg."""
    puntos = sorted({T1, T2, *(T for T, _ in CP_GAS_C2F4 if T1 < T < T2)})
    total = 0.0
    for Ta, Tb in zip(puntos, puntos[1:]):
        total += 0.5 * (cp_gas(Ta) + cp_gas(Tb)) * (Tb - Ta)
    return total


def _integral_cp_m(T1, T2):
    return 1065.0 * (T2 - T1) + 0.5 * 0.653 * (T2**2 - T1**2)


def _integral_cp_s(T1, T2):
    return 514.97 * (T2 - T1) + 0.5 * 1.563 * (T2**2 - T1**2)


def Hp(T, T_ref=T_HP_LINEAL_MAX):
    """Calor de pirólisis, J/kg.

    Lineal (Kemp, 1968) hasta T_ref; por encima, forma de Hess:
    Hp(T) = Hp(T_ref) + integral_{T_ref}^{T} (cp_gas - cp_m) dT.

    Nota de consistencia: la pendiente lineal (-279.2 J/(kg K)) cumple la ley de
    Kirchhoff con el cp_m de Wu et al. (1427 J/(kg K) a 800 K), pero NO con el
    cp_m adoptado aquí (1587 J/(kg K) a 800 K), que implicaría ~-431 J/(kg K).
    El efecto sobre Q* es < 1 % (comparar T_ref = 600 y 800 K).
    """
    if T <= T_ref:
        return HP0 - HP_PENDIENTE * T
    Hp_ref = HP0 - HP_PENDIENTE * T_ref
    return Hp_ref + _integral_cp_gas(T_ref, T) - _integral_cp_m(T_ref, T)


def Q_estrella(T_s, T_inicial=None, H_fusion=None, T_ref=T_HP_LINEAL_MAX):
    """Energía específica para llevar PTFE de T_inicial a monómero gaseoso a T_s, J/kg.

    Con T_ref = Tm el resultado no depende del cp del fundido extrapolado.
    """
    Ti = T0.valor if T_inicial is None else T_inicial
    Hf = Hm.valor if H_fusion is None else H_fusion
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # cp_m > 640 K: extrapolación declarada
        return (_integral_cp_s(Ti, Tm.valor) + Hf
                + _integral_cp_m(Tm.valor, T_s) + Hp(T_s, T_ref))


# ---------------------------------------------------------------------------
# Cantidades derivadas (Sec. 2.3)
# ---------------------------------------------------------------------------
def v2_efectiva(CL=None, CT=None):
    """Media cuadrática de velocidades ponderada por capacidad calorífica."""
    CL = C_L.valor if CL is None else CL
    CT = C_T.valor if CT is None else CT
    return (CL**2 + 2.0 * CT**2) / 3.0


def tau0_chester(a=None, CL=None, CT=None):
    """tau0 = 3 a / <v^2>_C (Chester, 1963, generalizado a tres ramas)."""
    a = a_s.valor if a is None else a
    return 3.0 * a / v2_efectiva(CL, CT)


def velocidad_onda_termica(a, tau0):
    """Ch = sqrt(a / tau0)."""
    return math.sqrt(a / tau0)


def velocidad_sonido_fundido_baja_frecuencia(T):
    """Velocidad longitudinal adiabática de baja frecuencia del fundido, m/s."""
    KT = 1.0 / kappa_T_m(T)
    rho = rho_m(T)
    alpha_v = expansion_m(T)
    gamma = 1.0 + alpha_v**2 * T * KT / (rho * cp_m(T))
    return math.sqrt(gamma * KT / rho)
