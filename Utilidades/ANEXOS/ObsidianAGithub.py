import tkinter as tk

from tkinter import filedialog, messagebox

import re

import os

  

def transformar_linea(match):

  # Extraer el contenido dentro de ![[ ... ]]

  contenido = match.group(1).strip()

  # Lógica de limpieza: quitar espacios en el nombre del archivo

  nombre_limpio = contenido.replace(" ", "")

  # Extensiones de imagen comunes

  extensiones_img = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')

  if nombre_limpio.lower().endswith(extensiones_img):

    # Formato Imagen para GitHub

    return f"![-](./ANEXOS/{nombre_limpio})"

  else:

    # Formato Descarga para GitHub

    return f"[descargar](./ANEXOS/{nombre_limpio})"

  

def procesar_archivos():

  # Seleccionar archivos

  rutas_archivos = filedialog.askopenfilenames(

    title="Selecciona tus archivos Markdown",

    filetypes=[("Markdown files", "*.md")]

  )

  if not rutas_archivos:

    return

  

  procesados = 0

  for ruta in rutas_archivos:

    try:

      with open(ruta, 'r', encoding='utf-8') as f:

        texto = f.read()

  

      # Regex para encontrar ![[nombre_archivo]]

      # El patrón busca: ![ seguido de [[, captura todo hasta ]], y cierra con ]]

      nuevo_texto = re.sub(r'!\[\[(.*?)\]\]', transformar_linea, texto)

  

      # Crear nuevo nombre de archivo

      directorio, nombre = os.path.split(ruta)

      nombre_sin_ext, ext = os.path.splitext(nombre)

      nueva_ruta = os.path.join(directorio, f"{nombre_sin_ext}_github{ext}")

  

      with open(nueva_ruta, 'w', encoding='utf-8') as f:

        f.write(nuevo_texto)

      procesados += 1

    except Exception as e:

      messagebox.showerror("Error", f"No se pudo procesar {nombre}: {e}")

  

  messagebox.showinfo("Éxito", f"Se han procesado {procesados} archivo(s) correctamente.")

  

# Configuración de la interfaz visual

root = tk.Tk()

root.title("Obsidian to GitHub Link Converter")

root.geometry("400x200")

  

label = tk.Label(root, text="Convertidor de Enlaces Markdown", font=("Arial", 12, "bold"), pady=20)

label.pack()

  

btn_procesar = tk.Button(

  root,

  text="Seleccionar Archivos .md",

  command=procesar_archivos,

  bg="#2c3e50",

  fg="white",

  padx=20,

  pady=10,

  font=("Arial", 10)

)

btn_procesar.pack(pady=10)

  

footer = tk.Label(root, text="Los archivos se guardarán con el sufijo '_github'", font=("Arial", 8), fg="gray")

footer.pack(side="bottom", pady=10)

  

root.mainloop()
