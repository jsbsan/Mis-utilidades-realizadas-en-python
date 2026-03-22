import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os
import difflib

def select_file():
    filepath = filedialog.askopenfilename(
        title="Seleccionar fichero Markdown",
        filetypes=(("Archivos Markdown", "*.md"), ("Todos los archivos", "*.*"))
    )
    if filepath:
        file_var.set(filepath)

def select_directory():
    dirpath = filedialog.askdirectory(title="Seleccionar directorio de búsqueda")
    if dirpath:
        dir_var.set(dirpath)

def extract_list_from_md(filepath):
    """Lee el archivo MD y extrae los elementos, identificando si ya son enlaces."""
    list_items = []
    # Regex para capturar el contenido de la línea de lista
    regex = r'^\s*[-*+]\s+(.*)|^\s*\d+\.\s+(.*)'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(regex, line)
                if match:
                    content = match.group(1) if match.group(1) else match.group(2)
                    content = content.strip()
                    
                    # Verificamos si el contenido YA es un enlace Markdown [texto](url)
                    is_already_link = bool(re.search(r'^\[.*\]\(.*\)$', content))
                    
                    list_items.append({
                        'raw': line.strip(), # Guardamos la línea original por si acaso
                        'text': content,
                        'skip': is_already_link
                    })
    except Exception as e:
        log_message(f"Error al leer el archivo: {e}")
    return list_items

def find_similar_file(item_name, files_list):
    matches = difflib.get_close_matches(item_name, files_list, n=1, cutoff=0.4)
    if matches:
        return matches[0]
    
    for f in files_list:
        if item_name.lower() in f.lower():
            return f
    return None

def log_message(msg):
    log_box.configure(state='normal')
    log_box.insert(tk.END, msg + "\n")
    log_box.configure(state='disabled')
    log_box.see(tk.END)
    root.update_idletasks()

def process_files():
    md_file = file_var.get()
    search_dir = dir_var.get()

    if not md_file or not search_dir:
        messagebox.showwarning("Atención", "Selecciona el archivo MD y el directorio.")
        return

    log_box.configure(state='normal')
    log_box.delete('1.0', tk.END)
    log_box.configure(state='disabled')

    try:
        items = extract_list_from_md(md_file)
        if not items:
            log_message("⚠️ No se encontraron elementos de lista.")
            return

        all_files = [f for f in os.listdir(search_dir) if os.path.isfile(os.path.join(search_dir, f))]
        output_file = os.path.join(os.path.dirname(md_file), "resultado_enlazado.md")
        
        log_message(f"--- Procesando {len(items)} elementos ---\n")

        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write("# Lista Enlazada Generada\n\n")
            
            for item_data in items:
                # Caso 1: Ya es un enlace, lo escribimos tal cual
                if item_data['skip']:
                    out_f.write(f"- {item_data['text']}\n")
                    log_message(f"ℹ️ Ignorado (ya es enlace): {item_data['text'][:30]}...")
                    continue
                
                # Caso 2: Es texto plano, buscamos fichero
                item_text = item_data['text']
                matched_file = find_similar_file(item_text, all_files)
                
                if matched_file:
                    link_path = os.path.join(search_dir, matched_file).replace('\\', '/').replace(' ', '%20')
                    out_f.write(f"- [{item_text}]({link_path})\n")
                    log_message(f"✅ Enlazado: \"{item_text}\" ➔ {matched_file}")
                else:
                    out_f.write(f"- {item_text}\n")
                    log_message(f"❌ Sin coincidencia: \"{item_text}\"")
        
        log_message(f"\n--- Proceso finalizado ---")
        messagebox.showinfo("Éxito", f"Archivo generado:\n{output_file}")

    except Exception as e:
        log_message(f"ERROR: {str(e)}")
        messagebox.showerror("Error", str(e))

# --- INTERFAZ ---
root = tk.Tk()
root.title("Enlazador Inteligente de Markdown")
root.geometry("650x550")

file_var, dir_var = tk.StringVar(), tk.StringVar()
main_frame = tk.Frame(root, padx=20, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# UI Elements
tk.Label(main_frame, text="1. Archivo Markdown Origen:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
f_frame = tk.Frame(main_frame); f_frame.pack(fill=tk.X, pady=(0, 10))
tk.Entry(f_frame, textvariable=file_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
tk.Button(f_frame, text="Buscar", command=select_file).pack(side=tk.RIGHT)

tk.Label(main_frame, text="2. Directorio de Archivos destino:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
d_frame = tk.Frame(main_frame); d_frame.pack(fill=tk.X, pady=(0, 10))
tk.Entry(d_frame, textvariable=dir_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
tk.Button(d_frame, text="Buscar", command=select_directory).pack(side=tk.RIGHT)

tk.Button(main_frame, text="GENERAR MARKDOWN ENLAZADO", command=process_files, 
          bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill=tk.X, pady=10)

log_box = scrolledtext.ScrolledText(main_frame, height=15, state='disabled', font=("Consolas", 9), bg="#f4f4f4")
log_box.pack(fill=tk.BOTH, expand=True)

root.mainloop()