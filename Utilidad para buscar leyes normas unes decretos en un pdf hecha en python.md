#utilidades/programación 
#python 


Esta utilidad esta desarrollada en python con entorno grafico donde le sueltas un fichero pdf, y te devuelve un .txt con las leyes,normas, r.d. detectados indicando nº de página y parrafo donde se encuentra:

| captura pantalla                     | fichero .txt generado                     |  
| ------------------------------------ | ----------------------------------------- |  
| ![ANEXOS/Pasted%20image%2020250412100623.png]   | ![ANEXOS/Pasted%20image%2020250412100522.png\|500]   |  
Prompt usado: (a parte de modificar manualmente la linea del patron (linea 24) para añadir alguna palabra más)
1. haz un programa en python que lea un fichero pdf y que extraiga a un fichero de texto plano, los parrafos que tenga leyes, reales decretos, normas une, "R.D." y "UNE"
2. Quiero que tenga interfaz visual y que le pueda arrastra y soltar el fichero pdf
3. Quiero que tambien los párrafos que tengan las palabras "BOE", "B.O.E.", "O.M." y "OM ", los extraiga, por favor modifica el patrón de expresión regular del programa anterior
4. ¿me lo puedes dar completo el codigo?

**Extra para instalar:**
> pip install PyMuPDF
> pip install tkinterdnd2-universal

![ANEXOS/ExtraerLeyesRDv2.00.py]  

