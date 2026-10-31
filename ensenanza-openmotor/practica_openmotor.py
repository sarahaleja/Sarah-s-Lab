"""
Práctica: balística interna de un motor cohete sólido con openMotor
===================================================================

Ejecuta:  python3 practica_openmotor.py

Genera en ./resultados/:
  - motor_base.ric          → ábrelo en openMotor (File ▸ Open) y compara.
  - motor_base.eng          → curva de empuje para OpenRocket / RockSim.
  - motor_base.csv          → datos tiempo a tiempo.
  - 01_caso_base.png        → empuje, presión, Kn y flujo másico.
  - 02_barrido_garganta.png → Experimento A: efecto del diámetro de garganta.
  - 03_geometria_bates.png  → Experimento B: progresivo, neutro, regresivo.
  - 04_densidad_carga.png   → Experimento C: núcleo vs. flujo másico (erosivo).
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mini_openmotor import KNSB, GranoBATES, Motor, Tobera

SALIDA = Path(__file__).parent / "resultados"
SALIDA.mkdir(exist_ok=True)

plt.rcParams.update({"figure.dpi": 120, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


# ---------------------------------------------------------------------------
# 1. Definición del motor base (motor de 38 mm, clase H, propelente KNSB)
# ---------------------------------------------------------------------------
def motor_base(garganta=7.0e-3, nucleo=12.7e-3, longitud=56e-3, n_granos=3,
               caras_inhibidas=0) -> Motor:
    granos = [GranoBATES(diametro=33e-3, nucleo=nucleo, longitud=longitud,
                         caras_inhibidas=caras_inhibidas) for _ in range(n_granos)]
    tobera = Tobera(garganta=garganta, salida=19e-3, eficiencia=0.85,
                    angulo_div=12.0, long_garganta=3e-3)
    return Motor(granos=granos, tobera=tobera, propelente=KNSB, dt=0.01)


def resumen(nombre: str, motor: Motor, r) -> None:
    print(f"\n=== {nombre} ===")
    print(f"  Designación ............ {r.designacion}")
    print(f"  Impulso total .......... {r.impulso:7.1f} N·s")
    print(f"  Empuje medio / máximo .. {r.empuje_medio:7.1f} / {max(r.F):.1f} N")
    print(f"  Tiempo de quemado ...... {r.tiempo_quemado:7.2f} s")
    print(f"  Presión máx. / media ... {max(r.P)/1e6:7.2f} / {sum(r.P)/len(r.P)/1e6:.2f} MPa")
    print(f"  Kn inicial / máximo .... {r.kn[0]:7.0f} / {max(r.kn):.0f}")
    print(f"  Isp entregado .......... {r.isp:7.1f} s")
    print(f"  Masa de propelente ..... {r.masa_inicial*1e3:7.0f} g")
    print(f"  Flujo másico máx. ...... {max(r.G):7.0f} kg/(m²·s)")
    print(f"  Relación de expansión .. {motor.tobera.expansion:7.2f}")
    print(f"  Alertas ................ {r.alertas or 'ninguna'}")


# ---------------------------------------------------------------------------
# 2. Exportadores
# ---------------------------------------------------------------------------
def exportar_ric(motor: Motor, ruta: Path) -> None:
    """Archivo de motor de openMotor (YAML, formato de la versión 0.6.2)."""
    g = motor.granos[0]
    inh = {0: "Neither", 1: "Top", 2: "Both"}[g.caras_inhibidas]
    granos = "".join(
        f"  - properties: {{coreDiameter: {gr.nucleo}, diameter: {gr.diametro}, "
        f"inhibitedEnds: {inh}, length: {gr.longitud}}}\n    type: BATES\n"
        for gr in motor.granos)
    tramos = "".join(
        f"    - {{a: {t.a}, k: {t.k}, m: {t.M}, maxPressure: {t.p_max}, "
        f"minPressure: {t.p_min}, n: {t.n}, t: {t.T}}}\n"
        for t in motor.propelente.tramos)
    tb = motor.tobera
    ruta.write_text(
        "data:\n"
        f"  config: {{ambPressure: {motor.P_amb}, burnoutThrustThres: {motor.umbral_empuje}, "
        f"burnoutWebThres: {motor.umbral_alma}, flowSeparationWarnPercent: 0.05, mapDim: 750, "
        f"maxMachNumber: 0.7, maxMassFlux: {motor.G_max_permitido}, maxPressure: {motor.P_max_permitida}, "
        f"minPortThroat: {motor.puerto_garganta_min}, sepPressureRatio: 0.4, timestep: {motor.dt}}}\n"
        "  grains:\n" + granos +
        f"  nozzle: {{convAngle: 35.0, divAngle: {tb.angulo_div}, efficiency: {tb.eficiencia}, "
        f"erosionCoeff: 0.0, exit: {tb.salida}, slagCoeff: 0.0, throat: {tb.garganta}, "
        f"throatLength: {tb.long_garganta}}}\n"
        "  propellant:\n"
        f"    density: {motor.propelente.densidad}\n"
        f"    name: {motor.propelente.nombre}\n"
        "    tabs:\n" + tramos +
        "type: !!python/object/apply:uilib.fileIO.fileTypes [3]\n"
        "version: !!python/tuple [0, 6, 2]\n",
        encoding="utf-8")


def exportar_eng(motor: Motor, r, ruta: Path, nombre="SL38-KNSB") -> None:
    """Formato RASP (.eng) que leen OpenRocket y RockSim."""
    D = motor.granos[0].diametro + 5e-3              # diámetro de la carcasa (aprox.)
    L = sum(g.longitud for g in motor.granos) + 40e-3  # + tobera y cierre
    m_prop = r.masa_inicial
    m_total = m_prop + 0.25                           # masa de hardware supuesta
    lineas = [f"; {nombre} — generado por practica_openmotor.py (Sarah's Lab)",
              f"{nombre}-{r.designacion} {D*1e3:.0f} {L*1e3:.0f} P {m_prop:.4f} {m_total:.4f} SarahsLab"]
    paso = max(1, len(r.t) // 30)                     # ~30 puntos, suficiente para la curva
    for t, F in list(zip(r.t, r.F))[1::paso]:
        lineas.append(f"   {t:.3f} {F:.2f}")
    lineas.append(f"   {r.t[-1]:.3f} 0.00")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def exportar_csv(r, ruta: Path) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tiempo_s", "kn", "presion_Pa", "empuje_N", "flujo_masico_kg_m2s", "masa_kg"])
        w.writerows(zip(r.t, r.kn, r.P, r.F, r.G, r.masa))


# ---------------------------------------------------------------------------
# 3. Caso base
# ---------------------------------------------------------------------------
def caso_base():
    m = motor_base()
    r = m.simular()
    resumen("CASO BASE — 3 × BATES KNSB, garganta 7 mm", m, r)
    exportar_ric(m, SALIDA / "motor_base.ric")
    exportar_eng(m, r, SALIDA / "motor_base.eng")
    exportar_csv(r, SALIDA / "motor_base.csv")

    fig, ax = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    ax[0, 0].plot(r.t, r.F, color="#c0392b"); ax[0, 0].set_ylabel("Empuje [N]")
    ax[0, 1].plot(r.t, [p / 1e6 for p in r.P], color="#2c3e50"); ax[0, 1].set_ylabel("Presión de cámara [MPa]")
    for t in KNSB.tramos:  # tramos de la ley de quemado
        ax[0, 1].axhline(t.p_max / 1e6, color="gray", ls=":", lw=0.8)
    ax[1, 0].plot(r.t, r.kn, color="#8e44ad"); ax[1, 0].set_ylabel("Kn = A_b / A_t")
    ax[1, 1].plot(r.t, r.G, color="#d35400"); ax[1, 1].set_ylabel("Flujo másico G [kg/(m²·s)]")
    ax[1, 1].axhline(m.G_max_permitido, color="red", ls="--", lw=1, label="Límite openMotor")
    ax[1, 1].legend()
    for a in ax[1]:
        a.set_xlabel("Tiempo [s]")
    fig.suptitle(f"Caso base: {r.designacion} — I = {r.impulso:.0f} N·s, Isp = {r.isp:.0f} s, "
                 f"P_max = {max(r.P)/1e6:.2f} MPa", fontweight="bold")
    fig.tight_layout(); fig.savefig(SALIDA / "01_caso_base.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Experimento A — Diámetro de garganta: Kn controla la presión
# ---------------------------------------------------------------------------
def experimento_garganta():
    gargantas = [6.0, 6.5, 7.0, 8.0, 9.0]  # mm
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
    print("\n=== EXPERIMENTO A — Barrido del diámetro de garganta ===")
    print("  d_t[mm]   Kn0   P_max[MPa]   Isp[s]   I[N·s]   t_b[s]   Clase")
    filas = []
    for dt_mm in gargantas:
        m = motor_base(garganta=dt_mm * 1e-3)
        r = m.simular()
        ax[0].plot(r.t, r.F, label=f"{dt_mm} mm")
        ax[1].plot(r.t, [p / 1e6 for p in r.P], label=f"{dt_mm} mm")
        filas.append((dt_mm, r.kn[0], max(r.P) / 1e6, r.isp))
        print(f"  {dt_mm:5.1f}  {r.kn[0]:5.0f}   {max(r.P)/1e6:8.2f}   {r.isp:7.1f}  "
              f"{r.impulso:7.1f}  {r.tiempo_quemado:6.2f}   {r.designacion}"
              + ("   ⚠ " + "; ".join(r.alertas) if r.alertas else ""))
    ax[0].set(title="Empuje", xlabel="Tiempo [s]", ylabel="F [N]")
    ax[1].set(title="Presión de cámara", xlabel="Tiempo [s]", ylabel="P [MPa]")
    ax[0].legend(title="Garganta"); ax[1].legend(title="Garganta")
    d, kn0, pmax, isp = zip(*filas)
    ax[2].plot(kn0, isp, "o-", color="#16a085")
    for x, y, p in zip(kn0, isp, pmax):
        ax[2].annotate(f"{p:.1f} MPa", (x, y), textcoords="offset points", xytext=(5, -12), fontsize=8)
    ax[2].set(title="Isp vs. Kn inicial (etiqueta: P_max)", xlabel="Kn inicial", ylabel="Isp [s]")
    fig.suptitle("Experimento A — Garganta más pequeña ⇒ Kn mayor ⇒ más presión ⇒ más Isp (y más riesgo)",
                 fontweight="bold")
    fig.tight_layout(); fig.savefig(SALIDA / "02_barrido_garganta.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Experimento B — Geometría del grano: perfil progresivo / neutro / regresivo
# ---------------------------------------------------------------------------
def experimento_geometria():
    D, d = 33e-3, 12.7e-3
    # Longitud BATES "óptima": A_b es igual al inicio y al final del quemado,
    # así la curva oscila lo menos posible alrededor de un valor medio.
    L_opt = (3 * D + d) / 2
    # Todos los casos tienen la MISMA longitud total de propelente (168 mm)
    casos = [
        ("6 × 28 mm (granos cortos)", dict(longitud=28e-3, n_granos=6)),
        (f"3 × {L_opt*1e3:.0f} mm (óptimo BATES)", dict(longitud=L_opt, n_granos=3)),
        ("2 × 84 mm (granos largos)", dict(longitud=84e-3, n_granos=2)),
        ("3 × 56 mm, caras inhibidas", dict(longitud=56e-3, n_granos=3, caras_inhibidas=2)),
    ]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    print(f"\n=== EXPERIMENTO B — Geometría (L_opt = (3D + d)/2 = {L_opt*1e3:.1f} mm) ===")
    for etiqueta, kw in casos:
        m = motor_base(**kw)
        r = m.simular()
        prog = (max(r.kn) - min(r.kn[:-5])) / r.kn[0] * 100  # variación de Kn durante el quemado
        ax[0].plot(r.t, r.kn, label=etiqueta)
        ax[1].plot(r.t, r.F, label=etiqueta)
        print(f"  {etiqueta:30s} Kn0={r.kn[0]:4.0f}  Kn_max={max(r.kn):4.0f}  Kn_final={r.kn[-3]:4.0f}  ΔKn/Kn0={prog:5.1f} %  "
              f"{r.designacion:6s} P_max={max(r.P)/1e6:.2f} MPa")
    ax[0].set(title="Kn(t): forma de la curva", xlabel="Tiempo [s]", ylabel="Kn")
    ax[1].set(title="Empuje", xlabel="Tiempo [s]", ylabel="F [N]")
    ax[0].legend(fontsize=8); ax[1].legend(fontsize=8)
    fig.suptitle("Experimento B — La geometría del grano define la forma de la curva de empuje",
                 fontweight="bold")
    fig.tight_layout(); fig.savefig(SALIDA / "03_geometria_bates.png"); plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Experimento C — Diámetro del núcleo: carga volumétrica vs. flujo másico
# ---------------------------------------------------------------------------
def experimento_nucleo():
    nucleos = [8.0, 10.0, 12.7, 15.0, 18.0]  # mm
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    print("\n=== EXPERIMENTO C — Diámetro del núcleo (carga vs. flujo másico) ===")
    for dn in nucleos:
        m = motor_base(nucleo=dn * 1e-3)
        r = m.simular()
        carga = 1 - (dn / 33) ** 2
        ax[0].plot(r.t, r.G, label=f"núcleo {dn} mm")
        ax[1].scatter(carga * 100, r.impulso, s=40)
        ax[1].annotate(f"{dn} mm", (carga * 100, r.impulso), textcoords="offset points", xytext=(5, 3), fontsize=8)
        print(f"  núcleo {dn:5.1f} mm  carga={carga*100:4.1f} %  G_max={max(r.G):5.0f} kg/m²s  "
              f"I={r.impulso:6.1f} N·s  {r.designacion}" + ("   ⚠ " + "; ".join(r.alertas) if r.alertas else ""))
    ax[0].axhline(motor_base().G_max_permitido, color="red", ls="--", lw=1, label="Límite G")
    ax[0].set(title="Flujo másico en la salida del último grano", xlabel="Tiempo [s]", ylabel="G [kg/(m²·s)]")
    ax[0].legend(fontsize=8)
    ax[1].set(title="Más carga ⇒ más impulso…", xlabel="Carga volumétrica de la sección [%]", ylabel="Impulso [N·s]")
    fig.suptitle("Experimento C — …pero un núcleo estrecho dispara el flujo másico (riesgo de quemado erosivo)",
                 fontweight="bold")
    fig.tight_layout(); fig.savefig(SALIDA / "04_densidad_carga.png"); plt.close(fig)


if __name__ == "__main__":
    caso_base()
    experimento_garganta()
    experimento_geometria()
    experimento_nucleo()
    print(f"\nResultados guardados en: {SALIDA.resolve()}")
