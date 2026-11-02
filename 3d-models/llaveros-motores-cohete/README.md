# Llaveros — motores de cohete experimentales 🚀

Cuatro llaveros pequeños (≈ 4–5,5 cm) para imprimir en **impresora Creality (FDM) con PLA**.

![preview](preview.png)

| Archivo (`stl/`) | Motor | Tamaño X×Y×Z (mm) | PLA aprox.* |
|---|---|---|---|
| `llavero_motor_campana.stl` | Motor líquido con tobera de campana (tipo Rao) + camisa regenerativa | 20 × 55 × 10 | ~2,4 g |
| `llavero_tobera_doble_campana.stl` | Tobera *dual-bell*: inflexión que da dos modos de altitud | 20 × 54 × 10 | ~2,3 g |
| `llavero_aerospike.stl` | Aerospike anular truncado: se autocompensa con la altitud | 20 × 56 × 10 | ~2,5 g |
| `llavero_motor_detonacion_rotativa.stl` | RDE: canal anular de detonación + cuerpo central tipo *plug* | 17 × 44 × 8,5 | ~2,0 g |

\*Con 4 paredes y 20 % de relleno. Macizo pesan 3–3,8 g.

## Diseño: por qué tienen la espalda plana
Cada motor es **medio sólido de revolución**: el perfil se gira 180° alrededor del eje y la cara de corte queda sobre la cama.
- **Sin soportes.** Todas las superficies crecen desde la cama.
- **Anilla resistente.** La pestaña es horizontal, así que el tirón del aro va *a lo largo* de las capas y no las separa. Es el modo de falla típico del PLA impreso en vertical.
- **Validado.** Cada malla es estanca (*watertight*), de 1 solo cuerpo y con un único agujero (género 1). Todo apoya en z = 0.

## Ajustes recomendados (Creality Print / Cura / OrcaSlicer)
| Parámetro | Valor |
|---|---|
| Boquilla / capa | 0,4 mm / **0,12–0,16 mm**: las curvas de las toberas salen mucho más suaves |
| Paredes | **4** (o relleno 100 %; son piezas pequeñas) |
| Relleno | 20–30 % giroide |
| Temperatura | 200–210 °C boquilla, 60 °C cama |
| Soportes | **Ninguno** |
| Adhesión | Borde (*brim*) de 3 mm, recomendado para la punta fina del aerospike |
| Orientación | Tal como viene: cara plana abajo |

Anilla: agujero de Ø 5 mm, compatible con anillas partidas estándar de 20–25 mm.

## Modificar / regenerar
Todo es paramétrico (radios de garganta, salida, cámara, tamaño de la pestaña…):
```bash
pip install manifold3d trimesh numpy matplotlib
python3 generar_llaveros.py   # escribe stl/*.stl e imprime dimensiones, volumen y masa
python3 render_preview.py     # regenera preview.png
```
Para escalar un modelo, basta escalarlo en el slicer (p. ej. al 80 %). No bajes la garganta de ~2,5 mm de radio para que no quede frágil.
