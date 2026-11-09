# Parámetros iniciales del PTFE

Generado automáticamente desde `ablation/materials/ptfe.py`; no editar a mano.

## Origen de los parámetros

De 28 entradas (parámetros y correlaciones):

- **21** física independiente de la ablación
- **4** de escenario (análisis de sensibilidad)
- **2** calibrados contra ablación (solo variante de comparación)
- **1** datos de ablación usados solo como referencia

Ningún parámetro del caso central se ajusta al resultado de ablación que se busca predecir.

## Parámetros

| Parámetro | Valor | Unidad | Rango de sensibilidad | Estatus | Cierre | Fuente | Nota |
|---|---|---|---|---|---|---|---|
| C_L, velocidad longitudinal (294 K, 5 MHz) | 1312 | m/s | 1312 – 1410 | anclado | fisica | Rae & Brown (2016) | Incertidumbre experimental ±5 m/s; rango entre fuentes 1312-1410 m/s. |
| C_T, velocidad transversal (294 K, 5 MHz) | 518 | m/s | 517 – 519 | anclado | fisica | Rae & Brown (2016) |  |
| Fluencia umbral de ablación a 1064 nm (PTFE sinterizado, 5 ns) | 3e+04 | J/m2 | — | anclado | referencia | Huber, Heitz & Bäuerle (2004) | 3 J/cm^2; régimen fuera de la ventana del modelo continuo. |
| Entalpía de las transiciones sólido-sólido (19-35 °C) | 7760 | J/kg | — | anclado | fisica | Blumm et al. (2010) | Se desprecia en el modelo (~0.3 % de Q*). |
| Hm, entalpía de fusión | 4.06e+04 | J/kg | 4.06e+04 – 5.86e+04 | acotado | fisica | Blumm et al. (2010) | Variante: 58.6 kJ/kg (Wu et al., 2025), compatible con ~60 % de cristalinidad. |
| Intensidad máxima de validez | 2e+10 | W/m2 | 2e+10 – 3e+10 | estimado | fisica | Tesis (Sec. 2.4) |  |
| Ap (Madorsky) | 4.7e+18 | 1/s | — | anclado | fisica | Madorsky et al. (1953) |  |
| Bp (Madorsky) | 4.051e+04 | K | — | anclado | fisica | Madorsky et al. (1953): Ea = 80.5 kcal/mol | Medida entre 697 y 786 K; el modelo la extrapola hasta ~2000 K. |
| Ap (Wu, Tabla 5.2) | 3.1e+19 | 1/s | — | acotado | calibrado | Wu et al. (2025), Tabla 5.2 |  |
| Bp (Wu, Tabla 5.2) | 4.177e+04 | K | — | acotado | calibrado | Wu et al. (2025), Tabla 5.2 |  |
| T0, temperatura inicial | 298.1 | K | — | supuesto | escenario | Escenario |  |
| Tm, temperatura de fusión nominal | 600 | K | 600 – 619 | acotado | fisica | Wu et al. (2025); Starkweather et al. (1982): 602 K refundido, 619 K virgen | La fusión real se distribuye en 513-633 K (Blumm et al., 2010). |
| a_s, difusividad térmica del sólido | 1.22e-07 | m2/s | 1.07e-07 – 1.35e-07 | acotado | fisica | Blumm et al. (2010); Price & Jarratt (2002) | Constante en T: las mediciones varían -2 a -7 % entre 323 y 505 K. |
| alpha a 1064 nm, cota superior en PTFE sinterizado | 200 | 1/m | 100 – 300 | estimado | fisica | Estimada de Huber, Heitz & Bäuerle (2004) | Equivale a 1-3 cm^-1. El 0.22 cm^-1 de Wu et al. no está medido a 1064 nm. |
| beta_ef, fracción absorbida efectiva | 0.8 | - | 0.7 – 0.9 | supuesto | escenario | Supuesto de escenario (Sec. 2.4) |  |
| cp del C2F4 gaseoso (tabla) | 115.6 | J/(mol K) | — | por_verificar | fisica | NIST-JANAF (Chase, 1998); puntos distintos de 800 K provisionales |  |
| lambda_m, conductividad del fundido | 0.245 | W/(m K) | 0.135 – 0.36 | supuesto | escenario | Wu et al. (2025), función lambda_a(Tm); origen probable Arai (1979) | Sin medición primaria verificada: entra al análisis de sensibilidad. |
| n, índice de refracción | 1.35 | - | 1.35 – 1.37 | acotado | fisica | Literatura general (Sec. 3.4) |  |
| Espesor mínimo de la piel de reacción | 1e-09 | m | — | supuesto | escenario | Criterio declarado de la tesis (~8 unidades CF2) |  |
| rho0, densidad de referencia para la recesión | 2161 | kg/m3 | 1933 – 2161 | acotado | fisica | Sólido virgen, Blumm et al. (2010) | Variante 1933 kg/m3 (Wu et al., 2025): ~12 % de diferencia en v. |
| s_ef,m, velocidad efectiva del fundido a frecuencia térmica | 291 | m/s | 227 – 510 | estimado | fisica | Estimación de la tesis (Sec. 2.3) |  |
| tau0,m, tiempo de relajación del fundido | 1.8e-12 | s | 2.5e-13 – 2.3e-12 | estimado | fisica | Tesis: modelo de dos canales (Sec. 2.3) |  |
| tau0,s, tiempo de relajación del sólido (~530 K) | 7.5e-13 | s | 2.2e-13 – 4.8e-12 | estimado | fisica | Tesis: Chester (1963) generalizado, entradas de Rae & Brown (2016) |  |

## Correlaciones dependientes de la temperatura

| Propiedad | Expresión | Unidad | Validez [K] | Estatus | Cierre | Fuente | Nota |
|---|---|---|---|---|---|---|---|
| cp_m(T) | 1065 + 0.653 T | J/(kg K) | 600 – 640 | acotado | fisica | Pendiente de Wu et al. (2025), anclada a ~1.47 J/(g K) en Tm (Blumm et al., 2010) | Por encima de ~640 K es extrapolación declarada. |
| cp_s(T) | 514.97 + 1.563 T | J/(kg K) | 298 – 600 | acotado | fisica | Ou et al. (2022); dentro de ±4 % de Blumm et al. (2010) |  |
| kappa_T,m(T) | 2.06e-5 exp(9.38e-3 T(°C)) cm2/kgf | 1/Pa | 603 – 643 | anclado | fisica | Zoller (1978) vía Starkweather et al. (1982) |  |
| rho_m(T) | 1/V0, V0 = 0.3200 + 9.586e-4 T(°C) cm3/g | kg/m3 | 603 – 643 | anclado | fisica | Zoller (1978) vía Starkweather et al. (1982) | Fuera de 330-370 °C es extrapolación declarada. |
| rho_s(T) | interpolación lineal entre 2161 kg/m3 (295 K) y 2041 kg/m3 (423 K) | kg/m3 | 295 – 600 | acotado | fisica | Blumm et al. (2010) | Extrapolación lineal declarada entre 423 y 600 K. |

## Tabla de cp del C2F4 gaseoso (J/(mol K))

Solo el punto de 800 K está verificado (NIST-JANAF). El resto es provisional.

| T [K] | cp |
|---|---|
| 298 | 80.5 |
| 500 | 101.0 |
| 800 | 115.6 |
| 1000 | 121.0 |
| 1500 | 127.6 |
| 2000 | 130.5 |
| 3000 | 132.5 |
