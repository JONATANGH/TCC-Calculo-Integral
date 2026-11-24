"""Lógica matemática del TCC de Cálculo Integral.

Contiene las 10 integrales definidas asignadas, el procedimiento paso a paso
de cada una, el cálculo exacto (SymPy) y la verificación numérica (SciPy).
"""
import re

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application)
from scipy import integrate as sci

x = sp.symbols("x")
pi, e = sp.pi, sp.E


def _i(n, f, a, b, latex, tecnica, pasos):
    return {"n": n, "f": f, "a": a, "b": b, "latex": latex,
            "tecnica": tecnica, "pasos": pasos}


INTEGRALES = [
    _i(1, 3*x**2 + 2*x + 1, 0, 2,
       r"\int_{0}^{2} (3x^2+2x+1)\,dx",
       "Integral de función polinómica (regla de la potencia y linealidad)",
       [
           "Aplicamos linealidad: ∫(3x² + 2x + 1)dx = 3∫x²dx + 2∫x dx + ∫1 dx.",
           "Regla de la potencia ∫xⁿdx = xⁿ⁺¹/(n+1):\n   F(x) = x³ + x² + x.",
           "Teorema Fundamental del Cálculo: ∫₀² f(x)dx = F(2) − F(0).",
           "F(2) = 8 + 4 + 2 = 14   y   F(0) = 0.",
           "Resultado: 14 − 0 = 14.",
       ]),
    _i(2, 1/x, 1, e,
       r"\int_{1}^{e} \frac{1}{x}\,dx",
       "Integral logarítmica (función 1/x y logaritmo natural)",
       [
           "La antiderivada de 1/x es F(x) = ln|x|.",
           "Teorema Fundamental del Cálculo: F(e) − F(1).",
           "F(e) = ln(e) = 1   y   F(1) = ln(1) = 0.",
           "Resultado: 1 − 0 = 1.",
       ]),
    _i(3, 2*x*sp.exp(x**2), 0, 1,
       r"\int_{0}^{1} 2x\,e^{x^2}\,dx",
       "Sustitución (cambio de variable, u = x²)",
       [
           "Sea u = x²  →  du = 2x dx.",
           "Cambiamos los límites: x = 0 → u = 0;  x = 1 → u = 1.",
           "La integral queda: ∫₀¹ eᵘ du.",
           "Antiderivada: F(u) = eᵘ.",
           "Evaluamos: e¹ − e⁰ = e − 1.",
       ]),
    _i(4, sp.sin(x), 0, pi/2,
       r"\int_{0}^{\pi/2} \mathrm{sen}(x)\,dx",
       "Integral trigonométrica (antiderivada de sen(x))",
       [
           "La antiderivada de sen(x) es F(x) = −cos(x).",
           "Teorema Fundamental del Cálculo: F(π/2) − F(0).",
           "F(π/2) = −cos(π/2) = 0   y   F(0) = −cos(0) = −1.",
           "Resultado: 0 − (−1) = 1.",
       ]),
    _i(5, x*sp.exp(x), 0, 1,
       r"\int_{0}^{1} x\,e^{x}\,dx",
       "Integración por partes (producto de función algebraica y exponencial)",
       [
           "Fórmula: ∫u dv = u·v − ∫v du.",
           "Elegimos u = x → du = dx;   dv = eˣ dx → v = eˣ.",
           "∫x eˣ dx = x eˣ − ∫eˣ dx = x eˣ − eˣ = eˣ(x − 1).",
           "Evaluamos: F(1) = e(0) = 0   y   F(0) = 1·(−1) = −1.",
           "Resultado: 0 − (−1) = 1.",
       ]),
    _i(6, x/(x**2 + 1), 0, 2,
       r"\int_{0}^{2} \frac{x}{x^2+1}\,dx",
       "Sustitución racional (u = x² + 1)",
       [
           "Sea u = x² + 1  →  du = 2x dx  →  x dx = du/2.",
           "Límites: x = 0 → u = 1;  x = 2 → u = 5.",
           "La integral queda: (1/2)∫₁⁵ (1/u) du.",
           "Antiderivada: (1/2) ln|u|.",
           "Evaluamos: (1/2)(ln 5 − ln 1) = (1/2) ln 5.",
       ]),
    _i(7, 1/((x + 1)*(x + 2)), 0, 1,
       r"\int_{0}^{1} \frac{1}{(x+1)(x+2)}\,dx",
       "Fracciones parciales",
       [
           "Descomponemos: 1/((x+1)(x+2)) = A/(x+1) + B/(x+2).",
           "1 = A(x+2) + B(x+1).  Con x = −1 → A = 1;  con x = −2 → B = −1.",
           "Integramos: ∫[1/(x+1) − 1/(x+2)]dx = ln|x+1| − ln|x+2| = ln|(x+1)/(x+2)|.",
           "F(1) = ln(2/3)   y   F(0) = ln(1/2).",
           "Resultado: ln(2/3) − ln(1/2) = ln(4/3).",
       ]),
    _i(8, sp.sec(x)**2, 0, pi/4,
       r"\int_{0}^{\pi/4} \sec^2(x)\,dx",
       "Integral trigonométrica (antiderivada de tan(x))",
       [
           "La antiderivada de sec²(x) es F(x) = tan(x).",
           "Teorema Fundamental del Cálculo: F(π/4) − F(0).",
           "F(π/4) = 1   y   F(0) = 0.",
           "Resultado: 1 − 0 = 1.",
       ]),
    _i(9, x*sp.sqrt(1 + x**2), 0, 1,
       r"\int_{0}^{1} x\sqrt{1+x^2}\,dx",
       "Sustitución con radicales (u = 1 + x²)",
       [
           "Sea u = 1 + x²  →  du = 2x dx  →  x dx = du/2.",
           "Límites: x = 0 → u = 1;  x = 1 → u = 2.",
           "La integral queda: (1/2)∫₁² u^(1/2) du.",
           "Antiderivada: (1/2)·(2/3)u^(3/2) = (1/3)u^(3/2).",
           "Evaluamos: (1/3)(2^(3/2) − 1) = (2√2 − 1)/3.",
       ]),
    _i(10, x**2 - x - 2, -1, 2,
       r"\int_{-1}^{2} (x^2-x-2)\,dx",
       "Integral polinómica con interpretación de área neta",
       [
           "Antiderivada: F(x) = x³/3 − x²/2 − 2x.",
           "F(2) = 8/3 − 2 − 4 = −10/3.",
           "F(−1) = −1/3 − 1/2 + 2 = 7/6.",
           "Resultado: −10/3 − 7/6 = −27/6 = −9/2.",
           "Interpretación: x² − x − 2 = (x−2)(x+1) ≤ 0 en [−1, 2], por eso el "
           "área neta es negativa; el área geométrica es 9/2 = 4.5.",
       ]),
]


