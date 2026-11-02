"""
Llaveros 3D de motores de cohete experimentales — generador paramétrico.

Impresora: Creality (FDM, boquilla 0.4 mm) · Material: PLA.

Modelos (sólidos de revolución completos, con detalles):
  1. Motor cohete de propelente sólido experimental (tipo prueba estática):
     tobera convergente-divergente, retenedor, roscas, cámara, tapón e ignitor.
  2. Motor de ciclo de combustión por etapas inspirado en el Raptor 1:
     campana, anillo colector, cámara con anillos, brida, cabezal con
     turbobombas, inyectores y tuberías.

Estrategia de impresión (sin soportes):
  * Se imprimen DE PIE: salida de la tobera sobre la cama, anilla arriba.
  * Toda superficie que mira hacia abajo tiene ≤ 45° respecto a la vertical
    (chaflanes a 45°, anillos con perfil de "gota", conos, tuberías casi verticales).
  * La tobera es HUECA por dentro (como la real) hasta la garganta: la cavidad
    se estrecha al subir, así que se autosoporta.
  * El agujero de la anilla tiene forma de gota (punta arriba) para imprimirse
    horizontal sin soporte.

Unidades: mm. Ejecutar:  python3 generar_llaveros.py
Requiere: pip install manifold3d trimesh numpy
"""
from pathlib import Path
import numpy as np
import manifold3d as m3d
import trimesh

OUT = Path(__file__).parent / "stl"
SEG = 128                      # segmentos de revolución
DENSIDAD_PLA = 1.24            # g/cm³
M = m3d.Manifold
CS = m3d.CrossSection


