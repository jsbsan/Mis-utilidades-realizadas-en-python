import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import os

class ExcelToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertidor Excel a Markdown Pro v2.0")
        self.root.geometry("900x700")

        # --- Variables de Estado ---
        self.ruta_archivo_actual = None
        self.formato_var = tk.StringVar(value="csv") # Valor por defecto: csv

        # --- SECCIÓN SUPERIOR: Carga de Archivo ---
        frame_top = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0")
        frame_top.pack(fill=tk.X)

        self.btn_cargar = tk.Button(frame_top, text="📂 Seleccionar Excel (.xlsx)", command=self.cargar_archivo, bg="white", relief="groove")
        self.btn_cargar.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_archivo = tk.Label(frame_top, text="Ningún archivo seleccionado", fg="gray", bg="#f0f0f0")
        self.lbl_archivo.pack(side=tk.LEFT)

        # --- SECCIÓN MEDIA: Opciones de Formato ---
        frame_options = tk.Frame(root, padx=10, pady=5)
        frame_options.pack(fill=tk.X)

        lbl_opciones = tk.Label(frame_options, text="Formato de salida:", font=("Arial", 10, "bold"))
        lbl_opciones.pack(side=tk.LEFT, padx=(0, 10))

        # Radiobuttons para elegir el formato. 
        # Al cambiar (command=self.actualizar_vista), se regenera el texto si ya hay archivo cargado.
        rb_csv = tk.Radiobutton(frame_options, text="Código CSV (Datos crudos)", variable=self.formato_var, value="csv", command=self.actualizar_vista)
        rb_csv.pack(side=tk.LEFT, padx=10)

        rb_table = tk.Radiobutton(frame_options, text="Tabla Visual (| Col | Col |)", variable=self.formato_var, value="table", command=self.actualizar_vista)
        rb_table.pack(side=tk.LEFT, padx=10)

        # --- SECCIÓN CENTRAL: Vista Previa ---
        self.lbl_preview = tk.Label(root, text="Vista previa:", anchor="w", padx=10)
        self.lbl_preview.pack(fill=tk.X)

        # Área de texto con scroll
        self.txt_preview = scrolledtext.ScrolledText(root, width=90, height=25, font=("Consolas", 10))
        self.txt_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- SECCIÓN INFERIOR: Botones de Acción ---
        frame_bottom = tk.Frame(root, padx=10, pady=15)
        frame_bottom.pack(fill=tk.X)

        # Botón Limpiar (Izquierda) - NUEVO
        self.btn_limpiar = tk.Button(frame_bottom, text="🗑️ Limpiar Todo", command=self.limpiar_todo, bg="#FFCDD2", fg="#B71C1C", relief="groove", padx=10)
        self.btn_limpiar.pack(side=tk.LEFT)

        # Contenedor para botones derechos
        frame_right_buttons = tk.Frame(frame_bottom)
        frame_right_buttons.pack(side=tk.RIGHT)

        # Botón Copiar (Derecha) - NUEVO
        self.btn_copiar = tk.Button(frame_right_buttons, text="📋 Copiar al Portapapeles", command=self.copiar_portapapeles, state=tk.DISABLED, bg="#BBDEFB", fg="#0D47A1", padx=10)
        self.btn_copiar.pack(side=tk.LEFT, padx=(0, 10))

        # Botón Guardar (Derecha)
        self.btn_guardar = tk.Button(frame_right_buttons, text="💾 Guardar Markdown", command=self.guardar_archivo, state=tk.DISABLED, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=20)
        self.btn_guardar.pack(side=tk.LEFT)

    def cargar_archivo(self):
        """Abre el diálogo para seleccionar archivo"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )

        if archivo:
            self.ruta_archivo_actual = archivo
            self.lbl_archivo.config(text=os.path.basename(archivo), fg="black")
            self.actualizar_vista() # Procesar el archivo recién cargado

    def actualizar_vista(self):
        """Llama al procesador si hay un archivo cargado"""
        if self.ruta_archivo_actual:
            self.procesar_excel(self.ruta_archivo_actual)

    def procesar_excel(self, archivo_entrada):
        """Lee el Excel y genera el string según el formato seleccionado"""
        try:
            # Feedback visual de carga
            self.txt_preview.delete(1.0, tk.END)
            self.txt_preview.insert(tk.END, "Procesando... esto puede tardar unos segundos si el archivo es grande.\n")
            self.root.update()

            xls = pd.ExcelFile(archivo_entrada)
            resultado_final = []
            modo = self.formato_var.get() # 'csv' o 'table'

            for nombre_hoja in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=nombre_hoja)
                
                # --- NUEVA LÓGICA DE FORMATEO ROBUSTA ---
                # Definimos una función que revisa CADA celda individualmente
                def forzar_coma_decimal(val):
                    if pd.isnull(val):
                        return ""
                    
                    # Si es un número (int o float)
                    if isinstance(val, (int, float)):
                        return str(val).replace('.', ',')
                    
                    # Si es texto pero parece un número (ej: "123.45" guardado como texto)
                    if isinstance(val, str):
                        val_str = val.strip()
                        try:
                            # Intentamos ver si es un número válido
                            float(val_str)
                            # Si no falló lo anterior, y tiene punto, lo cambiamos
                            if '.' in val_str:
                                return val_str.replace('.', ',')
                        except ValueError:
                            # No es un número, devolvemos el texto original
                            pass
                    
                    return val

                # Aplicamos esta función a TODO el Excel
                # Esto convierte todo a strings con comas donde corresponda
                df_formateado = df.applymap(forzar_coma_decimal)

                # Título de la pestaña
                bloque = f"## Pestaña: {nombre_hoja}\n\n"
                
                if modo == "csv":
                    # Formato Bloque de Código CSV
                    bloque += "```csv\n"
                    # Usamos ; como separador estándar
                    # Nota: Como ya convertimos todo a string en df_formateado, decimal=',' es redundante pero seguro
                    bloque += df_formateado.to_csv(index=False, sep=";")
                    bloque += "```\n"
                else:
                    # Formato Tabla Markdown Visual
                    try:
                        # Convertimos a markdown
                        # Requiere pip install tabulate
                        tabla_md = df_formateado.to_markdown(index=False)
                        bloque += tabla_md + "\n"
                    except ImportError:
                        bloque += "ERROR: Falta la librería 'tabulate'. Instala con: pip install tabulate\n"
                    except Exception as e:
                        bloque += f"Error al generar tabla: {e}\n"

                bloque += "\n---\n\n"
                resultado_final.append(bloque)

            # Unir y mostrar
            contenido_completo = "".join(resultado_final)
            self.txt_preview.delete(1.0, tk.END)
            self.txt_preview.insert(tk.END, contenido_completo)
            
            # Habilitar botones de acción
            self.btn_guardar.config(state=tk.NORMAL)
            self.btn_copiar.config(state=tk.NORMAL)

        except Exception as e:
            self.txt_preview.delete(1.0, tk.END)
            self.lbl_archivo.config(text="Error", fg="red")
            messagebox.showerror("Error crítico", f"No se pudo leer el archivo:\n{e}")

    def copiar_portapapeles(self):
        """Copia el contenido actual al portapapeles del sistema"""
        texto = self.txt_preview.get("1.0", tk.END).strip()
        if texto:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            self.root.update() # Necesario para asegurar que el portapapeles se actualice
            messagebox.showinfo("Copiado", "El contenido se ha copiado al portapapeles exitosamente.")

    def limpiar_todo(self):
        """Reinicia la aplicación a su estado inicial"""
        self.txt_preview.delete("1.0", tk.END)
        self.ruta_archivo_actual = None
        self.lbl_archivo.config(text="Ningún archivo seleccionado", fg="gray")
        
        # Deshabilitar botones de acción
        self.btn_guardar.config(state=tk.DISABLED)
        self.btn_copiar.config(state=tk.DISABLED)

    def guardar_archivo(self):
        """Guarda el contenido actual del editor"""
        texto_a_guardar = self.txt_preview.get(1.0, tk.END).strip()
        
        if not texto_a_guardar:
            return

        archivo_salida = filedialog.asksaveasfilename(
            defaultextension=".md",
            title="Guardar archivo Markdown",
            filetypes=[("Markdown", "*.md"), ("Texto", "*.txt")]
        )

        if archivo_salida:
            try:
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    f.write(texto_a_guardar)
                messagebox.showinfo("Guardado", f"Archivo guardado exitosamente en:\n{archivo_salida}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

# --- Ejecución ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelToMarkdownApp(root)
    root.mainloop()