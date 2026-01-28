import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

class MarkdownMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unificador de Archivos Markdown (.md)")
        self.root.geometry("500x350")

        # --- Elementos de la Interfaz ---

        # Título / Instrucciones
        self.label_info = tk.Label(
            root, 
            text="1. Selecciona una carpeta para buscar archivos .md\n2. El programa unirá el contenido de todos ellos.",
            pady=10
        )
        self.label_info.pack()

        # Botón Principal
        self.btn_action = tk.Button(
            root, 
            text="Seleccionar Carpeta y Unir", 
            command=self.procesar_archivos,
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 11, "bold"),
            padx=10, 
            pady=5
        )
        self.btn_action.pack(pady=15)

        # Área de log/estado
        self.log_area = scrolledtext.ScrolledText(root, height=10, width=55, state='disabled')
        self.log_area.pack(padx=10, pady=10)

        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Esperando acción del usuario...")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log(self, message):
        """Función auxiliar para escribir en el área de texto."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def procesar_archivos(self):
        # 1. Seleccionar Ruta de Origen
        directorio_origen = filedialog.askdirectory(title="Selecciona la carpeta raíz a escanear")
        
        if not directorio_origen:
            return  # El usuario canceló

        self.log(f"--- Escaneando: {directorio_origen} ---")
        self.status_var.set("Escaneando archivos...")
        self.root.update()

        contenido_total = []
        archivos_encontrados = 0

        # 2. Recorrer carpetas y subcarpetas
        for root, dirs, files in os.walk(directorio_origen):
            for file in files:
                if file.lower().endswith(".md"):
                    ruta_completa = os.path.join(root, file)
                    archivos_encontrados += 1
                    
                    # Formato del encabezado para cada archivo
                    encabezado = f"\n\n{'='*60}\n"
                    encabezado += f" ARCHIVO: {file}\n"
                    encabezado += f" RUTA: {ruta_completa}\n"
                    encabezado += f"{'='*60}\n\n"
                    
                    contenido_total.append(encabezado)
                    
                    try:
                        # Leemos el archivo (forzando UTF-8 para evitar errores de caracteres)
                        with open(ruta_completa, 'r', encoding='utf-8', errors='replace') as f:
                            texto = f.read()
                            contenido_total.append(texto)
                            self.log(f"Leído: {file}")
                    except Exception as e:
                        error_msg = f"[ERROR leyendo {file}: {str(e)}]\n"
                        contenido_total.append(error_msg)
                        self.log(f"Error en: {file}")

        if archivos_encontrados == 0:
            messagebox.showwarning("Aviso", "No se encontraron archivos .md en esa carpeta.")
            self.status_var.set("Listo.")
            return

        self.log(f"--- Se encontraron {archivos_encontrados} archivos. ---")
        
        # 3. Preguntar nombre de salida y Guardar
        archivo_salida = filedialog.asksaveasfilename(
            title="Guardar archivo unificado como...",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if archivo_salida:
            try:
                texto_final = "".join(contenido_total)
                with open(archivo_salida, 'w', encoding='utf-8') as f_out:
                    f_out.write(texto_final)
                
                messagebox.showinfo("Éxito", f"Se han unido {archivos_encontrados} archivos correctamente.\nGuardado en:\n{archivo_salida}")
                self.log(f"Guardado en: {archivo_salida}")
                self.status_var.set("Proceso completado con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
        else:
            self.log("Guardado cancelado por el usuario.")
            self.status_var.set("Operación cancelada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownMergerApp(root)
    root.mainloop()