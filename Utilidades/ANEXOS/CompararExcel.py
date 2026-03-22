import tkinter as tk
from tkinter import scrolledtext, Label, Button, Frame, messagebox, filedialog, BOTH, X, Y, LEFT, RIGHT, TOP, BOTTOM, SUNKEN, W, E
import pandas as pd
import openpyxl # Usado por pandas y para obtener nombres de columna como letras
from openpyxl.utils import get_column_letter
import os # Para obtener el nombre base del archivo

# Variables globales para almacenar las rutas de los archivos
file1_path = None
file2_path = None

def update_file_label(label_widget, file_path):
    """Actualiza la etiqueta para mostrar el archivo seleccionado."""
    if file_path:
        label_widget.config(text=f"Archivo: {os.path.basename(file_path)}")
    else:
        label_widget.config(text="Ningún archivo seleccionado")

# --- Funciones para Seleccionar Archivos ---

def select_file1():
    """Abre un diálogo para seleccionar el primer archivo Excel."""
    global file1_path
    # Tipos de archivo permitidos
    filetypes = [("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    filepath = filedialog.askopenfilename(title="Seleccionar Archivo Excel 1", filetypes=filetypes)
    if filepath: # Si el usuario seleccionó un archivo (no canceló)
        file1_path = filepath
        update_file_label(file1_label, file1_path)
        # Podríamos añadir validación extra si quisiéramos aquí
    else:
        # Opcional: Restablecer si el usuario cancela
        # file1_path = None
        # update_file_label(file1_label, file1_path)
        pass # No hacer nada si cancela, mantiene la selección anterior

def select_file2():
    """Abre un diálogo para seleccionar el segundo archivo Excel."""
    global file2_path
    filetypes = [("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    filepath = filedialog.askopenfilename(title="Seleccionar Archivo Excel 2", filetypes=filetypes)
    if filepath:
        file2_path = filepath
        update_file_label(file2_label, file2_path)
    else:
        pass # No hacer nada si cancela

# --- Lógica de Comparación (Sin cambios respecto a la versión anterior) ---

def compare_excel_files():
    """Función principal para comparar los dos archivos Excel seleccionados."""
    if not file1_path or not file2_path:
        messagebox.showwarning("Advertencia", "Por favor, selecciona ambos archivos Excel antes de comparar.")
        return

    report_text.config(state=tk.NORMAL) # Habilitar escritura
    report_text.delete('1.0', tk.END) # Limpiar reporte anterior
    report_text.insert(tk.END, f"Comparando Archivo 1: {os.path.basename(file1_path)}\n")
    report_text.insert(tk.END, f"Comparando Archivo 2: {os.path.basename(file2_path)}\n")
    report_text.insert(tk.END, "="*40 + "\n\n")

    xls1 = None # Inicializar para el bloque finally
    xls2 = None

    try:
        # Usar pandas.ExcelFile para obtener nombres de hojas eficientemente
        xls1 = pd.ExcelFile(file1_path)
        xls2 = pd.ExcelFile(file2_path)
        sheets1 = set(xls1.sheet_names)
        sheets2 = set(xls2.sheet_names)

        # 1. Comparar Nombres de Pestañas
        report_text.insert(tk.END, "*** Comparación de Pestañas ***\n")
        common_sheets = sheets1.intersection(sheets2)
        sheets_only_in_1 = sheets1 - sheets2
        sheets_only_in_2 = sheets2 - sheets1

        if common_sheets:
             report_text.insert(tk.END, f"Pestañas Comunes ({len(common_sheets)}): {', '.join(sorted(list(common_sheets)))}\n")
        else:
             report_text.insert(tk.END, "No hay pestañas con el mismo nombre en ambos archivos.\n")

        if sheets_only_in_1:
            report_text.insert(tk.END, f"Pestañas solo en Archivo 1 ({len(sheets_only_in_1)}): {', '.join(sorted(list(sheets_only_in_1)))}\n")
        if sheets_only_in_2:
            report_text.insert(tk.END, f"Pestañas solo en Archivo 2 ({len(sheets_only_in_2)}): {', '.join(sorted(list(sheets_only_in_2)))}\n")

        report_text.insert(tk.END, "\n" + "="*40 + "\n\n")

        # 2. Comparar Contenido de Pestañas Comunes
        if not common_sheets:
            report_text.insert(tk.END, "No hay pestañas comunes para comparar contenido.\n")
        else:
            report_text.insert(tk.END, "*** Comparación de Contenido (Pestañas Comunes) ***\n")
            for sheet_name in sorted(list(common_sheets)):
                report_text.insert(tk.END, f"\n--- Comparando Pestaña: '{sheet_name}' ---\n")
                try:
                    # Leer las hojas específicas como DataFrames
                    df1 = pd.read_excel(xls1, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)
                    df2 = pd.read_excel(xls2, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)

                    differences_found_in_sheet = False

                    # Comparar dimensiones
                    if df1.shape != df2.shape:
                        report_text.insert(tk.END, f"  - Diferencia de dimensiones: Archivo 1 ({df1.shape[0]}x{df1.shape[1]}) vs Archivo 2 ({df2.shape[0]}x{df2.shape[1]})\n")
                        differences_found_in_sheet = True

                    # Comparar celda por celda hasta el máximo de filas/columnas
                    max_rows = max(df1.shape[0], df2.shape[0])
                    max_cols = max(df1.shape[1], df2.shape[1])

                    for r in range(max_rows):
                        for c in range(max_cols):
                            val1_str = ""
                            val2_str = ""
                            cell_ref = f"{get_column_letter(c + 1)}{r + 1}" # Referencia tipo Excel (A1, B2, etc.)

                            try:
                                if r < df1.shape[0] and c < df1.shape[1]:
                                     val1 = df1.iloc[r, c]
                                     val1_str = str(val1)
                                else:
                                     val1_str = "[CELDA NO EXISTE]"
                            except IndexError:
                                val1_str = "[ERROR LECTURA F1]"

                            try:
                                if r < df2.shape[0] and c < df2.shape[1]:
                                     val2 = df2.iloc[r, c]
                                     val2_str = str(val2)
                                else:
                                     val2_str = "[CELDA NO EXISTE]"
                            except IndexError:
                                val2_str = "[ERROR LECTURA F2]"

                            # Comparar los valores (como strings)
                            if val1_str != val2_str:
                                report_text.insert(tk.END, f"  - Diferencia en Celda {cell_ref}: '{val1_str}' (F1) != '{val2_str}' (F2)\n")
                                differences_found_in_sheet = True

                    if not differences_found_in_sheet:
                         report_text.insert(tk.END, "  - Sin diferencias encontradas en el contenido de las celdas.\n")

                except Exception as e_sheet:
                     report_text.insert(tk.END, f"  - Error al procesar la pestaña '{sheet_name}': {e_sheet}\n")
                     differences_found_in_sheet = True

        report_text.insert(tk.END, "\n" + "="*40 + "\n")
        report_text.insert(tk.END, "Comparación completada.\n")

    except Exception as e_global:
        report_text.insert(tk.END, f"\n*** ERROR GENERAL DURANTE LA COMPARACIÓN ***\n{e_global}\n")
        messagebox.showerror("Error", f"Ocurrió un error al procesar los archivos: {e_global}")

    finally:
        # Asegurarse de cerrar los archivos si pandas los mantiene abiertos
        try:
            if xls1:
                xls1.close()
            if xls2:
                xls2.close()
        except Exception as e_close:
            print(f"Advertencia: no se pudieron cerrar los archivos Excel: {e_close}") # Opcional: log
        report_text.config(state=tk.DISABLED) # Hacer el texto no editable

# --- Configuración de la GUI ---
# Usar tk.Tk() estándar
root = tk.Tk()
root.title("Comparador de Archivos Excel")
root.geometry("700x600")

# Frame para los controles de selección de archivos
selection_frame = Frame(root, padx=10, pady=10)
selection_frame.pack(fill=X, side=TOP)

# --- Controles para Archivo 1 ---
file1_frame = Frame(selection_frame)
file1_frame.pack(side=LEFT, fill=X, expand=True, padx=5)

btn_select1 = Button(file1_frame, text="Seleccionar Archivo 1", command=select_file1)
btn_select1.pack(side=TOP, fill=X, pady=(0, 5)) # Espacio debajo del botón

file1_label = Label(file1_frame, text="Ningún archivo seleccionado", relief=SUNKEN, anchor=W, justify=LEFT, padx=5)
file1_label.pack(side=TOP, fill=X)

# --- Controles para Archivo 2 ---
file2_frame = Frame(selection_frame)
file2_frame.pack(side=RIGHT, fill=X, expand=True, padx=5)

btn_select2 = Button(file2_frame, text="Seleccionar Archivo 2", command=select_file2)
btn_select2.pack(side=TOP, fill=X, pady=(0, 5)) # Espacio debajo del botón

file2_label = Label(file2_frame, text="Ningún archivo seleccionado", relief=SUNKEN, anchor=W, justify=LEFT, padx=5)
file2_label.pack(side=TOP, fill=X)

# Botón de Comparación
compare_button = Button(root, text="Comparar Archivos", command=compare_excel_files, height=2)
compare_button.pack(pady=10, fill=X, padx=10)

# Área de texto para mostrar el reporte (con scroll)
# report_frame = Frame(root, padx=10, pady=(0, 10)) # Padding inferior para el frame
# report_frame.pack(fill=BOTH, expand=True)
# Corrección: Definir Frame sin pady tupla, aplicarla en pack()
report_frame = Frame(root, padx=10) # Quita pady=(0, 10) de aquí
report_frame.pack(fill=BOTH, expand=True, pady=(0, 10)) # Añade pady=(0, 10) aquí


report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, state=tk.DISABLED) # Inicia deshabilitado
report_text.pack(fill=BOTH, expand=True)

# Iniciar el bucle principal de la GUI
root.mainloop()