# ------------------------------------------------------------- utilidades 2D
def bezier(p0, p1, p2, n=40):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(np.asarray, (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def revolve(*tramos):
    """Revoluciona 360° un perfil (r, z) dado por tramos; se cierra por el eje."""
    pts = np.vstack([np.atleast_2d(np.asarray(t, float)) for t in tramos])
    keep = np.r_[True, np.linalg.norm(np.diff(pts, axis=0), axis=1) > 1e-6]
    pts = pts[keep]
    pts = np.vstack([[0.0, pts[0, 1]], pts, [0.0, pts[-1, 1]]])
    area = 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
    if area < 0:
        pts = pts[::-1]
    return M.revolve(CS([pts.tolist()]), SEG)


def anillo_gota(z, r_in, r_out, alto):
    """Anillo con perfil de gota: chaflán inferior a 45° (imprimible) y
    cara superior redondeada. Simula colectores y aros de refuerzo."""
    d = r_out - r_in
    zc = z + d                                   # el chaflán de 45° sube d
    a = np.radians(np.linspace(-90, 90, 24))
    rr = min(alto - d, d) if alto > d else d * 0.5
    top = np.c_[r_out - rr + rr * np.cos(a), zc + (alto - d) - rr + rr * np.sin(a)]
    top = top[top[:, 1] >= zc - 1e-9] if alto > d else np.array([[r_out, zc]])
    pts = np.vstack([[r_in, z], [r_out, zc], top, [r_in, z + alto + 0.01]])
    pts = np.vstack([[0, z], pts, [0, z + alto + 0.01]])
    return M.revolve(CS([pts.tolist()]), SEG)


def rosca(z, alto, r_raiz, r_cresta, paso=1.5):
    """Rosca helicoidal de perfil senoidal: r(θ, z) = R0 + e·cos(θ − 2πz/P).
    Pendiente máx. del flanco: |∂r/∂z| = 2πe/P  (≤ 1 → ≤ 45°, imprimible)."""
    e = (r_cresta - r_raiz) / 2
    R0 = r_raiz + e
    cil = M.cylinder(alto, R0, R0, SEG).refine_to_length(0.12)

    def deformar(v):
        v = np.array(v, dtype=float, copy=True)
        th = np.arctan2(v[:, 1], v[:, 0])
        rr = np.hypot(v[:, 0], v[:, 1])
        borde = rr > 1e-6
        nuevo = R0 + e * np.cos(th - 2 * np.pi * v[:, 2] / paso)
        f = np.where(borde, nuevo / np.where(borde, R0, 1), 1.0)
        f = np.where(rr > R0 - 1e-3, f, 1 + (f - 1) * rr / R0)   # tapas: escala suave
        v[:, 0] *= f
        v[:, 1] *= f
        return v

    return cil.warp_batch(deformar).translate([0, 0, z])


def cilindro(z, alto, r, x=0.0, y=0.0, base_conica=True):
    """Cilindro vertical; si base_conica, su fondo es un cono a 45° (sin voladizo)."""
    c = M.cylinder(alto, r, r, SEG // 2).translate([x, y, z])
    if base_conica:
        c = c + M.cylinder(r, 0.01, r, SEG // 2).translate([x, y, z - r])
    return c


def tuberia(puntos, r):
    """Tubería suave = unión de cápsulas (envolventes de esferas consecutivas)."""
    esf = [M.sphere(r, 32).translate(list(p)) for p in puntos]
    return M.batch_boolean([M.batch_hull([a, b]) for a, b in zip(esf, esf[1:])], m3d.OpType.Add)


def anilla(z_base, r_ext=4.0, r_int=2.0, espesor=3.4, cuello=2.0, base=6.0):
    """Anilla vertical para el aro del llavero. Agujero en gota (punta arriba)
    y exterior unido a la base por tangentes (sin voladizos > 45°)."""
    h = cuello + r_ext                                   # centro del agujero
    ext = CS.batch_hull([CS.circle(r_ext, 96).translate([0, h]),
                         CS.square([base, 0.5]).translate([-base / 2, 0])])   # base ⊂ soporte
    a = r_int / np.sqrt(2)
    gota = CS.circle(r_int, 96) + CS([[[a, a], [0, 2 * a], [-a, a], [0, 0]]])
    perfil = ext - gota.translate([0, h])
    sol = M.extrude(perfil, espesor).translate([0, 0, -espesor / 2])
    return sol.rotate([90, 0, 0]).translate([0, 0, z_base])   # (x,y,z)->(x,-z,y)


# ------------------------------------------------------------- modelo 1
def motor_solido():
    """Motor de propelente sólido experimental (≈ 15 × 64 mm)."""
    Rb = 6.0                                  # radio del cuerpo (cámara)
    # tobera convergente-divergente (exterior) + retenedor
    exterior = revolve(
        [4.7, 0.0], [4.7, 0.6],               # labio de salida
        [2.7, 8.0],                           # divergente
        [2.7, 8.6],                           # garganta
        [6.9, 12.8],                          # convergente (45°)
        [7.1, 13.0], [7.1, 16.4],             # retenedor (pieza 3)
        [Rb - 0.3, 17.2],                     # escalón hacia la rosca
        [Rb - 0.3, 19.9], [Rb, 20.2],         # chaflán 45° (sin escalón)
        [Rb, 44.0],                           # cámara de combustión (pieza 2)
        [Rb - 0.3, 44.0], [Rb - 0.3, 47.6],   # zona roscada superior
        [7.4, 49.3],                          # chaflán 45° bajo el tapón
        [7.4, 50.4], [7.0, 50.8], [7.0, 51.6], [7.4, 52.0],   # ranura del tapón
        [7.4, 53.6], [6.2, 54.8],             # hombro superior
        [2.5, 54.8], [2.5, 56.5],             # sellante + ignitor (piezas 4/5)
    )
    hueco = revolve([3.6, -0.1], [3.6, 0.0], [1.05, 8.0], [0.0, 9.1])   # divergente hueco
    # Rosca senoidal: pendiente máx. de flanco = 2πe/P ≤ 1  →  ≤ 45° (imprimible).
    # P = 1.5 mm, e = 0.22 mm  →  ≈ 43°.
    roscas = (rosca(16.6, 3.9, Rb - 0.39, Rb + 0.05, paso=1.5) +
              rosca(43.8, 4.1, Rb - 0.39, Rb + 0.05, paso=1.5))
    cuerpo = (exterior + roscas) - hueco
    return cuerpo + anilla(56.3, base=3.2)


# ------------------------------------------------------------- modelo 2
def motor_raptor():
    """Motor de combustión por etapas de metano (inspirado en Raptor 1),
    ≈ 26 × 62 mm."""
    campana_ext = bezier([12.6, 0.0], [11.6, 11.0], [8.6, 17.0], 50)
    exterior = revolve(
        [12.6, 0.0],
        campana_ext,                          # campana (bell)
        [6.8, 19.5],                          # hombro sobre el colector
        [4.6, 25.0],                          # parte superior de la tobera
        [4.4, 26.6],                          # garganta
        [6.0, 28.2],                          # expansión 45° hacia la cámara
        [6.0, 33.0],                          # cámara de combustión
        [9.2, 36.2], [9.2, 37.6],             # brida (chaflán 45° abajo)
        [7.0, 38.4], [6.6, 38.4],
        [6.6, 45.0],                          # cabezal / inyector
        [4.6, 46.0], [4.6, 48.4],             # domo superior
        [3.6, 49.0], [3.6, 50.4],             # cardán (gimbal)
    )
    hueco = revolve([11.0, -0.1], [11.0, 0.0],
                    bezier([11.0, 0.0], [9.6, 12.0], [5.6, 19.0], 40),
                    [2.6, 23.4], [0.0, 25.9])          # interior de la campana
    detalles = [
        anillo_gota(16.6, 8.0, 9.4, 2.6),     # colector de refrigeración regenerativa
        anillo_gota(23.4, 4.6, 5.6, 1.4),     # anillo superior de tobera
        anillo_gota(29.0, 5.8, 6.7, 1.2),     # aros de la cámara
        anillo_gota(31.4, 5.8, 6.7, 1.2),
        anillo_gota(41.6, 6.4, 7.2, 1.0),     # aro del cabezal
    ]
    # inyectores/válvulas alrededor del cabezal, apoyados sobre la brida
    for k in range(20):
        ang = 360 * k / 20
        if any(abs(((ang - b + 180) % 360) - 180) < 32 for b in (0, 133)):   # turbobombas
            continue
        detalles.append(M.cube([1.2, 0.7, 2.4]).translate([6.4, -0.35, 37.6]).rotate([0, 0, ang]))
    # turbobombas (dos) laterales, base cónica a 45°
    detalles += [cilindro(37.0, 7.0, 2.7, x=7.4, y=0.0), cilindro(44.0, 1.0, 2.1, x=7.4, y=0.0)]
    detalles += [cilindro(36.5, 6.5, 2.2, x=-5.0, y=5.4), cilindro(43.0, 0.8, 1.7, x=-5.0, y=5.4)]
    # tubería principal: de la turbobomba al colector (casi vertical, ≤ 25°)
    detalles.append(tuberia([(9.2, 0, 18.0), (10.6, 0.8, 24.0), (10.9, 0.6, 29.0),
                             (10.0, 0.0, 33.5), (8.4, 0.0, 37.5)], 1.35))
    # tubería secundaria
    # (por fuera de los aros de la cámara para no crear túneles)
    detalles.append(tuberia([(-6.4, -6.0, 18.0), (-6.0, -5.8, 23.0), (-5.9, -5.7, 28.0),
                             (-5.6, -5.4, 33.0), (-5.4, -5.2, 35.6)], 0.9))
    cuerpo = M.batch_boolean([exterior] + detalles, m3d.OpType.Add) - hueco
    return cuerpo + anilla(50.2)


MODELOS = {
    "llavero_motor_solido_experimental": motor_solido,
    "llavero_motor_metano_estilo_raptor": motor_raptor,
}


def a_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print(f"{'modelo':38s} {'X×Y×Z (mm)':>20s} {'vol cm³':>8s} {'g PLA*':>7s} estanco cuerpos género")
    for nombre, fn in MODELOS.items():
        sol = fn()
        tm = a_trimesh(sol)
        tm.export(OUT / f"{nombre}.stl")
        dx, dy, dz = tm.extents
        vol = tm.volume / 1000
        print(f"{nombre:38s} {dx:5.1f}×{dy:5.1f}×{dz:5.1f}    {vol:8.2f} {vol*DENSIDAD_PLA:7.2f} "
              f"{str(tm.is_watertight):7s} {len(sol.decompose()):7d} {sol.genus():6d}  zmin={tm.bounds[0,2]:.2f}")
    print("* masa maciza; con 3-4 paredes + 20 % relleno es ~65-80 % de eso.")
