import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- LÓGICA PRINCIPAL ---

class RiemannSumApp:
    def __init__(self, master):
        """
        Constructor de la aplicación. Inicializa la GUI.
        """
        self.master = master
        self.master.title("Calculadora de Sumas de Riemann")
        self.master.geometry("800x750")

        # --- Estilo ---
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TRadiobutton", padding=5, font=('Helvetica', 10))

        # --- Marco para los Controles (Inputs) ---
        controls_frame = ttk.Frame(master, padding="10 10 10 10")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # --- Entradas de Datos ---
        ttk.Label(controls_frame, text="Función f(x):").grid(row=0, column=0, sticky=tk.W)
        self.func_entry = ttk.Entry(controls_frame, width=40)
        self.func_entry.insert(0, "x**2") # Ejemplo inicial
        self.func_entry.grid(row=0, column=1, columnspan=3, sticky=tk.EW)

        ttk.Label(controls_frame, text="Intervalo [a, b]:").grid(row=1, column=0, sticky=tk.W)
        self.a_entry = ttk.Entry(controls_frame, width=10)
        self.a_entry.insert(0, "0")
        self.a_entry.grid(row=1, column=1, sticky=tk.W)
        
        self.b_entry = ttk.Entry(controls_frame, width=10)
        self.b_entry.insert(0, "10")
        self.b_entry.grid(row=1, column=2, sticky=tk.W)

        ttk.Label(controls_frame, text="Nº de Rectángulos (n):").grid(row=2, column=0, sticky=tk.W)
        self.n_entry = ttk.Entry(controls_frame, width=10)
        self.n_entry.insert(0, "20")
        self.n_entry.grid(row=2, column=1, sticky=tk.W)
        
        # --- Selección del Tipo de Suma ---
        self.sum_type = tk.StringVar(value="midpoint") # Valor por defecto
        
        ttk.Label(controls_frame, text="Método:").grid(row=3, column=0, sticky=tk.W)
        ttk.Radiobutton(controls_frame, text="Izquierda", variable=self.sum_type, value="left").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(controls_frame, text="Derecha", variable=self.sum_type, value="right").grid(row=3, column=2, sticky=tk.W)
        ttk.Radiobutton(controls_frame, text="Punto Medio", variable=self.sum_type, value="midpoint").grid(row=3, column=3, sticky=tk.W)
        ttk.Radiobutton(controls_frame, text="Trapecio", variable=self.sum_type, value="trapezoid").grid(row=3, column=4, sticky=tk.W)
        
        # --- Botón de Cálculo ---
        self.calc_button = ttk.Button(master, text="Calcular y Dibujar", command=self.calculate_and_draw)
        self.calc_button.pack(pady=10)

        # --- Etiqueta para el Resultado ---
        self.result_label = ttk.Label(master, text="Resultado: ", font=('Helvetica', 12, 'bold'))
        self.result_label.pack(pady=5)

        # --- Lienzo para la Gráfica de Matplotlib ---
        self.fig = plt.Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Añadimos una nota sobre la sintaxis de la función ---
        info_label = ttk.Label(master, text="Use sintaxis de Python para la función. Ej: x**3 + 2*x, sin(x), exp(x). Use np. para funciones de numpy.",
                               font=('Helvetica', 9, 'italic'), justify=tk.CENTER)
        info_label.pack(pady=(0, 10))


    def calculate_and_draw(self):
        """
        Función principal que se ejecuta al pulsar el botón.
        Valida entradas, calcula la suma y actualiza la gráfica.
        """
        try:
            # 1. Obtener y validar los datos de entrada
            func_str = self.func_entry.get()
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            n = int(self.n_entry.get())

            if n <= 0:
                messagebox.showerror("Error", "El número de rectángulos (n) debe ser un entero positivo.")
                return
            if a >= b:
                messagebox.showerror("Error", "El inicio del intervalo (a) debe ser menor que el final (b).")
                return

            # 2. Crear una función Python a partir del string de forma segura
            # Permitimos el uso de funciones de numpy y constantes
            safe_dict = {
                'np': np,
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
                'exp': np.exp, 'log': np.log, 'log10': np.log10, 'sqrt': np.sqrt,
                'pi': np.pi, 'e': np.e
            }
            
            # Usamos una función lambda para evaluar la expresión
            # La variable 'x' se pasará en el momento de la evaluación
            f = lambda x: eval(func_str, safe_dict, {'x': x})

            # Probar la función con un valor para detectar errores de sintaxis
            f(a) 

        except (ValueError, TypeError):
            messagebox.showerror("Error de Entrada", "Por favor, introduce valores numéricos válidos para 'a', 'b' y 'n'.")
            return
        except Exception as e:
            messagebox.showerror("Error en la Función", f"La función f(x) no es válida.\nError: {e}\nAsegúrate de usar la sintaxis correcta (ej: 'x**2' en lugar de 'x^2').")
            return

        # 3. Realizar el cálculo de la suma de Riemann
        delta_x = (b - a) / n
        x_points = np.linspace(a, b, n + 1)
        riemann_sum = 0
        
        # Puntos para dibujar los rectángulos/trapecios
        if self.sum_type.get() == "left":
            bar_x = x_points[:-1]
            bar_height = f(bar_x)
            riemann_sum = np.sum(bar_height * delta_x)
            align = 'edge'
        elif self.sum_type.get() == "right":
            bar_x = x_points[1:]
            bar_height = f(bar_x)
            riemann_sum = np.sum(bar_height * delta_x)
            align = 'edge'
        elif self.sum_type.get() == "midpoint":
            mid_points = (x_points[:-1] + x_points[1:]) / 2
            bar_x = mid_points
            bar_height = f(bar_x)
            riemann_sum = np.sum(bar_height * delta_x)
            align = 'center'
        elif self.sum_type.get() == "trapezoid":
            # Para la visualización, dibujaremos rectángulos, pero el cálculo es de trapecio
            y_points = f(x_points)
            riemann_sum = np.sum((y_points[:-1] + y_points[1:]) / 2 * delta_x)
            # Para la visualización, usaremos la altura media
            bar_x = x_points[:-1]
            bar_height = (y_points[:-1] + y_points[1:]) / 2
            align = 'edge'

        # 4. Actualizar la etiqueta del resultado
        self.result_label.config(text=f"Resultado Aproximado: {riemann_sum:.8f}")

        # 5. Dibujar la gráfica
        self.ax.clear()
        
        # Curva de la función original
        x_curve = np.linspace(a, b, 1000)
        y_curve = f(x_curve)
        self.ax.plot(x_curve, y_curve, 'b-', label=f"f(x) = {func_str}", linewidth=2)

        # Rectángulos o Trapecios
        if self.sum_type.get() == "trapezoid":
             # Dibujar los trapecios explícitamente
            for i in range(n):
                xs = [x_points[i], x_points[i], x_points[i+1], x_points[i+1]]
                ys = [0, y_points[i], y_points[i+1], 0]
                self.ax.fill(xs, ys, 'g', edgecolor='black', alpha=0.5)
        else:
             # Dibujar rectángulos para izquierda, derecha y punto medio
            self.ax.bar(bar_x, bar_height, width=delta_x, align=align, alpha=0.5, edgecolor='black', color='green')

        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.set_title(f"Suma de Riemann ({self.sum_type.get().capitalize()}) con n={n}")
        self.ax.legend()
        self.ax.grid(True)
        self.ax.axhline(0, color='black', linewidth=0.5) # Eje x
        
        # Actualizar el lienzo
        self.canvas.draw()


# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    root = tk.Tk()
    app = RiemannSumApp(root)
    root.mainloop()