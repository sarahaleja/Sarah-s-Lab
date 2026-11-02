"""
Llaveros de motores de cohete experimentales — generador paramétrico.

Impresora objetivo: Creality (FDM, boquilla 0.4 mm) · Material: PLA.

Cada llavero es un "medio sólido de revolución": el perfil del motor se gira
180° alrededor de su eje y la cara plana (el corte por el eje) queda apoyada
en la cama. Ventajas para FDM:
  * No necesita soportes (todas las superficies suben desde la cama).
  * La anilla del llavero es una pestaña plana horizontal: el esfuerzo del
    aro tira EN el plano de las capas, no las despega (máxima resistencia).

Unidades: milímetros. Ejecutar:  python3 generar_llaveros.py
Requiere: pip install manifold3d trimesh numpy matplotlib
"""
from pathlib import Path
import numpy as np
import manifold3d as m3d
import trimesh

OUT = Path(__file__).parent / "stl"
SEG = 160                      # segmentos de revolución (360°)
DENSIDAD_PLA = 1.24            # g/cm³

# Pestaña de la anilla (común a todos los modelos)
TAB_ESPESOR = 3.6              # mm (9 capas de 0.4 / 18 de 0.2)
TAB_ANCHO = 11.0
TAB_LARGO = 9.0                # cuánto sobresale del motor
AGUJERO_D = 5.0                # cabe una anilla partida estándar


