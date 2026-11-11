# Plan del código: modelo termoablativo corregido del PTFE

Base: Wu et al. (2025), *Numerical Simulation of Pulsed Plasma Thruster*, Cap. 2 (arco) y Cap. 3 (láser).
En cada paso se separa lo que se conserva de Wu, lo que se corrige o agrega, y cómo se verifica.
Orden: primero el arco (Fourier, dentro de la ventana de validez, hallazgo central); el láser reutiliza el núcleo.

| Paso | Base en Wu et al. (2025) | Nuevo o corregido | Verificación | Archivo |
|---|---|---|---|---|
| 0 · Parámetros (hecho) | Tablas 2.1, 3.1, 5.2 | Reemplazadas por mediciones con origen declarado (`cierre`) | 18/18 comprobaciones contra el marco teórico | `ablation/materials/ptfe.py` |
| 1 · Fourier + Stefan | Malla fija ξ, η (Ecs. 2.21–2.24), volúmenes finitos implícitos, TDMA | Forma entálpica conservativa; Ec. 2.26 con 1/(s − θ)²; arranque de la capa fundida con espesor cero (Mitchell & Vynnycky, 2012) | Solución de Neumann (T2, τ0 = 0: no detecta el término omitido, que es ∝ τ0); pulso rectangular (Ec. 2.27) | `ablation/solver/nucleo.py` |
| 2 · Entrada de energía | Flujo superficial y radiación σεT⁴ (Ecs. 2.4, 2.10), que se conserva | Un solo canal: sin fuente volumétrica, sin término de interfaz, sin R_r ni α sobre el calor del plasma (corrige A1, A2, D1) | Balance exacto: entra = almacena + funde + reacciona + radia | `ablation/solver/fuentes.py` |
| 3 · Despolimerización | Arrhenius volumétrico y ṁ integral (Ecs. 2.8, 2.14, 2.15) | Cinética de Madorsky (1953), Hp por Hess, ρ0 = 2161 kg/m³; aviso si la piel de reacción δ < 1 nm (corrige A4, D2) | Solución estacionaria de Kemp (Ecs. 2.28–2.29); v = βI/(ρ0·Q*) | `ablation/solver/cinetica.py` |
| 4 · Descarga y enfriamiento | I0 = 0.05·V(t)·I(t)/A_g con C, V0, R_eq, L_eq (Tabla 2.1); etapa post-descarga (Ecs. 2.16–2.20) | Salida nueva: espesor fundido al terminar la descarga; q_in como parámetro de escenario | Reproducir Figs. 2.8–2.10 con los parámetros de Wu; luego comparar con los medidos | `ablation/casos/arco.py` |
| 5 · Cattaneo-Vernotte (láser) | Cap. 3: Ecs. 3.1–3.8 y transformación 3.40–3.41 | Formulación (T, q); término −∂b/∂τ completo; q(s,t) = βI(t) sin retraso; τ0 anclado por fase; pulso gaussiano (corrige D3, D4, D5) | τ0 → 0 recupera el paso 1; solución manufacturada con θ″ ≠ 0 (T2b: detecta el término −∂b/∂τ, la forma de Wu no converge); soluciones de Bessel de Wu sin la fuente duplicada (Ecs. 3.49–3.53); v/Ch < 0.5 | `ablation/solver/hiperbolico.py`, `ablation/casos/laser.py` |
| 6 · Reparto gas / fragmentos | No existe en Wu | Arco: capa fundida expulsada tras la descarga; láser: déficit de energía frente a Q* | Huber et al. (2004); masa por disparo (LES-6, prototipo) | `ablation/solver/reparto.py` |
| 7 · Sensibilidad y diseño | No existe en Wu | Barrer β_ef, q_in, λ del fundido, α (dopante C o Al) y cristalinidad | La masa total no debe depender de τ0 | `ablation/estudios/` |
| 8 · 2D en COMSOL (opcional) | — | Solo si la geometría del dispositivo lo exige | Comparar contra el 1D | — |

## Se conserva de Wu

Dos capas con fronteras móviles, malla fija, volúmenes finitos implícitos con TDMA, radiación superficial,
despolimerización de Arrhenius volumétrica y entrada de energía del arco a partir de V·I.

## Es nuevo en esta tesis

Un solo canal de energía, formulación (T, q) con el término completo de la transformación, corrección de la
errata de la Ec. 2.26, parámetros medidos con origen declarado, Hp por la ley de Hess, ventana de validez,
módulo de reparto gas / fragmentos y mapa de diseño del propelente.

## Pendientes antes del paso 4

- Agregar q_in (fracción de 5 % de Alexeev et al., 2003) a `ptfe.py` o a un módulo de dispositivo, con rango de sensibilidad.
- Verificar la tabla de c_p del C₂F₄ contra NIST-JANAF (solo el punto de 800 K está confirmado).
