"""Aplicación del TCC de Cálculo Integral — Ingeniería de Software.

Resuelve las 10 integrales definidas asignadas y también una integral escrita
por el usuario. Muestra: notación matemática, técnica, procedimiento paso a
paso, resultado exacto, aproximación decimal, gráfica del área y verificación
con SciPy.
"""
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from integrales import (INTEGRALES, resolver, puntos_grafica, txt_lim,
                        construir_integral_libre, latex_integral, _parsear)

INTEGRANTES = (
    "Jonatan Jose Gomez Herrera · Luis Santiago Morelo Espitia · Ivan Andrés Cogollo López · Dhylan Jose Petro Ramos · Carlos Arturo Flórez Dugarte")

AZUL = "#1f3a6e"
CLARO = "#eaf1fb"

# (texto del botón, lo que inserta, cuántos caracteres retroceder el cursor)
SIMBOLOS = [
    ("x", "x", 0), ("x²", "^2", 0), ("xⁿ", "^", 0), ("√", "sqrt()", 1),
    ("π", "pi", 0), ("e", "e", 0), ("eˣ", "e^", 0), ("ln", "ln()", 1),
    ("sen", "sen()", 1), ("cos", "cos()", 1), ("tan", "tan()", 1),
    ("sec", "sec()", 1), ("|x|", "abs()", 1), ("( )", "()", 1),
    ("+", "+", 0), ("−", "-", 0), ("×", "*", 0), ("÷", "/", 0),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TCC Cálculo Integral — Resolutor de integrales definidas")
        self.geometry("1200x760")
        self.minsize(1000, 680)
        self.configure(bg=CLARO)
        self.actual = None
        self.resultado = None
        self.destino = None          # caja de texto donde escriben los símbolos
        self._hilo = {}
        self._construir()
        self.combo.current(0)
        self.resolver_seleccion()

    # ---------- interfaz ----------
    def _construir(self):
        top = tk.Frame(self, bg=AZUL)
        top.pack(fill="x")
        tk.Label(top, text="Resolutor de Integrales Definidas",
                 bg=AZUL, fg="white", font=("Segoe UI", 16, "bold")
                 ).pack(side="left", padx=14, pady=10)
        tk.Label(top, text="Universidad de Cartagena · Ingeniería de Software",
                 bg=AZUL, fg="#cfe0ff", font=("Segoe UI", 10)
                 ).pack(side="right", padx=14)

        sel = tk.Frame(self, bg=CLARO)
        sel.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(sel, text="Selecciona la integral:", bg=CLARO,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        valores = [f"Integral {i['n']}  —  {i['tecnica'].split('(')[0].strip()}"
                   for i in INTEGRALES]
        self.combo = ttk.Combobox(sel, values=valores, state="readonly", width=60)
        self.combo.pack(side="left", padx=10)
        self.combo.bind("<<ComboboxSelected>>", lambda _e: self.resolver_seleccion())
        ttk.Button(sel, text="Guardar gráfica (PNG)", command=self.guardar_png
                   ).pack(side="left", padx=4)
        ttk.Button(sel, text="Guardar procedimiento (TXT)", command=self.guardar_txt
                   ).pack(side="left", padx=4)

        self._construir_propia()

        pie = tk.Label(self, text="Integrantes: " + INTEGRANTES, bg=CLARO,
                       fg="#444444", font=("Segoe UI", 9))
        pie.pack(side="bottom", fill="x", pady=(0, 4))

        cuerpo = tk.Frame(self, bg=CLARO)
        cuerpo.pack(fill="both", expand=True, padx=14, pady=8)
        cuerpo.columnconfigure(0, weight=1, uniform="a")
        cuerpo.columnconfigure(1, weight=1, uniform="a")
        cuerpo.rowconfigure(0, weight=1)

        izq = tk.Frame(cuerpo, bg="white", bd=1, relief="solid")
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        der = tk.Frame(cuerpo, bg="white", bd=1, relief="solid")
        der.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        # notación matemática
        self.fig_nota = Figure(figsize=(5, 0.9), dpi=100)
        self.cv_nota = FigureCanvasTkAgg(self.fig_nota, master=izq)
        self.cv_nota.get_tk_widget().pack(fill="x")

        self.lbl_tecnica = tk.Label(izq, text="", bg="white", fg=AZUL,
                                    font=("Segoe UI", 10, "bold"),
                                    wraplength=520, justify="left")
        self.lbl_tecnica.pack(fill="x", padx=10)

        tk.Label(izq, text="Procedimiento paso a paso", bg="white",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        marco = tk.Frame(izq, bg="white")
        marco.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        self.txt = tk.Text(marco, wrap="word", font=("Consolas", 11), height=10,
                           bg="#fbfcfe", relief="flat")
        barra = ttk.Scrollbar(marco, command=self.txt.yview)
        barra.pack(side="right", fill="y")
        self.txt.pack(side="left", fill="both", expand=True)
        self.txt.configure(state="disabled", yscrollcommand=barra.set)

        res = tk.Frame(izq, bg="#f0f6ff", bd=1, relief="solid")
        res.pack(fill="x", padx=10, pady=(0, 10))
        self.lbl_exacto = tk.Label(res, bg="#f0f6ff", anchor="w",
                                   font=("Segoe UI", 11, "bold"))
        self.lbl_exacto.pack(fill="x", padx=8, pady=(6, 0))
        self.lbl_dec = tk.Label(res, bg="#f0f6ff", anchor="w", font=("Segoe UI", 11))
        self.lbl_dec.pack(fill="x", padx=8)
        self.lbl_ver = tk.Label(res, bg="#f0f6ff", anchor="w", fg="#1b6e2e",
                                font=("Segoe UI", 10))
        self.lbl_ver.pack(fill="x", padx=8, pady=(0, 6))

        # gráfica
        self.fig = Figure(figsize=(5.4, 4.6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.cv = FigureCanvasTkAgg(self.fig, master=der)
        self.cv.get_tk_widget().pack(fill="both", expand=True)

    def _construir_propia(self):
        """Zona para escribir una integral propia, con teclado de símbolos."""
        caja = tk.LabelFrame(self, text=" Integral propia (escríbela aquí) ",
                             bg=CLARO, fg=AZUL, font=("Segoe UI", 10, "bold"))
        caja.pack(fill="x", padx=14, pady=(4, 0))

        # vista previa en notación matemática de lo que se va escribiendo
        self.fig_prev = Figure(figsize=(3.4, 0.95), dpi=100)
        self.cv_prev = FigureCanvasTkAgg(self.fig_prev, master=caja)
        self.cv_prev.get_tk_widget().pack(side="right", padx=6, pady=2)

        izq = tk.Frame(caja, bg=CLARO)
        izq.pack(side="left", fill="x", expand=True, padx=6, pady=4)

        fila = tk.Frame(izq, bg=CLARO)
        fila.pack(fill="x")
        tk.Label(fila, text="f(x) =", bg=CLARO, font=("Segoe UI", 10, "bold")
                 ).pack(side="left")
        self.e_f = ttk.Entry(fila, width=26, font=("Consolas", 12))
        self.e_f.pack(side="left", padx=(4, 12))
        tk.Label(fila, text="desde", bg=CLARO, font=("Segoe UI", 10, "bold")
                 ).pack(side="left")
        self.e_a = ttk.Entry(fila, width=7, font=("Consolas", 12))
        self.e_a.pack(side="left", padx=(4, 8))
        tk.Label(fila, text="hasta", bg=CLARO, font=("Segoe UI", 10, "bold")
                 ).pack(side="left")
        self.e_b = ttk.Entry(fila, width=7, font=("Consolas", 12))
        self.e_b.pack(side="left", padx=(4, 10))
        self.btn_propia = ttk.Button(fila, text="Resolver mi integral",
                                     command=self.resolver_propia)
        self.btn_propia.pack(side="left")

        for caja_txt in (self.e_f, self.e_a, self.e_b):
            caja_txt.bind("<FocusIn>", lambda ev: setattr(self, "destino", ev.widget))
            caja_txt.bind("<KeyRelease>", lambda _e: self.vista_previa())
            caja_txt.bind("<Return>", lambda _e: self.resolver_propia())
        self.destino = self.e_f

        teclas = tk.Frame(izq, bg=CLARO)
        teclas.pack(fill="x", pady=(4, 0))
        for k, (texto, ins, atras) in enumerate(SIMBOLOS):
            tk.Button(teclas, text=texto, width=4, font=("Segoe UI", 10),
                      relief="groove", bg="white",
                      command=lambda t=ins, n=atras: self.insertar(t, n)
                      ).grid(row=k // 10, column=k % 10, padx=1, pady=1)
        tk.Button(teclas, text="⌫", width=4, font=("Segoe UI", 10), relief="groove",
                  bg="#fde8e8", command=self.borrar_uno).grid(row=1, column=8, padx=1)
        tk.Button(teclas, text="Limpiar", font=("Segoe UI", 9), relief="groove",
                  bg="#fde8e8", command=self.limpiar_cajas
                  ).grid(row=1, column=9, padx=1)

        self.vista_previa()

    # ---------- teclado de símbolos ----------
    def insertar(self, texto, atras=0):
        caja = self.destino or self.e_f
        pos = caja.index(tk.INSERT)
        caja.insert(pos, texto)
        caja.icursor(pos + len(texto) - atras)
        caja.focus_set()
        self.vista_previa()

    def borrar_uno(self):
        caja = self.destino or self.e_f
        pos = caja.index(tk.INSERT)
        if pos > 0:
            caja.delete(pos - 1)
        caja.focus_set()
        self.vista_previa()

    def limpiar_cajas(self):
        for c in (self.e_f, self.e_a, self.e_b):
            c.delete(0, "end")
        self.e_f.focus_set()
        self.vista_previa()

    def vista_previa(self):
        """Dibuja la integral tal como la entiende el programa."""
        self.fig_prev.clear()
        try:
            f = _parsear(self.e_f.get(), "f")
            a = _parsear(self.e_a.get() or "0", "a")
            b = _parsear(self.e_b.get() or "1", "b")
            self.fig_prev.text(0.5, 0.5, f"${latex_integral(f, a, b)}$",
                               fontsize=15, ha="center", va="center")
            self.cv_prev.draw()
        except Exception:
            self.fig_prev.clear()
            self.fig_prev.text(0.5, 0.5, "vista previa…", fontsize=10,
                               color="gray", ha="center", va="center")
            self.cv_prev.draw()

    # ---------- lógica ----------
    def resolver_seleccion(self):
        item = INTEGRALES[self.combo.current()]
        try:
            r = resolver(item)
        except Exception as err:
            messagebox.showerror("Error", str(err))
            return
        self.mostrar(item, r)

    def resolver_propia(self):
        try:
            item = construir_integral_libre(self.e_f.get(), self.e_a.get(),
                                            self.e_b.get())
        except ValueError as err:
            messagebox.showwarning("Revisa la integral", str(err))
            return
        self.btn_propia.state(["disabled"])
        self.lbl_ver.config(text="Calculando…", fg="#555555")
        self._hilo = {}

        def tarea():
            try:
                self._hilo["r"] = resolver(item)
            except Exception as err:          # se muestra en la ventana
                self._hilo["err"] = err

        threading.Thread(target=tarea, daemon=True).start()
        self.after(150, lambda: self._esperar(item))

    def _esperar(self, item):
        if "r" in self._hilo:
            self.btn_propia.state(["!disabled"])
            self.mostrar(item, self._hilo["r"])
        elif "err" in self._hilo:
            self.btn_propia.state(["!disabled"])
            self.lbl_ver.config(text="")
            err = self._hilo["err"]
            msg = str(err) if isinstance(err, ValueError) else \
                f"No pude resolver esa integral. Detalle: {err}"
            messagebox.showwarning("No se pudo resolver", msg)
        else:
            self.after(150, lambda: self._esperar(item))

    def mostrar(self, item, r):
        self.actual = item
        self.resultado = r

        self.fig_nota.clear()
        try:
            self.fig_nota.text(0.5, 0.5, f"${item['latex']}$", fontsize=22,
                               ha="center", va="center")
            self.cv_nota.draw()
        except Exception:
            self.fig_nota.clear()
            self.fig_nota.text(0.5, 0.5, "∫ f(x) dx", fontsize=18,
                               ha="center", va="center")
            self.cv_nota.draw()

        self.lbl_tecnica.config(text="Técnica: " + item["tecnica"])

        lineas = [f"Paso {k}. {p}" for k, p in enumerate(item["pasos"], 1)]
        a_txt, b_txt = txt_lim(item["a"]), txt_lim(item["b"])
        if r["tfc_ok"] is None:
            lineas.append(
                "Comprobación simbólica (SymPy):\n"
                "   SymPy calculó el valor exacto directamente, porque esta "
                "función no tiene una antiderivada simple.\n"
                f"   Valor = {r['exacto_txt']}")
        else:
            lineas.append(
                "Comprobación simbólica (SymPy, Teorema Fundamental del Cálculo):\n"
                f"   F(x) = {r['F_txt']}\n"
                f"   F({b_txt}) = {r['Fb_txt']}\n"
                f"   F({a_txt}) = {r['Fa_txt']}\n"
                f"   F(b) − F(a) = {r['exacto_txt']}"
                + ("   ✔" if r["tfc_ok"] else "   ✘"))
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", "\n\n".join(lineas))
        self.txt.configure(state="disabled")

        self.lbl_exacto.config(text=f"Resultado exacto:  {r['exacto_txt']}")
        self.lbl_dec.config(text=f"Aproximación decimal:  {r['decimal']:.8f}")
        ok = r["diferencia"] < 1e-8
        self.lbl_ver.config(
            text=("✔ Verificado con SciPy (quad): "
                  f"{r['scipy']:.8f}  |  diferencia = {r['diferencia']:.2e}")
            if ok else f"✘ Diferencia con SciPy: {r['diferencia']:.2e}",
            fg="#1b6e2e" if ok else "#b00020")
        self.graficar(item)

    def graficar(self, item):
        xs, ys, xi, yi, a, b = puntos_grafica(item)
        self.ax.clear()
        self.ax.axhline(0, color="black", lw=0.8)
        self.ax.plot(xs, ys, color=AZUL, lw=2, label="f(x)")
        self.ax.fill_between(xi, yi, 0, where=(yi >= 0), color="#3b82f6",
                             alpha=0.35, label="área positiva")
        self.ax.fill_between(xi, yi, 0, where=(yi < 0), color="#ef4444",
                             alpha=0.35, label="área negativa")
        self.ax.axvline(a, color="gray", ls="--", lw=0.8)
        self.ax.axvline(b, color="gray", ls="--", lw=0.8)
        self.ax.set_title(f"Integral {item['n']}: área bajo la curva en [{a:.3g}, {b:.3g}]"
                          f"\nvalor = {self.resultado['decimal']:.6f}", fontsize=10)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.grid(alpha=0.3)
        self.ax.legend(loc="best", fontsize=8)
        self.fig.tight_layout()
        self.cv.draw()

    def guardar_png(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png", initialfile=f"integral_{self.actual['n']}.png",
            filetypes=[("PNG", "*.png")])
        if ruta:
            self.fig.savefig(ruta, dpi=150)
            messagebox.showinfo("Guardado", f"Gráfica guardada en:\n{ruta}")

    def guardar_txt(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=f"integral_{self.actual['n']}.txt",
            filetypes=[("Texto", "*.txt")])
        if not ruta:
            return
        r, it = self.resultado, self.actual
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(f"Integral {it['n']}: {it['tecnica']}\n\n")
            for k, p in enumerate(it["pasos"], 1):
                fh.write(f"Paso {k}. {p}\n")
            fh.write(f"\nResultado exacto: {r['exacto_txt']}\n")
            fh.write(f"Aproximación decimal: {r['decimal']:.8f}\n")
            fh.write(f"Verificación SciPy: {r['scipy']:.8f}\n")
        messagebox.showinfo("Guardado", f"Procedimiento guardado en:\n{ruta}")


if __name__ == "__main__":
    App().mainloop()
