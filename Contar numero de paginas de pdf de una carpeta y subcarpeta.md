
### Promp:

haz un script en python que recorrar directorios y subdirectorios y diga de los ficheros pdf que encuentre el numero de páginas que tengan
añadele interfaz gráfica para que se pueda seleccionar la carpeta y mostrar resultados
debe de haber un boton para que el resultado del escaneo se copie al portapapeles

### Captura de Pantalla:

| pantallazo inicial                   | resultado                                                                                |
| ------------------------------------ | ---------------------------------------------------------------------------------------- |
| ![[./ANEXOS/Pasted image 20251218081805.png]] | Copiado al portapapeles y pegado en una hoja excel: ![[./ANEXOS/Pasted image 20251218082056.png]] |
|                                      |                                                                                          |

### Código:
``` python
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pypdf import PdfReader

class PDFCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contador de Páginas PDF")
        self.root.geometry("900x650")

        # Variables
        self.directorio_seleccionado = tk.StringVar()
        self.total_pdfs = 0
        self.total_paginas = 0
        self.escaneo_activo = False

        # --- SECCIÓN SUPERIOR: Selección de carpeta ---
        frame_top = tk.Frame(root, pady=10, padx=10)
        frame_top.pack(fill="x")

        tk.Label(frame_top, text="Directorio:").pack(side="left")
        
        self.entry_ruta = tk.Entry(frame_top, textvariable=self.directorio_seleccionado, width=50)
        self.entry_ruta.pack(side="left", padx=5, fill="x", expand=True)

        self.btn_seleccionar = tk.Button(frame_top, text="📂 Seleccionar", command=self.seleccionar_carpeta)
        self.btn_seleccionar.pack(side="left", padx=5)

        self.btn_iniciar = tk.Button(frame_top, text="▶ INICIAR ESCANEO", command=self.iniciar_thread, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.btn_iniciar.pack(side="left", padx=5)

        # --- SECCIÓN CENTRAL: Tabla de resultados ---
        frame_tabla = tk.Frame(root, padx=10, pady=5)
        frame_tabla.pack(fill="both", expand=True)

        columns = ("archivo", "paginas", "ruta")
        self.tree = ttk.Treeview(frame_tabla, columns=columns, show="headings")
        
        self.tree.heading("archivo", text="Nombre del Archivo")
        self.tree.heading("paginas", text="Páginas")
        self.tree.heading("ruta", text="Ruta Completa")

        self.tree.column("archivo", width=250)
        self.tree.column("paginas", width=80, anchor="center")
        self.tree.column("ruta", width=450)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- SECCIÓN INFERIOR: Botones y Totales ---
        frame_bottom = tk.Frame(root, pady=10, padx=10, bg="#f0f0f0")
        frame_bottom.pack(fill="x")

        # Botón de Copiar al Portapapeles (NUEVO)
        self.btn_copiar = tk.Button(frame_bottom, text="📋 Copiar Tabla al Portapapeles", command=self.copiar_al_portapapeles)
        self.btn_copiar.pack(side="left")

        # Etiquetas de estado
        self.lbl_estado = tk.Label(frame_bottom, text="Listo.", bg="#f0f0f0", anchor="w", padx=10)
        self.lbl_estado.pack(side="left", fill="x", expand=True)

        self.lbl_totales = tk.Label(frame_bottom, text="PDFs: 0 | Páginas: 0", font=("Arial", 11, "bold"), bg="#f0f0f0")
        self.lbl_totales.pack(side="right")

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.directorio_seleccionado.set(ruta)

    def iniciar_thread(self):
        ruta = self.directorio_seleccionado.get()
        if not ruta or not os.path.exists(ruta):
            messagebox.showerror("Error", "Por favor selecciona un directorio válido.")
            return

        if self.escaneo_activo:
            return

        # Limpieza inicial
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.total_pdfs = 0
        self.total_paginas = 0
        self.lbl_totales.config(text="PDFs: 0 | Páginas: 0")
        
        self.btn_iniciar.config(state="disabled", text="Escaneando...")
        self.escaneo_activo = True

        threading.Thread(target=self.procesar_directorio, args=(ruta,), daemon=True).start()

    def procesar_directorio(self, directorio):
        for raiz, dirs, archivos in os.walk(directorio):
            for archivo in archivos:
                if archivo.lower().endswith('.pdf'):
                    ruta_completa = os.path.join(raiz, archivo)
                    
                    try:
                        self.lbl_estado.config(text=f"Leyendo: {archivo}...")
                        
                        reader = PdfReader(ruta_completa)
                        num_paginas = len(reader.pages)
                        
                        self.tree.insert("", "end", values=(archivo, num_paginas, raiz))
                        
                        self.total_pdfs += 1
                        self.total_paginas += num_paginas
                        
                        if self.total_pdfs % 5 == 0:
                             self.lbl_totales.config(text=f"PDFs: {self.total_pdfs} | Páginas: {self.total_paginas}")

                    except Exception as e:
                        print(f"Error en {archivo}: {e}")
                        self.tree.insert("", "end", values=(archivo, "ERROR", raiz))

        self.lbl_estado.config(text="Escaneo Finalizado.")
        self.lbl_totales.config(text=f"PDFs: {self.total_pdfs} | Páginas: {self.total_paginas}")
        self.btn_iniciar.config(state="normal", text="▶ INICIAR ESCANEO")
        self.escaneo_activo = False

    def copiar_al_portapapeles(self):
        """Copia el contenido del Treeview al portapapeles en formato compatible con Excel"""
        if not self.tree.get_children():
            messagebox.showinfo("Información", "No hay datos para copiar.")
            return

        # Crear cabecera
        texto_copiado = "Nombre Archivo\tPáginas\tRuta Completa\n"

        # Recorrer filas y formatear con tabuladores
        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']
            # Convertimos cada valor a string y unimos con tabulador (\t)
            linea = "\t".join([str(v) for v in valores])
            texto_copiado += linea + "\n"

        # Limpiar portapapeles y asignar nuevo texto
        self.root.clipboard_clear()
        self.root.clipboard_append(texto_copiado)
        self.root.update()  # Necesario para asegurar que se queda en el portapapeles

        messagebox.showinfo("Éxito", "¡Datos copiados! Puedes pegarlos en Excel (Ctrl+V).")

# --- Ejecución ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PDFCounterApp(root)
        root.mainloop()
    except ImportError:
        print("Error: Necesitas instalar la librería pypdf.")
        print("Ejecuta: pip install pypdf")
```




### Programa

![[./ANEXOS/MostrarPaginasPdf.py]]