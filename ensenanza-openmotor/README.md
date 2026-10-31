# Enseñando openMotor: balística interna de un motor cohete sólido

Material didáctico para aprender a usar [openMotor](https://github.com/reilleya/openMotor), el
simulador libre de balística interna para motores de propelente sólido, y para **entender la física
que hay detrás**, no solo usar la interfaz.

| Archivo | Qué es |
|---|---|
| `mini_openmotor.py` | Réplica comentada (≈250 líneas) de las ecuaciones de `motorlib`, el núcleo de openMotor, para granos BATES. Se lee de principio a fin en una sesión. |
| `practica_openmotor.py` | Caso base y tres experimentos. Genera gráficas y archivos `.ric`, `.eng` y `.csv`. |
| `resultados/motor_base.ric` | El motor de ejemplo listo para abrir en openMotor (**File ▸ Open**). |
| `resultados/motor_base.eng` | Curva de empuje para OpenRocket o RockSim. |

```bash
pip install numpy scipy matplotlib
python3 practica_openmotor.py
```

---

## 1. Objetivos de aprendizaje

Al terminar la práctica, el estudiante podrá:

1. Explicar cómo **Kn** (relación de áreas) determina la **presión de cámara**.
2. Relacionar la **geometría del grano** con la forma de la curva de empuje (progresiva, neutra o regresiva).
3. Identificar los **límites de diseño** que vigila openMotor: presión máxima, flujo másico y relación puerto/garganta.
4. Construir y simular un motor en la interfaz de openMotor y **validar** su resultado contra un modelo independiente.
5. Exportar el motor a OpenRocket para cerrar el ciclo con la simulación de vuelo.

---

## 2. Física mínima (lo que openMotor resuelve en cada paso de tiempo)

**Ley de quemado** (Saint-Robert/Vieille), por tramos de presión:

$$\dot r = a\,P_c^{\,n}$$

**Equilibrio de masa en la cámara.** Lo que se genera en la superficie que quema es igual a lo que
sale por la garganta estrangulada:

$$\rho_p\,A_b\,a\,P_c^{\,n} = \frac{P_c\,A_t}{c^*}
\quad\Longrightarrow\quad
\boxed{P_c = \left(K_n\,\rho_p\,a\,c^*\right)^{\frac{1}{1-n}}},\qquad K_n=\frac{A_b}{A_t}$$

Como $n<1$, la presión crece de forma **no lineal** con Kn. Si $n\to1$, el motor se vuelve inestable.

**Velocidad característica** (depende solo del propelente):

$$c^* = \frac{\sqrt{\gamma\,\frac{R_u}{M}\,T_c}}{\gamma\sqrt{\left(\frac{2}{\gamma+1}\right)^{\frac{\gamma+1}{\gamma-1}}}}$$

**Empuje** a partir del coeficiente de empuje de la tobera:

$$F = C_F\,A_t\,P_c,\qquad
C_F = \underbrace{\sqrt{\tfrac{2\gamma^2}{\gamma-1}\left(\tfrac{2}{\gamma+1}\right)^{\frac{\gamma+1}{\gamma-1}}\left[1-\left(\tfrac{P_e}{P_c}\right)^{\frac{\gamma-1}{\gamma}}\right]}}_{\text{momento}}
+ \underbrace{\frac{(P_e-P_a)A_e}{P_c A_t}}_{\text{presión}}$$

openMotor multiplica $C_F$ por las pérdidas de divergencia $\frac{1+\cos\alpha}{2}$, de garganta, de
fricción (0.99) y por la eficiencia que ingresa el usuario.

**Algoritmo** (el mismo que `Motor.runSimulation()`):

```
x = 0
repetir:
    Δx  = a·Pⁿ·Δt                 # 1. regresión con la presión del paso anterior
    x  += Δx
    Kn  = A_b(x) / A_t             # 2. geometría → Kn
    P   = (Kn·ρ·a·c*)^(1/(1-n))    # 3. Kn → presión (equilibrio)
    F   = C_F·A_t·P                # 4. presión → empuje
hasta que F < 0.1 % de F_max
```

> **Hipótesis que hay que discutir en clase:** el modelo es 0D y cuasi-estacionario (no hay
> llenado de la cámara ni transitorio de ignición) y **no modela el quemado erosivo**: solo te
> avisa cuando el flujo másico G supera un umbral. Por eso el empuje "salta" a su valor de régimen
> en t = 0.

---

## 3. El motor de ejemplo

| Componente | Valor |
|---|---|
| Propelente | **KNSB** (KNO₃/sorbitol 65/35), preset "Nakka - KNSB" de openMotor: ρ = 1750 kg/m³, γ = 1.136, T = 1520 K, M = 39.9 g/mol, 5 tramos de (a, n) |
| Granos | 3 × BATES, Ø 33 mm, núcleo 12.7 mm, L = 56 mm, caras sin inhibir |
| Tobera | Garganta 7 mm, salida 19 mm (ε = 7.4), η = 0.85, α_div = 12°, garganta de 3 mm de largo |
| Carcasa | 38 mm (comercial de cohetería amateur) |

**Resultado** (caso base):

| Métrica | Valor |
|---|---|
| Designación | **H178** |
| Impulso total | 236.5 N·s |
| Empuje medio / máximo | 178 / 192 N |
| Tiempo de quemado | 1.32 s |
| Presión máxima | 3.94 MPa |
| Kn inicial / máximo | 288 / 326 |
| Isp entregado | 112.6 s |
| Propelente | 214 g |
| Flujo másico máximo | 1147 kg/(m²·s), por debajo del límite de 1406 |

![Caso base](resultados/01_caso_base.png)

**Para observar:** la curva de Kn tiene forma de "joroba" suave, que es la firma de un grano BATES
bien proporcionado. Los quiebres pequeños del empuje cerca de 3.8 MPa aparecen cuando la presión
cruza de un tramo de la ley de quemado del KNSB al siguiente (líneas punteadas en la gráfica de
presión).

---

## 4. Guía paso a paso en la interfaz de openMotor

1. **Instalar**: descarga el instalador desde *Releases* en GitHub, o ejecuta desde el código fuente
   con `pip install -r requirements.txt` y `python main.py`.
2. **Unidades**: *Edit ▸ Preferences ▸ Units*. Recomiendo cambiar todo a SI (m o mm, Pa o MPa, N),
   porque viene en unidades imperiales.
3. **Propelente**: en el editor de motor, *Propellant ▸ Nakka - KNSB*. Abre *Edit Propellants* y
   muestra a los estudiantes los 5 tramos de (a, n). El KNSB tiene un **"plateau"** con n ≈ 0 entre
   1.5 y 3.8 MPa.
4. **Granos**: *Add Grain ▸ BATES*. Ingresa diámetro 33 mm, núcleo 12.7 mm y longitud 56 mm. Usa
   *Copy* para tener 3 granos.
5. **Tobera**: garganta 7 mm, salida 19 mm, eficiencia 0.85, divergencia 12°, convergencia 35° y
   largo de garganta 3 mm.
6. **Simular**: el botón *Run* (o abrir directamente `resultados/motor_base.ric`).
7. **Leer los resultados**: la gráfica principal (empuje, presión, Kn), el panel de estadísticas
   (designación, Isp, presión máxima) y las **alertas** en rojo y amarillo.
8. **Ver la regresión del grano**: en el editor de grano, la pestaña de vista muestra los contornos
   de *fast marching*. Cambia a *Finocyl* o *Star* para ver geometrías no analíticas.
9. **Exportar**: *File ▸ Export ▸ ENG* y luego importar el archivo en OpenRocket (*Motor ▸ Load*).

**Validación cruzada:** compara el panel de estadísticas de openMotor con la salida de
`practica_openmotor.py`. Las dos herramientas usan las mismas ecuaciones, así que la diferencia
debería ser menor al 1 %. Si no lo es, hay un error en el modelo o en los datos, y encontrarlo es un
buen ejercicio de ingeniería.

---

## 5. Experimentos

### Experimento A: el diámetro de garganta controla la presión

![Barrido de garganta](resultados/02_barrido_garganta.png)

| d_t [mm] | Kn₀ | P_max [MPa] | Isp [s] | t_b [s] | Clase | Alerta |
|---|---|---|---|---|---|---|
| 6.0 | 392 | 7.29 | 116.5 | 0.98 | H247 | Flujo másico > límite |
| 6.5 | 334 | 5.38 | 113.4 | 1.16 | H204 | |
| **7.0** | **288** | **3.94** | **112.6** | **1.32** | **H178** | |
| 8.0 | 220 | 2.97 | 110.1 | 1.33 | H173 | |
| 9.0 | 174 | 2.35 | 106.7 | 1.32 | H169 | Puerto/garganta < 2 |

**Preguntas:**
- ¿Por qué si se reduce la garganta 1 mm (de 7 a 6 mm) la presión casi se duplica?
  *Pista: el exponente 1/(1−n).*
- ¿Por qué el tiempo de quemado **casi no cambia** entre 7 y 9 mm, pero cae mucho a 6 mm?
  *Pista: el plateau del KNSB, donde n ≈ 0 y la tasa de quemado no depende de la presión.*
- Más presión da más Isp. ¿Qué le cuesta al diseño? Piensa en el espesor de la carcasa, el factor
  de seguridad y la velocidad de la garganta.

### Experimento B: la geometría define la forma de la curva

Los cuatro casos tienen la **misma longitud total de propelente (168 mm)**:

![Geometría](resultados/03_geometria_bates.png)

| Configuración | Comportamiento | ΔKn durante el quemado |
|---|---|---|
| 6 × 28 mm | **Regresivo**: dominan las caras, que se encogen | 64 % |
| 3 × 56 mm (L ≈ (3D+d)/2) | **Casi neutro** | 13 % |
| 2 × 84 mm | **Progresivo**: domina el núcleo, que crece | 37 % |
| 3 × 56 mm con caras inhibidas | **Muy progresivo**: solo quema el núcleo | 159 % |

**Ejercicio analítico:** para un BATES con ambas caras libres,

$$A_b(x) = \pi(d+2x)(L-2x) + 2\cdot\tfrac{\pi}{4}\left[D^2-(d+2x)^2\right]
\;\Rightarrow\;
\frac{dA_b}{dx} = 2\pi\,(L - 2d - 6x)$$

Demostrar que con $L=\frac{3D+d}{2}$ se cumple $A_b(0)=A_b(x_{\text{final}})$, y discutir por qué
eso minimiza la variación de Kn.

### Experimento C: carga volumétrica frente a flujo másico

![Núcleo](resultados/04_densidad_carga.png)

Un núcleo más estrecho mete más propelente en la carcasa y da más impulso. El costo es que **todo**
el gas de los granos de arriba tiene que pasar por un puerto pequeño. El flujo másico G = ṁ/A_puerto
se dispara en t ≈ 0, a la salida del último grano. Por encima de ~1400 kg/(m²·s) aparece el
**quemado erosivo**: el flujo arrastra la llama, la tasa de quemado sube localmente y se produce un
pico de presión que el modelo **no predice**.

**Pregunta de ingeniería:** el núcleo de 10 mm da +6 % de impulso pero viola el límite de G.
¿Lo aceptarías? ¿Qué ensayo harías antes de volar ese motor?

---

## 6. Retos para los estudiantes

1. **Diseño a especificación:** diseñar un motor de **clase I** (320–640 N·s) en carcasa de 54 mm con
   P_max < 5 MPa y ninguna alerta. Entregar el `.ric` y una justificación de cada decisión.
2. **Sensibilidad:** variar ±10 % los parámetros a, n y T del propelente. ¿Cuál afecta más al
   impulso? ¿Y a la presión máxima? ¿Qué te dice eso sobre qué hay que **medir** en el laboratorio?
3. **Validación experimental:** si tienen un banco estático, superponer la curva medida y la
   simulada, y ajustar la eficiencia de la tobera y c* hasta que coincidan. Discutir por qué los dos
   parámetros están correlacionados.
4. **Más allá de BATES:** en la interfaz, reemplazar el grano superior por un *Finocyl* de 6 aletas y
   observar el pico inicial de Kn. ¿Para qué misión querrías ese perfil?

---

*Referencias:* código de openMotor (`motorlib/motor.py`, `propellant.py`, `nozzle.py`); R. Nakka,
*Richard Nakka's Experimental Rocketry Web Site* (datos del KNSB); Sutton & Biblarz, *Rocket
Propulsion Elements*, caps. 3, 12 y 13.
