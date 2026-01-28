<span style="background:#b1ffff">Promp:</span>
hazme un script en python para unir todos los ficheros pdf que hay en una carpeta y subcarpeta en un solo pdf. Tiene que ser interfaz visual que permita elegir la carpeta, y mostrar el logging,


**Nota:** Tras no encontrar la libreria y mostrar el error a gemini, me cambia el código para que en caso de que no este instalada la libreria la instale


<span style="background:#b1ffff">Pantallazo:</span>
![ANEXOS/Pastedimage20251218075114.png]  


Codigo fuente:

``` python
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import threading
from datetime import datetime

# --- BLOQUE DE AUTO-INSTALACIÓN ---
# Esto intenta instalar la librería automáticamente si tu Ejecutor no la tiene
try:
    from pypdf import PdfWriter
except ImportError:
    print("La librería 'pypdf' no fue encontrada. Intentando instalarla automáticamente...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        from pypdf import PdfWriter
        print("Instalación exitosa.")
    except Exception as e:
        # Si falla la instalación automática, mostramos un error visual
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror("Error de Librería", 
                             f"No se pudo instalar la librería 'pypdf' automáticamente.\n\n"
                             f"Error técnico: {e}\n\n"
                             f"Necesitas pedir al administrador de tu sistema que instale 'pypdf' "
                             f"en el entorno de Python que ejecuta T:\\Ejecutor.py")
        sys.exit(1)
# ----------------------------------

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fusionador de PDFs")
        self.root.geometry("600x500")
        
        # Variables
        self.source_folder = tk.StringVar()
        
        # --- UI Layout ---
        
        # Marco para selección de carpeta
        frame_top = tk.Frame(root, pady=10, padx=10)
        frame_top.pack(fill="x")
        
        tk.Label(frame_top, text="Carpeta Origen:").pack(side="left")
        self.entry_path = tk.Entry(frame_top, textvariable=self.source_folder, width=40)
        self.entry_path.pack(side="left", padx=5, fill="x", expand=True)
        
        btn_browse = tk.Button(frame_top, text="Seleccionar Carpeta", command=self.browse_folder)
        btn_browse.pack(side="left")
        
        # Botón de Acción
        self.btn_merge = tk.Button(root, text="UNIR TODOS LOS PDFs", command=self.start_merge_thread, 
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_merge.pack(fill="x", padx=20, pady=10)
        
        # Área de Logging
        tk.Label(root, text="Registro de actividad (Logs):").pack(anchor="w", padx=10)
        self.log_area = scrolledtext.ScrolledText(root, state='disabled', height=15)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo.")
        tk.Label(root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w").pack(side="bottom", fill="x")

    def log(self, message):
        """Agrega mensajes al área de texto con timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END) # Auto-scroll al final
        self.log_area.config(state='disabled')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_folder.set(folder_selected)
            self.log(f"Carpeta seleccionada: {folder_selected}")

    def start_merge_thread(self):
        """Inicia el proceso en un hilo separado para no congelar la UI."""
        folder = self.source_folder.get()
        if not folder:
            messagebox.showwarning("Atención", "Por favor selecciona una carpeta primero.")
            return
        
        # Deshabilitar botón para evitar doble clic
        self.btn_merge.config(state="disabled", text="Procesando...")
        
        # Iniciar hilo
        threading.Thread(target=self.process_pdfs, args=(folder,), daemon=True).start()

    def process_pdfs(self, folder_path):
        merger = PdfWriter()
        pdf_files_found = []

        self.log("--- Iniciando búsqueda de archivos ---")
        self.status_var.set("Buscando archivos PDF...")

        # 1. Buscar recursivamente
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    pdf_files_found.append(full_path)
        
        if not pdf_files_found:
            self.log("No se encontraron archivos PDF en la carpeta seleccionada.")
            self.finish_process(success=False)
            return

        # Ordenar alfabéticamente para tener consistencia
        pdf_files_found.sort()
        self.log(f"Se encontraron {len(pdf_files_found)} archivos PDF.")

        # 2. Unir archivos
        count = 0
        for pdf in pdf_files_found:
            try:
                self.status_var.set(f"Procesando: {os.path.basename(pdf)}")
                merger.append(pdf)
                self.log(f"Agregado: {os.path.basename(pdf)}")
                count += 1
            except Exception as e:
                self.log(f"ERROR al agregar {os.path.basename(pdf)}: {str(e)}")

        # 3. Guardar resultado
        if count > 0:
            output_filename = "PDF_Fusionado_Final.pdf"
            output_path = os.path.join(folder_path, output_filename)
            
            self.log("Guardando archivo final...")
            self.status_var.set("Guardando archivo...")
            
            try:
                merger.write(output_path)
                merger.close()
                self.log(f"--- ÉXITO: Archivo guardado en: {output_path} ---")
                messagebox.showinfo("Éxito", f"Se han unido {count} PDFs exitosamente.\nGuardado en: {output_path}")
            except Exception as e:
                self.log(f"ERROR CRÍTICO al guardar: {str(e)}")
        else:
            self.log("No se pudo procesar ningún archivo correctamente.")

        self.finish_process(success=True)

    def finish_process(self, success):
        """Restaura la UI al terminar."""
        self.btn_merge.config(state="normal", text="UNIR TODOS LOS PDFs")
        self.status_var.set("Listo.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()
```


Fichero:
![ANEXOS/FusionadorPdf.py]  