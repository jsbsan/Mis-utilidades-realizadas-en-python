import tkinter as tk
from tkinter import scrolledtext, Label, Button, Frame, messagebox, filedialog, ttk
from tkinter import BOTH, X, Y, LEFT, RIGHT, TOP, BOTTOM, SUNKEN, W, E, DISABLED, NORMAL
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
import os

# Variables globales
file1_path = None
file2_path = None

# --- NUEVO: Diccionario para guardar referencias a los widgets de texto ---
# Esto soluciona el problema de que no encuentre el contenido al guardar
tab_widgets = {} 

def update_file_label(label_widget, file_path):
    """Actualiza la etiqueta para mostrar el archivo seleccionado."""
    if file_path:
        label_widget.config(text=f"Archivo: {os.path.basename(file_path)}")
    else:
        label_widget.config(text="Ningún archivo seleccionado")

# --- Funciones para Seleccionar Archivos ---

def select_file1():
    global file1_path
    filetypes = [("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    filepath = filedialog.askopenfilename(title="Seleccionar Archivo Excel 1", filetypes=filetypes)
    if filepath:
        file1_path = filepath
        update_file_label(file1_label, file1_path)

def select_file2():
    global file2_path
    filetypes = [("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
    filepath = filedialog.askopenfilename(title="Seleccionar Archivo Excel 2", filetypes=filetypes)
    if filepath:
        file2_path = filepath
        update_file_label(file2_label, file2_path)

# --- Lógica de Comparación ---

def clear_notebook_tabs(notebook):
    """Elimina todas las pestañas de un widget Notebook y limpia el diccionario."""
    # Limpiar el diccionario de widgets guardados
    tab_widgets.clear()
    
    while True:
        try:
            notebook.forget(notebook.tabs()[0])
        except IndexError:
            break

def add_report_tab(notebook, title):
    """Crea una nueva pestaña con un ScrolledText, la registra y la devuelve."""
    tab_frame = Frame(notebook, padx=5, pady=5)
    notebook.add(tab_frame, text=title)
    
    report_widget = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, state=DISABLED)
    report_widget.pack(fill=BOTH, expand=True)
    
    # --- CORRECCIÓN CLAVE ---
    # Guardamos la referencia usando el ID (nombre interno) del frame de la pestaña
    # str(tab_frame) nos da el ID único que usa el notebook.tabs()
    tab_widgets[str(tab_frame)] = report_widget
    
    return report_widget

# --- FUNCIONALIDAD CORREGIDA: Guardar Reporte ---
def save_report():
    """Recopila el texto de todas las pestañas y lo guarda en un .txt"""
    
    # Verificar si hay pestañas (usando nuestro diccionario)
    if not tab_widgets:
        messagebox.showwarning("Advertencia", "No hay ningún reporte generado para guardar. Por favor, compara los archivos primero.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
        title="Guardar Reporte de Diferencias"
    )

    if not file_path:
        return 

    try:
        full_content = ""
        
        # Iterar sobre las pestañas en el orden visual que tienen en el Notebook
        # notebook.tabs() devuelve una lista de strings (IDs de los frames)
        for tab_id in report_notebook.tabs():
            
            # Obtener el título
            tab_title = report_notebook.tab(tab_id, "text")
            
            full_content += f"\n{'='*50}\nREPORTE: {tab_title}\n{'='*50}\n"
            
            # --- CORRECCIÓN: Recuperar el widget directamente del diccionario ---
            if tab_id in tab_widgets:
                text_widget = tab_widgets[tab_id]
                # Extraer texto. "1.0" es fila 1 col 0, tk.END es el final.
                text_content = text_widget.get("1.0", tk.END)
                full_content += text_content
            else:
                full_content += "[Error: No se pudo recuperar el contenido de esta pestaña]\n"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)
            
        messagebox.showinfo("Éxito", f"Reporte guardado exitosamente en:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")

# ---------------------------------------------

def compare_excel_files():
    """Función principal para comparar los dos archivos Excel seleccionados."""
    if not file1_path or not file2_path:
        messagebox.showwarning("Advertencia", "Por favor, selecciona ambos archivos Excel antes de comparar.")
        return

    clear_notebook_tabs(report_notebook)

    summary_text = add_report_tab(report_notebook, "Resumen General")
    summary_text.config(state=NORMAL)

    summary_text.insert(tk.END, f"Comparando Archivo 1: {os.path.basename(file1_path)}\n")
    summary_text.insert(tk.END, f"Comparando Archivo 2: {os.path.basename(file2_path)}\n")
    summary_text.insert(tk.END, "="*40 + "\n\n")

    xls1 = None
    xls2 = None

    try:
        xls1 = pd.ExcelFile(file1_path)
        xls2 = pd.ExcelFile(file2_path)
        sheets1 = set(xls1.sheet_names)
        sheets2 = set(xls2.sheet_names)

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
        summary_text.config(state=DISABLED)

        if not common_sheets:
             summary_text.config(state=NORMAL)
             summary_text.insert(tk.END, "\nNo hay pestañas comunes para comparar contenido.\n")
             summary_text.config(state=DISABLED)
        else:
            for sheet_name in sorted(list(common_sheets)):
                sheet_text = add_report_tab(report_notebook, sheet_name)
                sheet_text.config(state=NORMAL)
                
                sheet_text.insert(tk.END, f"--- Comparando Pestaña: '{sheet_name}' ---\n\n")
                
                try:
                    df1 = pd.read_excel(xls1, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)
                    df2 = pd.read_excel(xls2, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)

                    differences_found_in_sheet = False

                    if df1.shape != df2.shape:
                        sheet_text.insert(tk.END, f"  - Diferencia de dimensiones: Archivo 1 ({df1.shape[0]}x{df1.shape[1]}) vs Archivo 2 ({df2.shape[0]}x{df2.shape[1]})\n")
                        differences_found_in_sheet = True

                    max_rows = max(df1.shape[0], df2.shape[0])
                    max_cols = max(df1.shape[1], df2.shape[1])
                    cell_diff_count = 0

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

                            if val1_str != val2_str:
                                sheet_text.insert(tk.END, f"  - Celda {cell_ref}: '{val1_str}' (F1) != '{val2_str}' (F2)\n")
                                differences_found_in_sheet = True
                                cell_diff_count += 1

                    if not differences_found_in_sheet:
                         sheet_text.insert(tk.END, "  - Sin diferencias encontradas en el contenido.\n")
                    elif cell_diff_count == 0 and df1.shape != df2.shape:
                         sheet_text.insert(tk.END, "  - No se encontraron diferencias en los valores de las celdas dentro del área común comparada.\n")


                except Exception as e_sheet:
                     sheet_text.insert(tk.END, f"\n*** Error al procesar esta pestaña '{sheet_name}' ***\n{e_sheet}\n")
                
                finally:
                    sheet_text.config(state=DISABLED)

        summary_text.config(state=NORMAL)
        summary_text.insert(tk.END, "\nComparación completada.\n")
        summary_text.config(state=DISABLED)


    except Exception as e_global:
        try:
            summary_text.config(state=NORMAL)
            summary_text.insert(tk.END, f"\n*** ERROR GENERAL DURANTE LA COMPARACIÓN ***\n{e_global}\n")
            summary_text.config(state=DISABLED)
        except tk.TclError:
             error_text = add_report_tab(report_notebook, "ERROR")
             error_text.config(state=NORMAL)
             error_text.insert(tk.END, f"*** ERROR GENERAL DURANTE LA COMPARACIÓN ***\n{e_global}\n")
             error_text.config(state=DISABLED)
             
        messagebox.showerror("Error", f"Ocurrió un error al procesar los archivos: {e_global}")

    finally:
        try:
            if xls1: xls1.close()
            if xls2: xls2.close()
        except Exception as e_close:
            print(f"Advertencia: no se pudieron cerrar los archivos Excel: {e_close}")


# --- Configuración de la GUI ---
root = tk.Tk()
root.title("Comparador de Archivos Excel")
root.geometry("750x650")

selection_frame = Frame(root, padx=10, pady=10)
selection_frame.pack(fill=X, side=TOP)

file1_frame = Frame(selection_frame)
file1_frame.pack(side=LEFT, fill=X, expand=True, padx=5)
btn_select1 = Button(file1_frame, text="Seleccionar Archivo 1", command=select_file1)
btn_select1.pack(side=TOP, fill=X, pady=(0, 5))
file1_label = Label(file1_frame, text="Ningún archivo seleccionado", relief=SUNKEN, anchor=W, justify=LEFT, padx=5)
file1_label.pack(side=TOP, fill=X)

file2_frame = Frame(selection_frame)
file2_frame.pack(side=RIGHT, fill=X, expand=True, padx=5)
btn_select2 = Button(file2_frame, text="Seleccionar Archivo 2", command=select_file2)
btn_select2.pack(side=TOP, fill=X, pady=(0, 5))
file2_label = Label(file2_frame, text="Ningún archivo seleccionado", relief=SUNKEN, anchor=W, justify=LEFT, padx=5)
file2_label.pack(side=TOP, fill=X)

# --- Frame para Botones de Acción ---
action_frame = Frame(root, padx=10, pady=10)
action_frame.pack(fill=X)

# Botón de Comparación
compare_button = Button(action_frame, text="Comparar Archivos", command=compare_excel_files, height=2, bg="#dddddd")
compare_button.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

# --- Botón: Guardar Reporte ---
save_button = Button(action_frame, text="Guardar Reporte en TXT", command=save_report, height=2, bg="#cceeff")
save_button.pack(side=RIGHT, fill=X, expand=True, padx=(5, 0))
# -------------------------------------

report_notebook = ttk.Notebook(root)
report_notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

root.mainloop()