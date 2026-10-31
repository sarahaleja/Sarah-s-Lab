"""
mini_openmotor.py — Réplica didáctica del núcleo de cálculo de openMotor
========================================================================

Este módulo reproduce, de forma compacta y comentada, las ecuaciones que usa
openMotor (https://github.com/reilleya/openMotor, carpeta `motorlib/`) para
simular la balística interna de un motor cohete de propelente sólido con
granos BATES. El objetivo es que el estudiante pueda LEER el modelo completo
en un solo archivo y luego comparar sus resultados con los de la interfaz
gráfica de openMotor, abriendo el archivo .ric equivalente.

Hipótesis del modelo (las mismas que openMotor):
  1. Cámara cuasi-estacionaria (0D): en cada instante la masa generada por el
     grano es igual a la masa que sale por la garganta (no hay llenado/vaciado).
  2. Ley de quemado de Saint-Robert / Vieille por tramos:  r = a · P^n
  3. Gas ideal, flujo isentrópico, garganta estrangulada (M = 1).
  4. Regresión uniforme y normal a toda superficie expuesta.
  5. No se modela el quemado erosivo (solo se vigila el flujo másico G).

Unidades: SI en todo el módulo (m, kg, s, Pa, K). Masa molar en g/mol (=kg/kmol).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from scipy.optimize import brentq

R_UNIV = 8314.462618   # J/(kmol·K)  — misma constante que motorlib/constants.py
G0 = 9.80665           # m/s²
P_ATM = 101325.0       # Pa


# ---------------------------------------------------------------------------
# Propelente
# ---------------------------------------------------------------------------
@dataclass
class TramoPropelente:
    """Propiedades válidas en un rango de presión [p_min, p_max]."""
    p_min: float   # Pa
    p_max: float   # Pa
    a: float       # m/(s·Pa^n)
    n: float       # –
    k: float       # razón de calores específicos γ
    T: float       # K, temperatura de combustión (adiabática · eficiencia c*)
    M: float       # g/mol, masa molar de los gases de escape


@dataclass
class Propelente:
    nombre: str
    densidad: float                 # kg/m³
    tramos: list[TramoPropelente]

    @staticmethod
    def _factor_flujo(t: TramoPropelente) -> float:
        """Γ/√(R T): el gasto másico por la garganta es  ṁ = P·At·√(k/(R T))·(2/(k+1))^((k+1)/(2(k-1)))."""
        R = R_UNIV / t.M
        return math.sqrt(t.k / (R * t.T) * (2 / (t.k + 1)) ** ((t.k + 1) / (t.k - 1)))

    def tramo(self, P: float) -> TramoPropelente:
        """Tramo cuyo rango contiene P (o el más cercano, como hace openMotor)."""
        for t in self.tramos:
            if t.p_min <= P <= t.p_max:
                return t
        return min(self.tramos, key=lambda t: min(abs(P - t.p_min), abs(P - t.p_max)))

    def tasa_quemado(self, P: float) -> float:
        t = self.tramo(P)
        return t.a * P ** t.n

    def c_estrella(self, P: float) -> float:
        """Velocidad característica c* = P·At / ṁ."""
        return 1.0 / self._factor_flujo(self.tramo(P))

    def presion_desde_kn(self, kn: float) -> float:
        """
        Equilibrio de masa en la cámara:
            ρ · A_b · a · Pⁿ  =  P · A_t / c*
        Dividiendo por A_t y usando Kn = A_b / A_t:
            P = (Kn · ρ · a · c*)^(1/(1-n))
        Se prueba cada tramo y se acepta el que cae dentro de su propio rango.
        """
        candidatos = []
        for t in self.tramos:
            P = (kn * self.densidad * t.a / self._factor_flujo(t)) ** (1 / (1 - t.n))
            if t.p_min <= P <= t.p_max:
                return P
            candidatos.append((min(abs(P - t.p_min), abs(P - t.p_max)), P))
        return min(candidatos)[1]


# ---------------------------------------------------------------------------
# Grano BATES (cilindro con núcleo circular)
# ---------------------------------------------------------------------------
@dataclass
class GranoBATES:
    diametro: float           # m
    nucleo: float             # m
    longitud: float           # m
    caras_inhibidas: int = 0  # 0, 1 o 2 caras que NO queman

    @property
    def alma(self) -> float:
        """Espesor de pared (web) inicial."""
        return (self.diametro - self.nucleo) / 2

    def longitud_en(self, x: float) -> float:
        return max(self.longitud - (2 - self.caras_inhibidas) * x, 0.0)

    def area_cara(self, x: float) -> float:
        d = self.nucleo + 2 * x
        return math.pi / 4 * (self.diametro ** 2 - min(d, self.diametro) ** 2)

    def area_puerto(self, x: float) -> float:
        return math.pi / 4 * min(self.nucleo + 2 * x, self.diametro) ** 2

    def alma_restante(self, x: float) -> float:
        pared = self.alma - x
        return pared if self.caras_inhibidas == 2 else min(pared, self.longitud_en(x))

    def area_quemado(self, x: float) -> float:
        """A_b(x) = superficie del núcleo + caras expuestas."""
        if self.alma_restante(x) <= 0:
            return 0.0
        nucleo = math.pi * (self.nucleo + 2 * x) * self.longitud_en(x)
        return nucleo + (2 - self.caras_inhibidas) * self.area_cara(x)

    def volumen(self, x: float) -> float:
        if self.alma_restante(x) <= 0:
            return 0.0
        return self.area_cara(x) * self.longitud_en(x)


# ---------------------------------------------------------------------------
# Tobera
# ---------------------------------------------------------------------------
@dataclass
class Tobera:
    garganta: float               # m
    salida: float                 # m
    eficiencia: float = 0.85
    angulo_div: float = 15.0      # grados (semiángulo)
    long_garganta: float = 0.0    # m

    @property
    def At(self) -> float:
        return math.pi / 4 * self.garganta ** 2

    @property
    def Ae(self) -> float:
        return math.pi / 4 * self.salida ** 2

    @property
    def expansion(self) -> float:
        return self.Ae / self.At

    def presion_salida(self, k: float, Pc: float) -> float:
        """Resuelve la relación de áreas isentrópica  Ae/At = f(Pe/Pc)  (rama supersónica)."""
        def eps(pr):  # Ae/At en función de pr = Pe/Pc
            return 1 / (((k + 1) / 2) ** (1 / (k - 1)) * pr ** (1 / k)
                        * math.sqrt((k + 1) / (k - 1) * (1 - pr ** ((k - 1) / k))))
        pr_critica = (2 / (k + 1)) ** (k / (k - 1))
        pr = brentq(lambda pr: eps(pr) - self.expansion, 1e-9, pr_critica * (1 - 1e-9))
        return pr * Pc

    def cf(self, Pc: float, Pa: float, k: float) -> float:
        """Coeficiente de empuje ideal corregido con las mismas pérdidas que openMotor."""
        Pe = self.presion_salida(k, Pc)
        momento = math.sqrt(2 * k ** 2 / (k - 1) * (2 / (k + 1)) ** ((k + 1) / (k - 1))
                            * (1 - (Pe / Pc) ** ((k - 1) / k)))
        presion = (Pe - Pa) * self.Ae / (self.At * Pc)
        cf_ideal = momento + presion
        perd_div = (1 + math.cos(math.radians(self.angulo_div))) / 2
        aspecto = self.long_garganta / self.garganta
        perd_garg = 0.95 if aspecto > 0.45 else 0.99 - 0.0333 * aspecto
        perd_piel = 0.99
        return perd_div * perd_garg * self.eficiencia * (perd_piel * cf_ideal + (1 - perd_piel))


# ---------------------------------------------------------------------------
# Motor y simulación
# ---------------------------------------------------------------------------
@dataclass
class Resultado:
    t: list = field(default_factory=list)
    kn: list = field(default_factory=list)
    P: list = field(default_factory=list)
    F: list = field(default_factory=list)
    G: list = field(default_factory=list)       # flujo másico máximo (kg/m²/s)
    masa: list = field(default_factory=list)
    masa_inicial: float = 0.0
    alertas: list = field(default_factory=list)

    # --- métricas resumen (mismas definiciones que motorlib/simResult.py) ---
    @property
    def impulso(self) -> float:
        return sum(F * (t1 - t0) for F, t0, t1 in zip(self.F[1:], self.t[:-1], self.t[1:]))

    @property
    def tiempo_quemado(self) -> float:
        return self.t[-1]

    @property
    def empuje_medio(self) -> float:
        return sum(self.F) / len(self.F)

    @property
    def isp(self) -> float:
        return self.impulso / (self.masa_inicial * G0)

    @property
    def designacion(self) -> str:
        """Clase NAR/TRA: cada letra duplica el impulso (A = 1.26–2.5 N·s)."""
        orden = int(math.log(self.impulso / 1.25, 2)) + 1
        return f"{chr(64 + orden)}{self.empuje_medio:.0f}"


@dataclass
class Motor:
    granos: list[GranoBATES]
    tobera: Tobera
    propelente: Propelente
    dt: float = 0.01
    P_amb: float = P_ATM
    P_max_permitida: float = 1500 * 6895     # Pa (≈10.3 MPa, valor por defecto de openMotor)
    G_max_permitido: float = 2 / 0.001422    # kg/(m²·s) (≈1406, 2 lb/in²/s)
    puerto_garganta_min: float = 2.0
    umbral_alma: float = 0.001 / 39.37       # m
    umbral_empuje: float = 0.1               # % del empuje máximo

    def kn(self, x: float) -> float:
        return sum(g.area_quemado(x) for g in self.granos) / self.tobera.At

    def simular(self) -> Resultado:
        res = Resultado()
        prop, rho = self.propelente, self.propelente.densidad
        x = 0.0  # todos los granos BATES regresan igual (misma presión)

        ratio = self.granos[-1].area_puerto(0) / self.tobera.At
        if ratio < self.puerto_garganta_min:
            res.alertas.append(f"Relación puerto/garganta inicial {ratio:.2f} < {self.puerto_garganta_min}")

        res.masa_inicial = rho * sum(g.volumen(0) for g in self.granos)
        P = prop.presion_desde_kn(self.kn(0))
        res.t.append(0.0); res.kn.append(self.kn(0)); res.P.append(P)
        res.F.append(0.0); res.G.append(0.0); res.masa.append(res.masa_inicial)

        while len(res.t) == 1 or res.F[-1] > self.umbral_empuje / 100 * max(res.F):
            dx = prop.tasa_quemado(res.P[-1]) * self.dt   # 1) regresión con la presión anterior
            # 2) flujo másico acumulado a lo largo de los granos → G en la salida de cada uno
            mdot, G = 0.0, 0.0
            for g in self.granos:
                if g.alma_restante(x) > self.umbral_alma:
                    mdot += rho * (g.volumen(x) - g.volumen(x + dx)) / self.dt
                    G = max(G, mdot / g.area_puerto(x + dx))
            x += dx
            # 3) nuevo Kn → presión de equilibrio → empuje
            kn = self.kn(x)
            P = prop.presion_desde_kn(kn) if kn > 0 else 0.0
            k = prop.tramo(P).k
            F = max(self.tobera.cf(P, self.P_amb, k) * self.tobera.At * P, 0.0) if P > self.P_amb else 0.0

            res.t.append(res.t[-1] + self.dt); res.kn.append(kn); res.P.append(P)
            res.F.append(F); res.G.append(G)
            res.masa.append(rho * sum(g.volumen(x) for g in self.granos))

        if max(res.P) > self.P_max_permitida:
            res.alertas.append(f"Presión máxima {max(res.P)/1e6:.2f} MPa supera el límite "
                               f"{self.P_max_permitida/1e6:.2f} MPa")
        if max(res.G) > self.G_max_permitido:
            res.alertas.append(f"Flujo másico máximo {max(res.G):.0f} kg/m²s supera "
                               f"{self.G_max_permitido:.0f} kg/m²s (riesgo de quemado erosivo)")
        return res


# ---------------------------------------------------------------------------
# Propelente de referencia: KNSB (nitrato de potasio / sorbitol 65/35),
# datos de Richard Nakka — idénticos al preset "Nakka - KNSB" de openMotor.
# ---------------------------------------------------------------------------
def _knsb_tramo(p_min, p_max, a, n):
    return TramoPropelente(p_min, p_max, a, n, k=1.1361, T=1520.0, M=39.9)


KNSB = Propelente(
    nombre="Nakka - KNSB",
    densidad=1750.0,
    tramos=[
        _knsb_tramo(103425, 806715, 1.9253259619746373e-06, 0.625),
        _knsb_tramo(806715, 1503110, 0.6656608561590813, -0.313),
        _knsb_tramo(1503110, 3792250, 0.009528121181782798, -0.0145),
        _knsb_tramo(3792250, 7032900, 2.709667768835332e-06, 0.5245),
        _knsb_tramo(7032900, 10673460, 0.00417677261069904, 0.059),
    ],
)
