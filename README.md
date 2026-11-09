# Sarah-s-Lab
Where physics meets research, code &amp; visualization.  A personal space to explore my research, projects, and scientific ideas — from thermal transport and space propulsion to interactive simulations that make complex physics easier to see and understand.

## Modelo termoablativo del PTFE (`ablation/`)

Modelo numérico de la ablación del PTFE como propelente de propulsores de plasma pulsado,
construido a partir de la corrección del modelo de Wu et al. (2025).

- `ablation/parameters.py`: estructura `Param` / `Correlacion` con valor, rango, fuente y estatus
  epistémico (anclado, acotado, estimado, supuesto, por_verificar).
- `ablation/materials/ptfe.py`: parámetros iniciales del PTFE y funciones de propiedades.
  Es la fuente única de verdad del modelo.
- `docs/parametros_ptfe.md`: tabla generada desde el código (`python3 -m ablation.tabla`).
- `tests/test_ptfe.py`: comprueba que los parámetros reproducen los valores del marco teórico
  (`python3 -m tests.test_ptfe`).

Requiere solo Python 3 (biblioteca estándar).
