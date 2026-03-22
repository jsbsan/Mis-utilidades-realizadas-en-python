import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pyperclip  # Necesitarás instalar esta librería: pip install pyperclip

def seleccionar_directorio():
    """Abre un diálogo para que el usuario seleccione un directorio."""
    directorio_seleccionado = filedialog.askdirectory()
    if directorio_seleccionado:
        ruta_directorio.set(directorio_seleccionado)
        listar_ficheros(directorio_seleccionado)

def listar_ficheros(directorio):
    """Muestra los ficheros del directorio en el cuadro de texto."""
    listado_ficheros.delete('1.0', tk.END)  # Limpia el contenido anterior
    try:
        ficheros = os.listdir(directorio)
        if ficheros:
            for fichero in ficheros:
                listado_ficheros.insert(tk.END, fichero + '\n')
        else:
            listado_ficheros.insert(tk.END, "El directorio está vacío.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo acceder al directorio:\n{e}")

def copiar_al_portapapeles():
    """Copia el listado de ficheros del cuadro de texto al portapapeles."""
    contenido = listado_ficheros.get('1.0', tk.END).strip()
    if contenido and contenido != "El directorio está vacío.":
        pyperclip.copy(contenido)
        messagebox.showinfo("Copiado", "¡Listado de ficheros copiado al portapapeles!")
    else:
        messagebox.showwarning("Advertencia", "No hay nada que copiar.")

# --- Configuración de la ventana principal ---
ventana = tk.Tk()
ventana.title("Listado de Ficheros de un Directorio")
ventana.geometry("500x450")
ventana.resizable(True, True)

# Variable para almacenar la ruta del directorio
ruta_directorio = tk.StringVar()

# --- Creación de los widgets ---
frame_superior = tk.Frame(ventana, pady=10)
frame_superior.pack(fill='x')

boton_seleccionar = tk.Button(frame_superior, text="📂 Seleccionar Directorio", command=seleccionar_directorio)
boton_seleccionar.pack(side='left', padx=10)

etiqueta_ruta = tk.Label(frame_superior, textvariable=ruta_directorio, fg="blue", wraplength=350)
etiqueta_ruta.pack(side='left', fill='x', expand=True)

# Cuadro de texto para mostrar el listado de ficheros
frame_texto = tk.Frame(ventana, padx=10)
frame_texto.pack(fill='both', expand=True)

listado_ficheros = tk.Text(frame_texto, wrap='none', height=15, width=50)
listado_ficheros.pack(side='left', fill='both', expand=True)

# Barra de desplazamiento para el cuadro de texto
scrollbar_y = tk.Scrollbar(frame_texto, orient='vertical', command=listado_ficheros.yview)
scrollbar_y.pack(side='right', fill='y')
listado_ficheros.config(yscrollcommand=scrollbar_y.set)

scrollbar_x = tk.Scrollbar(ventana, orient='horizontal', command=listado_ficheros.xview)
scrollbar_x.pack(fill='x', padx=10)
listado_ficheros.config(xscrollcommand=scrollbar_x.set)

# Botón para copiar al portapapeles
boton_copiar = tk.Button(ventana, text="📋 Copiar al Portapapeles", command=copiar_al_portapapeles, pady=5)
boton_copiar.pack(pady=10)


# --- Iniciar el bucle de la aplicación ---
ventana.mainloop()