"""Genera preview.png (render z-buffer ortográfico, sombreado Lambert) de cada llavero.
Uso: python3 render_preview.py"""
from pathlib import Path
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path(__file__).parent

def render(m, elev=40, azim=-35, px=14):
    a, e = np.radians(azim), np.radians(elev)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e - np.pi/2), -np.sin(e - np.pi/2)], [0, np.sin(e - np.pi/2), np.cos(e - np.pi/2)]])
    R = Rx @ Rz
    v = (m.vertices - m.bounds.mean(0)) @ R.T
    n = m.face_normals @ R.T
    v[:, :2] = (v[:, :2] - v[:, :2].min(0)) * px + 10
    W, H = (v[:, :2].max(0) + 10).astype(int)
    zb = np.full((H, W), -np.inf); img = np.ones((H, W, 3))
    luz = np.array([-0.4, 0.5, 0.77]); luz /= np.linalg.norm(luz)
    base = np.array([0.93, 0.42, 0.13])
    for f, nf in zip(m.faces, n):
        if nf[2] <= 0: continue
        t = v[f]; x0, y0 = np.floor(t[:, :2].min(0)).astype(int); x1, y1 = np.ceil(t[:, :2].max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        p = np.c_[xs.ravel() + .5, ys.ravel() + .5]
        T = np.array([t[1, :2] - t[0, :2], t[2, :2] - t[0, :2]]).T
        if abs(np.linalg.det(T)) < 1e-9: continue
        l = np.linalg.solve(T, (p - t[0, :2]).T); l1, l2 = l; l0 = 1 - l1 - l2
        ok = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not ok.any(): continue
        z = l0 * t[0, 2] + l1 * t[1, 2] + l2 * t[2, 2]
        X, Y, z = xs.ravel()[ok], ys.ravel()[ok], z[ok]
        upd = z > zb[Y, X]
        X, Y, z = X[upd], Y[upd], z[upd]
        zb[Y, X] = z
        img[Y, X] = base * (0.3 + 0.7 * max(nf @ luz, 0)) + 0.15 * max(nf @ luz, 0) ** 20
    return np.clip(img[::-1], 0, 1)

stls = sorted((D / "stl").glob("*.stl"))
fig, axs = plt.subplots(1, len(stls), figsize=(4.2 * len(stls), 6.5), facecolor="white")
for ax, f in zip(axs, stls):
    ax.imshow(render(trimesh.load(f))); ax.axis("off")
    ax.set_title(f.stem.replace("llavero_", "").replace("_", " "), fontsize=12)
plt.tight_layout(); plt.savefig(D / "preview.png", dpi=100)