def _txt(expr):
    """Pasa una expresión de SymPy a texto legible en español."""
    return (str(expr).replace("**", "^").replace("log", "ln")
            .replace("sqrt(2)", "√2").replace("sqrt", "√")
            .replace("sin(x)/cos(x)", "tan(x)")
            .replace("sin(", "sen(")
            .replace("exp(", "e^(")
            .replace("pi", "π")
            .replace("E", "e").replace("*", "·"))


def txt_lim(v):
    """Texto de un límite de integración (por ejemplo E -> e, pi/2 -> π/2)."""
    return _txt(sp.sympify(v))


def resolver(item):
    """Devuelve exacto, decimal, verificación (SciPy) y diferencia."""
    f, a, b = item["f"], item["a"], item["b"]
    F0 = sp.integrate(f, x)
    F1 = sp.simplify(F0)
    F = F1 if sp.count_ops(F1) < sp.count_ops(F0) else F0
    exacto = sp.simplify(sp.integrate(f, (x, a, b)))
    if exacto.has(sp.Integral):
        raise ValueError("SymPy no pudo calcular el valor exacto de esta integral.")
    if F.has(sp.Integral):
        # hay valor exacto pero no una antiderivada simple (por ejemplo |x|)
        F_txt, Fb_txt, Fa_txt, tfc_ok = "no disponible", "—", "—", None
    else:
        # Teorema Fundamental del Cálculo hecho por el programa: F(b) - F(a)
        Fb = sp.simplify(F.subs(x, b))
        Fa = sp.simplify(F.subs(x, a))
        F_txt, Fb_txt, Fa_txt = _txt(F), _txt(Fb), _txt(Fa)
        tfc_ok = bool(sp.simplify(Fb - Fa - exacto) == 0)
    decimal = sp.N(exacto, 12)
    fn = sp.lambdify(x, f, "numpy")
    af, bf = float(sp.N(a)), float(sp.N(b))
    num, err = sci.quad(fn, af, bf)
    return {
        "exacto": exacto,
        "exacto_txt": _txt(exacto),
        "F_txt": F_txt,
        "Fb_txt": Fb_txt,
        "Fa_txt": Fa_txt,
        "tfc_ok": tfc_ok,
        "exacto_latex": sp.latex(exacto),
        "decimal": float(decimal),
        "scipy": num,
        "error_scipy": err,
        "diferencia": abs(float(decimal) - num),
    }


def puntos_grafica(item, n=600):
    af, bf = float(sp.N(item["a"])), float(sp.N(item["b"]))
    margen = (bf - af) * 0.25
    fn = sp.lambdify(x, item["f"], "numpy")
    xs = np.linspace(af - margen, bf + margen, n)
    xi = np.linspace(af, bf, n)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(np.asarray(fn(xs), dtype=float), xs.shape)
        yi = np.broadcast_to(np.asarray(fn(xi), dtype=float), xi.shape)
    return xs, ys, xi, yi, af, bf


