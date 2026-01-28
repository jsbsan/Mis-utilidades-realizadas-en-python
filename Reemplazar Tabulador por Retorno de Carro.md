#utilidades/programación 
#python 

<span style="background:#b1ffff">prompt:</span>
HAZ UN SCRIPT EN PYTHON CON ENTORNO VISUAL, QUE EL USUARIO PEGUE UN TEXTO Y EL PROGRAMA DEVUELVA EL MISMO TEXTO PERO CAMBIANDO LOS TABULADORES POR RETORNOS DE CARROS.
añade un boton al interfaz para borrar los textos original y convertido

<span style="background:#b1ffff">Captura de Pantalla:</span>
![ANEXOS/Pasted%20image%2020251021101951.png|300]  

<span style="background:#b1ffff">Codigo</span>
```python
import tkinter as tk

from tkinter import ttk

from tkinter import scrolledtext

  

def convertir_texto():

    """

    Toma el texto del cuadro de entrada, reemplaza tabuladores por

    saltos de línea y lo pone en el cuadro de salida.

    """

    texto_original = entrada_texto.get("1.0", tk.END)

    texto_convertido = texto_original.replace('\t', '\n')

    salida_texto.delete("1.0", tk.END)

    salida_texto.insert(tk.END, texto_convertido)

  

def copiar_al_portapapeles():

    """

    Copia el contenido del cuadro de salida al portapapeles del sistema.

    """

    texto_resultado = salida_texto.get("1.0", tk.END)

    if texto_resultado.strip():

        ventana.clipboard_clear()

        ventana.clipboard_append(texto_resultado)

        ventana.update()

        print("¡Texto copiado al portapapeles!")

  

# --- NUEVA FUNCIÓN ---

def borrar_textos():

    """

    Limpia el contenido de ambos cuadros de texto.

    """

    entrada_texto.delete("1.0", tk.END)

    salida_texto.delete("1.0", tk.END)

    print("Campos limpiados.")

  

# --- Configuración de la Ventana Principal ---

  

ventana = tk.Tk()

ventana.title("Reemplazar Tabuladores por Saltos de Línea")

ventana.geometry("700x550")

  

estilo = ttk.Style(ventana)

estilo.theme_use('clam')

  

frame_principal = ttk.Frame(ventana, padding="10")

frame_principal.pack(fill=tk.BOTH, expand=True)

  

# --- Widgets de Entrada ---

  

etiqueta_entrada = ttk.Label(frame_principal, text="Pega el texto original aquí:")

etiqueta_entrada.pack(pady=(0, 5), anchor="w")

  

entrada_texto = scrolledtext.ScrolledText(frame_principal, height=10, width=80, wrap=tk.WORD)

entrada_texto.pack(fill=tk.BOTH, expand=True, pady=5)

  

# --- Botón de Conversión ---

  

boton_convertir = ttk.Button(frame_principal, text="Convertir Tabuladores ➔ Saltos de Línea", command=convertir_texto)

boton_convertir.pack(pady=10)

  

# --- Widgets de Salida ---

  

etiqueta_salida = ttk.Label(frame_principal, text="Texto convertido:")

etiqueta_salida.pack(pady=(5, 5), anchor="w")

  

salida_texto = scrolledtext.ScrolledText(frame_principal, height=10, width=80, wrap=tk.WORD)

salida_texto.pack(fill=tk.BOTH, expand=True, pady=5)

  

# --- NUEVO: Frame para los botones inferiores ---

# Usamos un frame para que los botones "Copiar" y "Limpiar"

# aparezcan uno al lado del otro.

frame_botones_inferiores = ttk.Frame(frame_principal)

frame_botones_inferiores.pack(fill='x', pady=5)

  

# Botón para copiar el resultado (ahora dentro del frame inferior)

boton_copiar = ttk.Button(frame_botones_inferiores, text="Copiar Resultado", command=copiar_al_portapapeles)

# side=tk.LEFT hace que se alinee a la izquierda

# expand=True y fill='x' hacen que ocupe el espacio disponible

boton_copiar.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 5))

  

# --- NUEVO: Botón para Limpiar ---

boton_limpiar = ttk.Button(frame_botones_inferiores, text="Limpiar Campos", command=borrar_textos)

# side=tk.RIGHT hace que se alinee a la derecha

boton_limpiar.pack(side=tk.RIGHT, expand=True, fill='x', padx=(5, 0))

  
  

# --- Iniciar el Bucle Principal ---

  

ventana.mainloop()
```

<span style="background:#b1ffff">archivo:</span>
![ANEXOS/CambioTABporRetornoCarro.py]  