# ---------------------------------------------------------------- utilidades
def bezier(p0, p1, p2, n=40):
    """Curva de Bézier cuadrática entre p0 y p2 con punto de control p1."""
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(np.asarray, (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def arco(c, r, a0, a1, n=24):
    a = np.radians(np.linspace(a0, a1, n))
    return np.c_[c[0] + r * np.cos(a), c[1] + r * np.sin(a)]


def perfil(*tramos):
    """Une tramos (r, z) en un polígono cerrado que toca el eje r=0."""
    pts = np.vstack([np.atleast_2d(t) for t in tramos])
    # elimina puntos duplicados consecutivos
    keep = np.r_[True, np.linalg.norm(np.diff(pts, axis=0), axis=1) > 1e-6]
    pts = pts[keep]
    pts = np.vstack([[0.0, pts[0, 1]], pts, [0.0, pts[-1, 1]]])
    # orientación antihoraria para manifold
    area = 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
    return pts if area > 0 else pts[::-1]


def anillos(z_list, r, alto=0.8):
    """Rectángulos (r,z) que añaden aros de refuerzo / colectores."""
    return [np.array([[0, z], [r, z], [r, z + alto], [0, z + alto]]) for z in z_list]


def medio_revolucion(poligonos):
    """Gira perfiles (r, z) 180° y los deja con la cara plana en z=0.
    Ejes finales: Y = eje del motor (tobera en y=0), Z = altura sobre la cama."""
    cs = m3d.CrossSection([p.tolist() for p in poligonos[:1]])
    for p in poligonos[1:]:
        cs = cs + m3d.CrossSection([p.tolist()])
    sol = m3d.Manifold.revolve(cs, SEG, 180.0)          # eje → Z, mitad y≥0
    # rotación +90° en X: (x, y, z) → (x, -z, y): eje del motor → -Y, mitad → +Z.
    # Se refleja Y para que la tobera quede en y=0 y el inyector en +Y.
    return sol.rotate([90.0, 0.0, 0.0]).mirror([0.0, 1.0, 0.0])


def pestana(y_iny):
    """Pestaña plana con agujero, unida al extremo del inyector (y = y_iny),
    creciendo hacia +Y (lejos de la tobera). Se solapa 4 mm con el domo."""
    yc = y_iny + TAB_LARGO                     # centro del agujero
    base = m3d.CrossSection.square([TAB_ANCHO, TAB_LARGO + 4]).translate([-TAB_ANCHO / 2, y_iny - 4])
    punta = m3d.CrossSection.circle(TAB_ANCHO / 2, 96).translate([0, yc])
    agujero = m3d.CrossSection.circle(AGUJERO_D / 2, 96).translate([0, yc])
    return m3d.Manifold.extrude((base + punta) - agujero, TAB_ESPESOR)


def ensamblar(perfiles):
    cuerpo = medio_revolucion(perfiles)
    bb = cuerpo.bounding_box()            # (xmin, ymin, zmin, xmax, ymax, zmax)
    y_iny = bb[4]                         # extremo del inyector (máx. Y)
    llavero = cuerpo + pestana(y_iny)
    return llavero.translate([0, -llavero.bounding_box()[1], 0])


# ---------------------------------------------------------------- modelos
def motor_campana():
    """Motor de propelente líquido con tobera de campana (tipo Rao) y
    camisa de refrigeración regenerativa (aros)."""
    Re, Rt, Rc = 9.5, 3.6, 6.5            # radios: salida, garganta, cámara
    tobera = bezier([Re, 0], [5.0, 9.0], [Rt + 0.4, 19.0])          # campana
    garganta = arco([Rt + 2.0, 20.0], 2.0, 210, 150)                 # radio de garganta
    convergente = bezier([Rt + 0.3, 21.6], [Rc, 24.0], [Rc, 27.0])
    camara = np.array([[Rc, 35.0]])
    domo = arco([0, 35.0], Rc, 0, 60)                                # placa inyectora
    labio = np.array([[Re + 0.6, 0.0], [Re + 0.6, 1.0]])             # labio de salida
    p = perfil(labio, tobera, garganta, convergente, camara, domo)
    extras = anillos([27.5, 30.5, 33.5], Rc + 0.6) + anillos([12.0], 6.5, 0.9)
    return ensamblar([p] + extras)


def motor_doble_campana():
    """Tobera de doble campana (dual-bell): la inflexión permite dos modos de
    altitud — experimental para etapas que vuelan de mar a vacío."""
    Re, Ri, Rt, Rc = 9.5, 6.4, 3.4, 6.2
    ext = bezier([Re, 0], [8.4, 4.5], [Ri, 9.0])                     # 2ª campana
    base = bezier([Ri, 9.0], [4.6, 13.0], [Rt + 0.3, 19.5])          # 1ª campana
    garganta = arco([Rt + 1.8, 21.0], 1.8, 215, 145)
    convergente = bezier([Rt + 0.4, 22.4], [Rc, 24.5], [Rc, 27.5])
    domo = np.vstack([[Rc, 34.0], arco([0, 34.0], Rc, 0, 55)])
    labio = np.array([[Re + 0.5, 0.0], [Re + 0.5, 0.9]])
    p = perfil(labio, ext, base, garganta, convergente, domo)
    extras = anillos([9.0], Ri + 0.7, 0.9) + anillos([28.5, 31.5], Rc + 0.5)
    return ensamblar([p] + extras)


def motor_aerospike():
    """Aerospike anular truncado: cámara toroidal y espiga central que
    se autocompensa con la altitud."""
    Rcw, Rsp = 9.5, 6.0                  # radio de la carcasa y raíz de la espiga
    espiga = bezier([1.6, 0.0], [2.6, 14.0], [Rsp, 26.0])           # espiga truncada
    garganta = np.array([[Rsp + 0.6, 26.0], [Rsp + 0.6, 27.0]])     # salida anular
    carcasa = np.array([[Rcw, 27.0], [Rcw, 36.0]])
    domo = arco([0, 36.0], Rcw, 0, 35)
    base_esp = np.array([[1.6, 0.0]])
    p = perfil(base_esp, espiga, garganta, carcasa, domo)
    # cámara/colector toroidal superior marcado
    extras = anillos([29.0, 33.0], Rcw + 0.6, 1.0)
    return ensamblar([p] + extras)


def motor_detonacion_rotativa():
    """Motor de detonación rotativa (RDE): cámara anular corta con cuerpo
    central y tobera tipo tapón (plug) — un concepto en investigación activa."""
    Ro, Rcb = 8.5, 5.5
    plug = bezier([1.4, 0.0], [3.0, 7.0], [Rcb, 10.0])
    cuerpo = np.array([[Rcb, 22.0]])
    anillo_ext = np.array([[Ro, 10.0], [Ro, 22.0]])
    domo = np.vstack([[Ro, 24.0], arco([0, 24.0], Ro, 0, 40)])
    p_plug = perfil(np.array([[1.4, 0.0]]), plug, cuerpo, np.array([[Rcb, 24.0]]), domo)
    # carcasa exterior separada por la ranura anular (canal de detonación)
    carcasa = np.array([[Rcb + 1.2, 10.0], [Ro, 10.0], [Ro, 24.0], [Rcb + 1.2, 24.0]])
    inyectores = anillos([25.5, 28.0], 4.0, 1.0)
    return ensamblar([p_plug, carcasa] + inyectores)


MODELOS = {
    "llavero_motor_campana": motor_campana,
    "llavero_tobera_doble_campana": motor_doble_campana,
    "llavero_aerospike": motor_aerospike,
    "llavero_motor_detonacion_rotativa": motor_detonacion_rotativa,
}


def a_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print(f"{'modelo':38s} {'X×Y×Z (mm)':>20s} {'vol cm³':>8s} {'g PLA*':>7s} estanco")
    for nombre, fn in MODELOS.items():
        tm = a_trimesh(fn())
        tm.export(OUT / f"{nombre}.stl")
        dx, dy, dz = tm.extents
        vol = tm.volume / 1000
        print(f"{nombre:38s} {dx:5.1f}×{dy:5.1f}×{dz:5.1f}    {vol:8.2f} {vol*DENSIDAD_PLA:7.2f} {tm.is_watertight}")
    print("* masa sólida al 100 %; con 4 paredes + 20 % relleno es ~60-70 % de eso.")
