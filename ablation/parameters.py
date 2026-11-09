"""Estructura de datos para parámetros físicos con trazabilidad.

Cada parámetro lleva su valor central, unidad, rango de sensibilidad,
fuente y estatus epistémico, siguiendo la convención del marco teórico:

- anclado:       medido directamente o derivado en forma cerrada de una medición.
- acotado:       respaldado por más de una fuente, con dispersión conocida.
- estimado:      calculado con supuestos de modelo declarados.
- supuesto:      parámetro de escenario, se explora con análisis de sensibilidad.
- por_verificar: valor provisional que debe contrastarse con su fuente primaria.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple

ESTATUS_VALIDOS = ("anclado", "acotado", "estimado", "supuesto", "por_verificar")


@dataclass(frozen=True)
class Param:
    nombre: str
    valor: float
    unidad: str
    fuente: str
    estatus: str
    rango: Optional[Tuple[float, float]] = None
    nota: str = field(default="")

    def __post_init__(self):
        if self.estatus not in ESTATUS_VALIDOS:
            raise ValueError(f"{self.nombre}: estatus '{self.estatus}' no válido")
        if self.rango is not None:
            lo, hi = self.rango
            if not lo <= self.valor <= hi:
                raise ValueError(f"{self.nombre}: valor fuera de su rango {self.rango}")

    def __float__(self):
        return float(self.valor)


@dataclass(frozen=True)
class Correlacion:
    """Propiedad dependiente de la temperatura, con intervalo de validez."""

    nombre: str
    expresion: str
    unidad: str
    T_min: float
    T_max: float
    fuente: str
    estatus: str
    nota: str = ""

    def __post_init__(self):
        if self.estatus not in ESTATUS_VALIDOS:
            raise ValueError(f"{self.nombre}: estatus '{self.estatus}' no válido")
