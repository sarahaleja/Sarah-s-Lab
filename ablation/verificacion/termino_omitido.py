"""Verificación simbólica del término omitido en Wu et al. (2025), Ecs. 3.40-3.41.

Wu et al. transforman la ecuación de Cattaneo-Vernotte,

    ∂T/∂t + τ0 ∂²T/∂t² = (difusión) + (fuentes),

a coordenadas que siguen las fronteras móviles:

    capa cristalina:  ξ = x / θ(t)
    capa fundida:     η = (x − θ(t)) / (s(t) − θ(t))

Con u(ξ, τ) = T(x, t) y τ = t, la primera derivada es (Ec. 3.39 de Wu, correcta)

    ∂T/∂t = u_τ − b u_ξ ,   b = −∂ξ/∂t|ₓ  (velocidad de la malla).

Al aplicar el operador dos veces, b también se deriva respecto al tiempo,
porque depende de θ(t) y s(t). Resulta

    ∂²T/∂t² = u_ττ − 2b u_ξτ + b² u_ξξ + (b ∂b/∂ξ − ∂b/∂τ) u_ξ .

Al pasar todo al lado derecho, el coeficiente correcto de u_ξ es

    b − τ0 b ∂b/∂ξ + τ0 ∂b/∂τ ,

y Wu escribe solo  b − τ0 b ∂b/∂ξ : falta  +τ0 ∂b/∂τ , que contiene la
aceleración de las fronteras (θ̈, s̈).

Uso:  python3 -m ablation.verificacion.termino_omitido
"""

import sympy as sp

x, t, tau0 = sp.symbols("x t tau0", real=True)
th = sp.Function("theta")(t)
s = sp.Function("s")(t)
X = sp.Symbol("X")  # coordenada transformada genérica (ξ o η)
tau = sp.Symbol("tau")


def verificar(nombre, X_de_xt, x_de_Xt, coef_wu):
    """Compara la derivada exacta con las formas correcta y de Wu.

    X_de_xt: X(x, t); x_de_Xt: inversa x(X, t); coef_wu: coeficiente de u_X que
    Wu escribe en el lado derecho, como expresión en X y t.
    """
    u = sp.Function("u")
    T = u(X_de_xt, t)  # T(x, t) = u(X(x,t), t)

    # Lado izquierdo exacto de Cattaneo: ∂T/∂t + τ0 ∂²T/∂t², en coordenadas (X, τ)
    lhs = sp.diff(T, t) + tau0 * sp.diff(T, t, 2)
    lhs = lhs.subs(x, x_de_Xt).doit()

    # Pasar las derivadas de u a símbolos simples
    U = sp.Function("U")(X, t)
    lhs = lhs.subs(u(X, t), U)
    lhs = sp.simplify(lhs.replace(
        lambda e: isinstance(e, sp.Subs), lambda e: e.doit()))
    lhs = lhs.subs(u(X, t), U)

    # Coeficiente exacto de U_X (lado izquierdo); en el derecho cambia de signo
    uX = sp.Derivative(U, X)
    lhs_exp = sp.expand(lhs)
    coef_lhs = lhs_exp.coeff(uX)
    coef_rhs_exacto = sp.simplify(-coef_lhs)

    # Forma general: b − τ0 b b_X + τ0 b_τ
    b = -sp.diff(X_de_xt, t).subs(x, x_de_Xt)
    b = sp.simplify(b)
    b_X = sp.diff(b, X)
    b_t = sp.diff(b, t)  # a X fijo
    coef_correcto = b - tau0 * b * b_X + tau0 * b_t

    ok_correcto = sp.simplify(coef_rhs_exacto - coef_correcto) == 0
    faltante = sp.simplify(coef_rhs_exacto - coef_wu)
    ok_wu = faltante == 0

    print(f"--- {nombre} ---")
    print("b (velocidad de malla)       :", sp.simplify(b))
    print("coef. exacto de u_X (der.)   :", sp.factor(coef_rhs_exacto))
    print("forma b − τ0·b·b_X + τ0·b_τ  :", "COINCIDE" if ok_correcto else "NO coincide")
    print("forma de Wu                  :", "COINCIDE" if ok_wu else "NO coincide")
    print("término que falta en Wu      :", sp.factor(faltante))
    print("igual a τ0·∂b/∂τ             :", sp.simplify(faltante - tau0 * b_t) == 0)
    print()
    return ok_correcto and not ok_wu


thd, sd = sp.diff(th, t), sp.diff(s, t)

# Capa cristalina: ξ = x/θ.  Wu, Ec. 3.40: ξθ̇/θ − τ0 ξ (θ̇/θ)²
ok1 = verificar(
    "Capa cristalina (Ec. 3.40)",
    x / th, X * th,
    X * thd / th - tau0 * X * (thd / th) ** 2,
)

# Capa fundida: η = (x−θ)/(s−θ).  Wu, Ec. 3.41: b [1 − τ0 (ṡ−θ̇)/(s−θ)]
b_m = ((1 - X) * thd + X * sd) / (s - th)
ok2 = verificar(
    "Capa fundida (Ec. 3.41)",
    (x - th) / (s - th), th + X * (s - th),
    b_m * (1 - tau0 * (sd - thd) / (s - th)),
)

if __name__ == "__main__":
    print("Resultado:", "término omitido CONFIRMADO en ambas capas"
          if ok1 and ok2 else "revisar")