``` python
import tkinter as tk
from tkinter import ttk  # Para widgets más modernos
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD # Para Drag & Drop

import fitz  # PyMuPDF
import re
import os
import threading # Para que la GUI no se bloquee durante el proceso
import queue     # Para comunicar el hilo de trabajo con la GUI

# --- Lógica de extracción (ligeramente modificada para la GUI) ---
def extraer_parrafos_legales(pdf_path, txt_path, status_queue):
    """
    Lee un PDF, extrae párrafos con términos legales y los guarda en TXT.
    Actualiza el estado a través de una cola para la GUI.

    Args:
        pdf_path (str): Ruta al PDF de entrada.
        txt_path (str): Ruta al TXT de salida.
        status_queue (queue.Queue): Cola para enviar mensajes de estado a la GUI.
    """
    try:
        status_queue.put(f"Procesando: {os.path.basename(pdf_path)}...")
        patron = re.compile(
            r'\b(decreto|decretos|ley|leyes|real\s+decreto|reales\s+decretos|norma\s+une|normas\s+une|r\.d\.|une|boe|b\.o\.e\.|o\.m\.|om)\b',
            re.IGNORECASE
        )
        parrafos_encontrados = []
        documento = None

        if not os.path.exists(pdf_path):
            status_queue.put(f"Error: PDF no encontrado '{pdf_path}'.")
            return

        documento = fitz.open(pdf_path)

        for num_pagina in range(documento.page_count):
            if num_pagina % 10 == 0 or num_pagina == documento.page_count - 1: # Actualiza cada 10 paginas
                 status_queue.put(f"Leyendo página {num_pagina + 1}/{documento.page_count}...")

            pagina = documento.load_page(num_pagina)
            bloques = pagina.get_text("blocks")

            for bloque in bloques:
                if bloque[6] == 0: # Bloque de texto
                    texto_parrafo = bloque[4].strip().replace('\n', ' ')
                    texto_parrafo = re.sub(r'\s+', ' ', texto_parrafo).strip()
                    if texto_parrafo and patron.search(texto_parrafo):
                        parrafos_encontrados.append({
                            'pagina': num_pagina + 1,
                            'texto': texto_parrafo
                        })

        # Escritura del archivo
        status_queue.put("Escribiendo archivo de salida...")
        with open(txt_path, 'w', encoding='utf-8') as f_salida:
            if parrafos_encontrados:
                f_salida.write(f"Párrafos extraídos de '{os.path.basename(pdf_path)}' que contienen referencias legales:\n")
                f_salida.write("=" * 80 + "\n\n")
                for i, parrafo_info in enumerate(parrafos_encontrados):
                    f_salida.write(f"--- Párrafo {i+1} (Página {parrafo_info['pagina']}) ---\n")
                    f_salida.write(parrafo_info['texto'] + '\n\n')
                status_queue.put(f"¡Éxito! {len(parrafos_encontrados)} párrafos guardados en {os.path.basename(txt_path)}")
            else:
                f_salida.write(f"No se encontraron párrafos en '{os.path.basename(pdf_path)}' que contengan los términos de búsqueda.\n")
                status_queue.put(f"No se encontraron párrafos. Archivo de salida creado: {os.path.basename(txt_path)}")

    except fitz.fitz.FitzError as e:
        status_queue.put(f"Error al procesar PDF: {e}")
    except IOError as e:
         status_queue.put(f"Error al escribir archivo: {e}")
    except Exception as e:
        status_queue.put(f"Error inesperado: {e}")
    finally:
        if documento:
            documento.close()
        status_queue.put("DONE") # Señal de finalización

# --- Clase para la Aplicación GUI ---
class PdfExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractor de Párrafos Legales PDF")
        # Intenta ajustar al tamaño necesario, permite redimensionar
        self.root.geometry("550x400")
        self.root.minsize(450, 300)

        self.pdf_input_path = tk.StringVar()
        self.pdf_output_path = tk.StringVar()
        self.status_text = tk.StringVar()
        self.status_text.set("Arrastra un PDF o selecciónalo.")

        # --- Configuración Drag & Drop ---
        # Usamos un Frame como zona principal para soltar
        self.drop_frame = ttk.Frame(root, padding="10 10 10 10", relief="sunken", borderwidth=2)
        self.drop_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # El Frame es el objetivo del drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<DropEnter>>', self.on_drop_enter)
        self.drop_frame.dnd_bind('<<DropLeave>>', self.on_drop_leave)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)

        # Mensaje dentro del área de drop
        drop_label = ttk.Label(self.drop_frame, text="\nArrastra y suelta un archivo PDF aquí\n", anchor=tk.CENTER)
        drop_label.pack(fill=tk.BOTH, expand=True)

        # --- Botón de Selección Manual ---
        self.select_button = ttk.Button(root, text="O selecciona un archivo PDF...", command=self.select_pdf_file)
        self.select_button.pack(pady=5)

        # --- Info Archivo Seleccionado y Salida ---
        info_frame = ttk.Frame(root, padding="5")
        info_frame.pack(fill=tk.X, padx=10)

        ttk.Label(info_frame, text="Entrada:").grid(row=0, column=0, sticky=tk.W, padx=(0,5))
        self.input_label = ttk.Label(info_frame, textvariable=self.pdf_input_path, wraplength=400)
        self.input_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(info_frame, text="Salida:").grid(row=1, column=0, sticky=tk.W, padx=(0,5))
        self.output_label = ttk.Label(info_frame, textvariable=self.pdf_output_path, wraplength=400)
        self.output_label.grid(row=1, column=1, sticky=tk.W)

        # --- Botón de Extracción ---
        self.extract_button = ttk.Button(root, text="Extraer Párrafos", command=self.start_extraction, state=tk.DISABLED)
        self.extract_button.pack(pady=10)

        # --- Barra de Estado ---
        self.status_bar = ttk.Label(root, textvariable=self.status_text, relief=tk.SUNKEN, anchor=tk.W, padding="5 2")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Cola para comunicación con hilo ---
        self.status_queue = queue.Queue()

    def on_drop_enter(self, event):
        # Opcional: Cambia el aspecto al entrar
        self.drop_frame.config(relief="raised")

    def on_drop_leave(self, event):
        # Opcional: Restaura el aspecto al salir
        self.drop_frame.config(relief="sunken")

    def on_drop(self, event):
        self.drop_frame.config(relief="sunken")
        # event.data contiene la ruta del archivo (puede tener {} en Windows)
        filepath = event.data.strip('{}')
        if filepath and filepath.lower().endswith('.pdf'):
            self.update_selected_pdf(filepath)
        else:
            self.status_text.set("Error: Solo se pueden soltar archivos PDF.")
            messagebox.showerror("Error de Archivo", "Por favor, arrastra y suelta solo un archivo PDF.")

    def select_pdf_file(self):
        filepath = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.update_selected_pdf(filepath)

    def update_selected_pdf(self, filepath):
        self.pdf_input_path.set(os.path.basename(filepath))
        # Sugerir nombre de salida en el mismo directorio
        output_dir = os.path.dirname(filepath)
        output_filename = os.path.splitext(os.path.basename(filepath))[0] + "_parrafos.txt"
        self.pdf_output_path.set(os.path.join(output_dir, output_filename))
        self.extract_button.config(state=tk.NORMAL) # Habilitar botón
        self.status_text.set("Archivo PDF listo. Pulsa 'Extraer'.")

    def start_extraction(self):
        input_path = ""
        # Necesitamos la ruta completa, no solo el basename
        # Buscamos la ruta completa basada en el nombre y directorio sugerido
        if self.pdf_input_path.get() and self.pdf_output_path.get():
             output_path_full = self.pdf_output_path.get()
             input_dir = os.path.dirname(output_path_full)
             input_path = os.path.join(input_dir, self.pdf_input_path.get())
        else:
             messagebox.showerror("Error", "No se ha especificado un archivo PDF de entrada.")
             return

        output_path = self.pdf_output_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Faltan las rutas de entrada o salida.")
            return

        # Deshabilitar botones durante el proceso
        self.extract_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)
        self.status_text.set("Iniciando extracción...")

        # Iniciar el proceso en un hilo separado
        self.extraction_thread = threading.Thread(
            target=extraer_parrafos_legales,
            args=(input_path, output_path, self.status_queue),
            daemon=True # El hilo terminará si la app se cierra
        )
        self.extraction_thread.start()

        # Empezar a verificar la cola de estado
        self.root.after(100, self.check_status_queue)

    def check_status_queue(self):
        try:
            message = self.status_queue.get_nowait()
            if message == "DONE":
                # Proceso terminado, reactivar botones
                self.extract_button.config(state=tk.NORMAL if self.pdf_input_path.get() else tk.DISABLED)
                self.select_button.config(state=tk.NORMAL)
                # El último mensaje antes de DONE es el resultado final
            else:
                self.status_text.set(message)
                # Seguir verificando la cola
                self.root.after(100, self.check_status_queue)
        except queue.Empty:
            # Si la cola está vacía, seguir verificando
            self.root.after(100, self.check_status_queue)


# --- Punto de entrada ---
if __name__ == "__main__":
    # Usar TkinterDnD.Tk() en lugar de tk.Tk()
    root = TkinterDnD.Tk()
    app = PdfExtractorApp(root)
    root.mainloop()


```





