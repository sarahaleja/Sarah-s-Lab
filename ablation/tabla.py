"""Genera la tabla de parámetros en Markdown a partir de un módulo de material.

Uso:  python3 -m ablation.tabla > docs/parametros_ptfe.md
"""
from .materials import ptfe
from .parameters import Correlacion, Param


def _fmt(x):
    return f"{x:.4g}"


def tabla(modulo):
    params, corrs = [], []
    for nombre in dir(modulo):
        obj = getattr(modulo, nombre)
        if isinstance(obj, Param):
            params.append(obj)
        elif isinstance(obj, Correlacion):
            corrs.append(obj)
        elif isinstance(obj, dict) and nombre == "KINETICA":
            for variante in obj.values():
                params.extend(variante.values())
    lineas = [
        "# Parámetros iniciales del PTFE",
        "",
        "Generado automáticamente desde `ablation/materials/ptfe.py`; no editar a mano.",
        "",
        "## Parámetros",
        "",
        "| Parámetro | Valor | Unidad | Rango de sensibilidad | Estatus | Fuente | Nota |",
        "|---|---|---|---|---|---|---|",
    ]
    for p in params:
        rango = f"{_fmt(p.rango[0])} – {_fmt(p.rango[1])}" if p.rango else "—"
        lineas.append(f"| {p.nombre} | {_fmt(p.valor)} | {p.unidad} | {rango} | "
                      f"{p.estatus} | {p.fuente} | {p.nota} |")
    lineas += [
        "",
        "## Correlaciones dependientes de la temperatura",
        "",
        "| Propiedad | Expresión | Unidad | Validez [K] | Estatus | Fuente | Nota |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in corrs:
        lineas.append(f"| {c.nombre} | {c.expresion} | {c.unidad} | "
                      f"{c.T_min:.0f} – {c.T_max:.0f} | {c.estatus} | {c.fuente} | {c.nota} |")
    lineas += [
        "",
        "## Tabla de cp del C2F4 gaseoso (J/(mol K))",
        "",
        "Solo el punto de 800 K está verificado (NIST-JANAF). El resto es provisional.",
        "",
        "| T [K] | cp |",
        "|---|---|",
    ]
    lineas += [f"| {T:.0f} | {cp} |" for T, cp in modulo.CP_GAS_C2F4]
    return "\n".join(lineas) + "\n"


if __name__ == "__main__":
    print(tabla(ptfe), end="")
