import tkinter as tk
from tkinter import scrolledtext, Label, Button, Frame, messagebox, filedialog, ttk # Importar ttk
from tkinter import BOTH, X, Y, LEFT, RIGHT, TOP, BOTTOM, SUNKEN, W, E, DISABLED, NORMAL # Importar constantes de estado
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

# --- Funciones para Seleccionar Archivos (sin cambios) ---

def select_file1():
    """Abre un diálogo para seleccionar el primer archivo Excel."""
    global file1_path
    filetypes = [("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    filepath = filedialog.askopenfilename(title="Seleccionar Archivo Excel 1", filetypes=filetypes)
    if filepath:
        file1_path = filepath
        update_file_label(file1_label, file1_path)
    else:
        pass

def select_file2():
    """Abre un diálogo para seleccionar el segundo archivo Excel."""
    global file2_path
    filetypes = [("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    filepath = filedialog.askopenfilename(title="Seleccionar Archivo Excel 2", filetypes=filetypes)
    if filepath:
        file2_path = filepath
        update_file_label(file2_label, file2_path)
    else:
        pass

# --- Lógica de Comparación (Modificada para usar Notebook) ---

def clear_notebook_tabs(notebook):
    """Elimina todas las pestañas de un widget Notebook."""
    # Iterar sobre las pestañas existentes y eliminarlas
    # Es más seguro iterar mientras se comprueba si existen pestañas
    while True:
        try:
            # .tabs() devuelve una lista de identificadores de pestaña
            # Intentamos eliminar la primera pestaña en cada iteración
            notebook.forget(notebook.tabs()[0])
        except IndexError:
            # Se lanza IndexError cuando .tabs() está vacío
            break

def add_report_tab(notebook, title):
    """Crea una nueva pestaña con un ScrolledText y la devuelve."""
    tab_frame = Frame(notebook, padx=5, pady=5)
    notebook.add(tab_frame, text=title)
    
    # Crear el widget ScrolledText dentro del frame de la pestaña
    report_widget = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, state=DISABLED)
    report_widget.pack(fill=BOTH, expand=True)
    
    return report_widget # Devolver el widget de texto para poder escribir en él

def compare_excel_files():
    """Función principal para comparar los dos archivos Excel seleccionados."""
    if not file1_path or not file2_path:
        messagebox.showwarning("Advertencia", "Por favor, selecciona ambos archivos Excel antes de comparar.")
        return

    # Limpiar pestañas anteriores del Notebook
    clear_notebook_tabs(report_notebook)

    # Crear la pestaña de Resumen y obtener su widget de texto
    summary_text = add_report_tab(report_notebook, "Resumen General")
    summary_text.config(state=NORMAL) # Habilitar escritura temporalmente

    # Añadir información inicial al Resumen
    summary_text.insert(tk.END, f"Comparando Archivo 1: {os.path.basename(file1_path)}\n")
    summary_text.insert(tk.END, f"Comparando Archivo 2: {os.path.basename(file2_path)}\n")
    summary_text.insert(tk.END, "="*40 + "\n\n")

    xls1 = None # Inicializar para el bloque finally
    xls2 = None

    try:
        # Usar pandas.ExcelFile para obtener nombres de hojas eficientemente
        xls1 = pd.ExcelFile(file1_path)
        xls2 = pd.ExcelFile(file2_path)
        sheets1 = set(xls1.sheet_names)
        sheets2 = set(xls2.sheet_names)

        # 1. Comparar Nombres de Pestañas (en la pestaña Resumen)
        summary_text.insert(tk.END, "*** Comparación de Pestañas ***\n")
        common_sheets = sheets1.intersection(sheets2)
        sheets_only_in_1 = sheets1 - sheets2
        sheets_only_in_2 = sheets2 - sheets1

        if common_sheets:
             summary_text.insert(tk.END, f"Pestañas Comunes ({len(common_sheets)}): {', '.join(sorted(list(common_sheets)))}\n")
        else:
             summary_text.insert(tk.END, "No hay pestañas con el mismo nombre en ambos archivos.\n")

        if sheets_only_in_1:
            summary_text.insert(tk.END, f"Pestañas solo en Archivo 1 ({len(sheets_only_in_1)}): {', '.join(sorted(list(sheets_only_in_1)))}\n")
        if sheets_only_in_2:
            summary_text.insert(tk.END, f"Pestañas solo en Archivo 2 ({len(sheets_only_in_2)}): {', '.join(sorted(list(sheets_only_in_2)))}\n")

        summary_text.insert(tk.END, "\n" + "="*40 + "\n\n")
        summary_text.insert(tk.END, "Ver las pestañas individuales para detalles de contenido.\n")
        summary_text.config(state=DISABLED) # Deshabilitar edición del resumen

        # 2. Comparar Contenido de Pestañas Comunes (en pestañas individuales)
        if not common_sheets:
             # Añadir mensaje también al resumen si no hay nada más que comparar
             summary_text.config(state=NORMAL)
             summary_text.insert(tk.END, "\nNo hay pestañas comunes para comparar contenido.\n")
             summary_text.config(state=DISABLED)
        else:
            for sheet_name in sorted(list(common_sheets)):
                # Crear una nueva pestaña para esta hoja y obtener su widget de texto
                sheet_text = add_report_tab(report_notebook, sheet_name) # Usar nombre de hoja como título
                sheet_text.config(state=NORMAL) # Habilitar escritura
                
                sheet_text.insert(tk.END, f"--- Comparando Pestaña: '{sheet_name}' ---\n\n")
                
                try:
                    # Leer las hojas específicas como DataFrames
                    df1 = pd.read_excel(xls1, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)
                    df2 = pd.read_excel(xls2, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)

                    differences_found_in_sheet = False

                    # Comparar dimensiones
                    if df1.shape != df2.shape:
                        sheet_text.insert(tk.END, f"  - Diferencia de dimensiones: Archivo 1 ({df1.shape[0]}x{df1.shape[1]}) vs Archivo 2 ({df2.shape[0]}x{df2.shape[1]})\n")
                        differences_found_in_sheet = True

                    # Comparar celda por celda hasta el máximo de filas/columnas
                    max_rows = max(df1.shape[0], df2.shape[0])
                    max_cols = max(df1.shape[1], df2.shape[1])
                    cell_diff_count = 0 # Contador para diferencias de celda

                    for r in range(max_rows):
                        for c in range(max_cols):
                            val1_str = ""
                            val2_str = ""
                            cell_ref = f"{get_column_letter(c + 1)}{r + 1}"

                            try:
                                if r < df1.shape[0] and c < df1.shape[1]: val1_str = str(df1.iloc[r, c])
                                else: val1_str = "[CELDA NO EXISTE]"
                            except IndexError: val1_str = "[ERROR LECTURA F1]"

                            try:
                                if r < df2.shape[0] and c < df2.shape[1]: val2_str = str(df2.iloc[r, c])
                                else: val2_str = "[CELDA NO EXISTE]"
                            except IndexError: val2_str = "[ERROR LECTURA F2]"

                            # Comparar los valores (como strings)
                            if val1_str != val2_str:
                                sheet_text.insert(tk.END, f"  - Celda {cell_ref}: '{val1_str}' (F1) != '{val2_str}' (F2)\n")
                                differences_found_in_sheet = True
                                cell_diff_count += 1

                    if not differences_found_in_sheet:
                         sheet_text.insert(tk.END, "  - Sin diferencias encontradas en el contenido.\n")
                    elif cell_diff_count == 0 and df1.shape != df2.shape:
                         # Caso donde solo difieren dimensiones pero no celdas (dentro del área común)
                         sheet_text.insert(tk.END, "  - No se encontraron diferencias en los valores de las celdas dentro del área común comparada.\n")


                except Exception as e_sheet:
                     sheet_text.insert(tk.END, f"\n*** Error al procesar esta pestaña '{sheet_name}' ***\n{e_sheet}\n")
                     differences_found_in_sheet = True # Marcar como diferencia si hubo error
                
                finally:
                    sheet_text.config(state=DISABLED) # Deshabilitar edición de esta pestaña

        # Mensaje final en la pestaña Resumen (opcional)
        summary_text.config(state=NORMAL)
        summary_text.insert(tk.END, "\nComparación completada.\n")
        summary_text.config(state=DISABLED)


    except Exception as e_global:
        # Mostrar error global en la pestaña Resumen si aún no existe o crearla si es necesario
        try:
            # Intentar escribir en la pestaña de resumen existente
            summary_text.config(state=NORMAL)
            summary_text.insert(tk.END, f"\n*** ERROR GENERAL DURANTE LA COMPARACIÓN ***\n{e_global}\n")
            summary_text.config(state=DISABLED)
        except tk.TclError: # Si summary_text no es válido (ej. error muy temprano)
             # Crear una pestaña de error si la de resumen falló antes de crearse
             error_text = add_report_tab(report_notebook, "ERROR")
             error_text.config(state=NORMAL)
             error_text.insert(tk.END, f"*** ERROR GENERAL DURANTE LA COMPARACIÓN ***\n{e_global}\n")
             error_text.config(state=DISABLED)
             
        messagebox.showerror("Error", f"Ocurrió un error al procesar los archivos: {e_global}")

    finally:
        # Asegurarse de cerrar los archivos si pandas los mantiene abiertos
        try:
            if xls1: xls1.close()
            if xls2: xls2.close()
        except Exception as e_close:
            print(f"Advertencia: no se pudieron cerrar los archivos Excel: {e_close}")


# --- Configuración de la GUI ---
root = tk.Tk()
root.title("Comparador de Archivos Excel")
root.geometry("750x650") # Aumentar tamaño para acomodar mejor las pestañas

# Frame para los controles de selección de archivos (sin cambios)
selection_frame = Frame(root, padx=10, pady=10)
selection_frame.pack(fill=X, side=TOP)
# --- Controles para Archivo 1 ---
file1_frame = Frame(selection_frame)
file1_frame.pack(side=LEFT, fill=X, expand=True, padx=5)
btn_select1 = Button(file1_frame, text="Seleccionar Archivo 1", command=select_file1)
btn_select1.pack(side=TOP, fill=X, pady=(0, 5))
file1_label = Label(file1_frame, text="Ningún archivo seleccionado", relief=SUNKEN, anchor=W, justify=LEFT, padx=5)
file1_label.pack(side=TOP, fill=X)
# --- Controles para Archivo 2 ---
file2_frame = Frame(selection_frame)
file2_frame.pack(side=RIGHT, fill=X, expand=True, padx=5)
btn_select2 = Button(file2_frame, text="Seleccionar Archivo 2", command=select_file2)
btn_select2.pack(side=TOP, fill=X, pady=(0, 5))
file2_label = Label(file2_frame, text="Ningún archivo seleccionado", relief=SUNKEN, anchor=W, justify=LEFT, padx=5)
file2_label.pack(side=TOP, fill=X)

# Botón de Comparación (sin cambios)
compare_button = Button(root, text="Comparar Archivos", command=compare_excel_files, height=2)
compare_button.pack(pady=10, fill=X, padx=10)

# --- Área de Reporte con Pestañas (Notebook) ---
# Crear el widget Notebook
report_notebook = ttk.Notebook(root)
report_notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

# No añadimos pestañas aquí inicialmente, se crearán dinámicamente
# al pulsar el botón "Comparar Archivos". Se podría crear una
# pestaña inicial vacía si se prefiere:
# initial_summary_text = add_report_tab(report_notebook, "Resumen General")
# initial_summary_text.insert(tk.END, "Selecciona archivos y pulsa 'Comparar Archivos'.")
# initial_summary_text.config(state=DISABLED)


# Iniciar el bucle principal de la GUI
root.mainloop()