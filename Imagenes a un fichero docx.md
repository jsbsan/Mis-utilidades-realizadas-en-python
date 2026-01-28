#utilidades/programación 
#python 


Programa en Python que con "coger y soltar"  las imágenes crea un fichero .docx
![[Pasted image 20250408162029.png|300]]

Fichero:
![[ImagenesAdocx.py]]


Código:
``` python
import tkinter as tk
from tkinter import ttk  # Para widgets mejorados (opcional pero recomendado)
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD  # Importante para drag & drop
import os
import docx
from docx.shared import Inches # Para especificar el tamaño de la imagen

# Lista de extensiones de imagen comunes que queremos procesar
SUPPORTED_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')

# --- Funciones Lógicas ---

def find_images_in_directory(directory_path):
    """Encuentra todos los archivos de imagen soportados en un directorio."""
    image_files = []
    if not os.path.isdir(directory_path):
        return image_files # Devuelve lista vacía si no es un directorio válido

    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            # Comprueba si es un archivo y si tiene una extensión de imagen soportada
            if os.path.isfile(item_path) and item.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS):
                image_files.append(item_path)
    except Exception as e:
        messagebox.showerror("Error al leer directorio", f"No se pudo leer el directorio:\n{e}")
    return image_files

def create_docx_with_images(image_paths, output_docx_path):
    """Crea un documento .docx y añade las imágenes especificadas."""
    if not image_paths:
        messagebox.showwarning("Sin imágenes", "No se encontraron imágenes válidas en la carpeta seleccionada.")
        return False
    if not output_docx_path.lower().endswith(".docx"):
        output_docx_path += ".docx" # Asegura que la extensión sea .docx

    doc = docx.Document()
    doc.add_heading('Presa: ', level=1)
    doc.add_heading('Actuación: ', level=2)
    doc.add_heading('Periodo/Fecha: ', level=2)
    doc.add_paragraph() # Añade un espacio
    doc.add_paragraph('A continuación reportaje fotográfico de los trabajos realizados.')
    doc.add_paragraph() # Añade un espacio

    added_count = 0
    for img_path in image_paths:
        try:
            # Añade la imagen. Ajusta el ancho si es necesario (ej. 6 pulgadas)
            # Puedes ajustar 'width' o 'height'. Si solo pones uno, mantiene la proporción.
            doc.add_picture(img_path, width=Inches(6.0))
            # Añade un pequeño párrafo después de cada imagen para separarlas
            doc.add_paragraph()
            added_count += 1
            # Actualizar estado (opcional, puede ralentizar si hay muchas imágenes)
            # status_label.config(text=f"Añadiendo imagen {added_count}/{len(image_paths)}...")
            # root.update_idletasks()
        except Exception as e:
            print(f"Advertencia: No se pudo añadir la imagen {os.path.basename(img_path)}: {e}")
            # Opcional: Informar al usuario sobre imágenes omitidas
            # messagebox.showwarning("Error de Imagen", f"No se pudo añadir la imagen:\n{os.path.basename(img_path)}\nError: {e}")


    try:
        doc.save(output_docx_path)
        messagebox.showinfo("Éxito", f"¡Documento '{os.path.basename(output_docx_path)}' creado con {added_count} imágenes!")
        return True
    except Exception as e:
        messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo .docx:\n{e}")
        return False

# --- Funciones de la Interfaz Gráfica (GUI) ---

def handle_drop(event):
    """Maneja los archivos/carpetas soltados en el área designada."""
    # event.data contiene una cadena con las rutas, a veces entre {} si tienen espacios
    path_data = event.data.strip()
    if path_data.startswith('{') and path_data.endswith('}'):
        # Quita las llaves si están presentes (común en Windows para rutas con espacios)
        path_data = path_data[1:-1]

    # Asumimos que el usuario soltará UNA carpeta (o el primer elemento si son varios)
    # Podrías adaptar esto para manejar múltiples carpetas o archivos individuales si quisieras
    potential_path = path_data.split('} {')[0] # Maneja el caso de múltiples elementos soltados

    if os.path.isdir(potential_path):
        source_dir_var.set(potential_path)
        status_label.config(text=f"Carpeta seleccionada: {os.path.basename(potential_path)}")
        list_images_in_selected_folder() # Opcional: mostrar imágenes encontradas
    elif os.path.isfile(potential_path):
         # Si suelta un archivo, usa el directorio que lo contiene
         containing_dir = os.path.dirname(potential_path)
         source_dir_var.set(containing_dir)
         status_label.config(text=f"Carpeta seleccionada (desde archivo): {os.path.basename(containing_dir)}")
         list_images_in_selected_folder() # Opcional
    else:
        messagebox.showwarning("Elemento no válido", "Por favor, arrastra una CARPETA que contenga imágenes.")
        status_label.config(text="Error: Arrastra una carpeta válida.")

def browse_source_directory():
    """Abre un diálogo para seleccionar la carpeta de imágenes."""
    directory = filedialog.askdirectory(title="Selecciona la carpeta con imágenes")
    if directory:
        source_dir_var.set(directory)
        status_label.config(text=f"Carpeta seleccionada: {os.path.basename(directory)}")
        list_images_in_selected_folder() # Opcional

def browse_output_file():
    """Abre un diálogo para seleccionar dónde guardar el archivo .docx."""
    filepath = filedialog.asksaveasfilename(
        title="Guardar documento como...",
        defaultextension=".docx",
        filetypes=[("Documentos Word", "*.docx"), ("Todos los archivos", "*.*")]
    )
    if filepath:
        # Asegurarse de que la extensión es .docx
        if not filepath.lower().endswith(".docx"):
            filepath += ".docx"
        output_file_var.set(filepath)
        status_label.config(text="Archivo de salida seleccionado.")

def list_images_in_selected_folder():
    """(Opcional) Muestra las imágenes encontradas en un Listbox."""
    image_listbox.delete(0, tk.END) # Limpia la lista
    source_dir = source_dir_var.get()
    if source_dir and os.path.isdir(source_dir):
        images = find_images_in_directory(source_dir)
        if images:
            image_listbox.insert(tk.END, f"{len(images)} imágenes encontradas:")
            for img_path in images:
                image_listbox.insert(tk.END, f"  - {os.path.basename(img_path)}")
        else:
             image_listbox.insert(tk.END, "No se encontraron imágenes soportadas.")
    else:
        image_listbox.insert(tk.END, "Selecciona o arrastra una carpeta válida.")


def start_creation_process():
    """Inicia el proceso de creación del DOCX."""
    source_dir = source_dir_var.get()
    output_file = output_file_var.get()

    if not source_dir or not os.path.isdir(source_dir):
        messagebox.showerror("Error", "Por favor, selecciona una carpeta de origen válida.")
        return
    if not output_file:
        messagebox.showerror("Error", "Por favor, especifica un archivo de salida.")
        # Podríamos llamar a browse_output_file() aquí automáticamente
        # browse_output_file()
        # output_file = output_file_var.get() # Re-obtener por si el usuario cancela
        # if not output_file: return
        return

    image_paths = find_images_in_directory(source_dir)
    if not image_paths:
        status_label.config(text="No se encontraron imágenes válidas para procesar.")
        return # Ya se mostró un warning en find_images_in_directory o create_docx_with_images

    status_label.config(text="Procesando... por favor espera.")
    root.update_idletasks() # Actualiza la GUI para mostrar el mensaje

    # Deshabilitar botón mientras procesa
    create_button.config(state=tk.DISABLED)

    success = create_docx_with_images(image_paths, output_file)

    # Rehabilitar botón
    create_button.config(state=tk.NORMAL)

    if success:
        status_label.config(text="¡Proceso completado!")
        # Opcional: limpiar campos después de éxito
        # source_dir_var.set("")
        # output_file_var.set("")
        # image_listbox.delete(0, tk.END)
    else:
        status_label.config(text="Proceso fallido. Revisa los mensajes de error.")


# --- Configuración de la Interfaz Gráfica (GUI) ---

# Usar TkinterDnD.Tk() en lugar de tk.Tk() para habilitar drag & drop
root = TkinterDnD.Tk()
root.title("Creador de DOCX con Imágenes")
root.geometry("550x500") # Ajusta tamaño según necesites

# --- Variables de Tkinter ---
source_dir_var = tk.StringVar()
output_file_var = tk.StringVar()

# --- Widgets ---

# Frame para la selección de la carpeta de origen
source_frame = ttk.LabelFrame(root, text="1. Carpeta de Imágenes de Origen")
source_frame.pack(padx=10, pady=10, fill="x")

# Etiqueta/Área para soltar (Drag and Drop Target)
# Usamos un Label como área visual para soltar
drop_target_label = tk.Label(
    source_frame,
    text="Arrastra la CARPETA con imágenes aquí\no usa el botón 'Explorar'",
    relief="solid", # Borde para que sea visible
    borderwidth=1,
    pady=20 # Espacio vertical interno
)
drop_target_label.pack(pady=10, padx=10, fill="x")

# Registrar el Label como destino para soltar archivos
drop_target_label.drop_target_register(DND_FILES)
drop_target_label.dnd_bind('<<Drop>>', handle_drop) # Vincular el evento Drop

# Entrada para mostrar la ruta seleccionada (solo lectura es buena opción)
source_entry = ttk.Entry(source_frame, textvariable=source_dir_var, state="readonly", width=60)
source_entry.pack(side=tk.LEFT, padx=(10, 5), pady=5, expand=True, fill="x")

# Botón para explorar carpeta
browse_source_button = ttk.Button(source_frame, text="Explorar...", command=browse_source_directory)
browse_source_button.pack(side=tk.LEFT, padx=(0, 10), pady=5)

# (Opcional) Listbox para mostrar las imágenes encontradas
image_listbox = tk.Listbox(root, height=8, width=70)
image_listbox.pack(padx=10, pady=5, fill="x")
list_images_in_selected_folder() # Llama inicial para mostrar mensaje


# Frame para la selección del archivo de salida
output_frame = ttk.LabelFrame(root, text="2. Archivo .DOCX de Salida")
output_frame.pack(padx=10, pady=10, fill="x")

# Entrada para mostrar la ruta del archivo de salida
output_entry = ttk.Entry(output_frame, textvariable=output_file_var, state="readonly", width=60)
output_entry.pack(side=tk.LEFT, padx=(10, 5), pady=5, expand=True, fill="x")

# Botón para elegir archivo de salida
browse_output_button = ttk.Button(output_frame, text="Guardar como...", command=browse_output_file)
browse_output_button.pack(side=tk.LEFT, padx=(0, 10), pady=5)


# Botón para crear el documento
create_button = ttk.Button(root, text="Crear Documento DOCX", command=start_creation_process)
create_button.pack(pady=20)

# Etiqueta de estado
status_label = ttk.Label(root, text="Esperando acciones...", relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)


# --- Iniciar el bucle principal de la GUI ---
root.mainloop()
```

Nota:
Generado por Gemini