# ---------------------------------------------------------------------------
# Integral escrita por el usuario (por ejemplo, la que ponga el profesor)
# ---------------------------------------------------------------------------
_LOCAL = {"x": x, "e": sp.E, "pi": sp.pi, "ln": sp.log, "log": sp.log,
          "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "tg": sp.tan,
          "sec": sp.sec, "csc": sp.csc, "cot": sp.cot, "sqrt": sp.sqrt,
          "exp": sp.exp, "Abs": sp.Abs, "asin": sp.asin, "acos": sp.acos,
          "atan": sp.atan, "arcsen": sp.asin, "arccos": sp.acos,
          "arctan": sp.atan}
_TRANSF = standard_transformations + (implicit_multiplication_application,)
_SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")


def _limpiar(s):
    """Convierte lo que se escribe (con símbolos como √ π ² ÷) a sintaxis de SymPy."""
    s = s.strip()
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+",
               lambda m: "**(" + m.group().translate(_SUP) + ")", s)
    for a, b in (("−", "-"), ("–", "-"), ("×", "*"), ("·", "*"), ("÷", "/"),
                 ("π", "pi"), ("^", "**")):
        s = s.replace(a, b)
    s = re.sub(r"√\s*([A-Za-z0-9.]+)", r"sqrt(\1)", s)
    s = s.replace("√", "sqrt")
    s = re.sub(r"\|([^|]+)\|", r"Abs(\1)", s)
    s = re.sub(r"\bsen\b", "sin", s)
    s = re.sub(r"(?<=\d),(?=\d)", ".", s)
    s = re.sub(r"\s*\bdx\s*$", "", s)
    return s


def _parsear(texto, nombre):
    if not texto.strip():
        raise ValueError(f"Escribe {nombre}.")
    try:
        return parse_expr(_limpiar(texto), local_dict=_LOCAL,
                          transformations=_TRANSF)
    except Exception:
        raise ValueError(f"No pude entender {nombre}. Revisa los paréntesis "
                         "y los símbolos.")


def latex_integral(f, a, b):
    """LaTeX de la integral para mostrarla en notación matemática."""
    cuerpo = sp.latex(f)
    cuerpo = re.sub(r"\\sin(?![a-z])", r"\\mathrm{sen}", cuerpo)
    return (r"\int_{" + sp.latex(a) + "}^{" + sp.latex(b) + "} "
            + cuerpo + r"\,dx")


def construir_integral_libre(txt_f, txt_a, txt_b):
    """Valida lo escrito y devuelve un item igual a los de INTEGRALES."""
    f = _parsear(txt_f, "la función a integrar")
    a = _parsear(txt_a, "el límite inferior")
    b = _parsear(txt_b, "el límite superior")
    if not isinstance(f, sp.Expr) or (f.free_symbols - {x}):
        raise ValueError("La función solo puede tener la variable x.")
    for lim, nom in ((a, "inferior"), (b, "superior")):
        if lim.free_symbols or not lim.is_real:
            raise ValueError(f"El límite {nom} debe ser un número "
                             "(puede ser como π/2 o e).")
    if not a < b:
        raise ValueError("El límite inferior debe ser menor que el superior.")
    # puntos donde la función no está definida dentro del intervalo
    try:
        sing = sp.singularities(f, x)
        dentro = sp.Intersection(sing, sp.Interval(a, b))
        if dentro != sp.S.EmptySet:
            raise ValueError("La función no está definida en todo el intervalo "
                             "(es una integral impropia), así que esta app no "
                             "la resuelve.")
    except ValueError:
        raise
    except Exception:
        pass
    fn = sp.lambdify(x, f, "numpy")
    with np.errstate(all="ignore"):
        ys = np.asarray(fn(np.linspace(float(a), float(b), 2001)), dtype=complex)
    if not np.all(np.isfinite(ys)) or np.any(np.abs(ys.imag) > 1e-12):
        raise ValueError("La función no está definida con valores reales en "
                         "todo el intervalo.")
    return {
        "n": "propia", "f": f, "a": a, "b": b,
        "latex": latex_integral(f, a, b),
        "tecnica": "Integral propia (Teorema Fundamental del Cálculo; "
                   "SymPy halla la antiderivada)",
        "pasos": [
            f"Función a integrar: f(x) = {_txt(f)}.",
            "Buscamos una antiderivada F(x) y aplicamos el Teorema "
            "Fundamental del Cálculo: ∫ f(x)dx desde a hasta b = F(b) − F(a).",
            "Los valores de F(x), F(a) y F(b) los calcula SymPy y aparecen "
            "en la comprobación de abajo.",
        ],
    }
