import os

# --- CONFIGURACIÓN DE PRIVACIDAD Y MODO OFFLINE ---
os.environ['TRANSFORMERS_OFFLINE'] = '1'

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
from sentence_transformers import SentenceTransformer, util
import torch

# --- CARGA DEL MODELO ---
try:
    print("Cargando modelo de IA local...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    print("Modelo no detectado. Conectando para descarga inicial...")
    os.environ['TRANSFORMERS_OFFLINE'] = '0'
    model = SentenceTransformer('all-MiniLM-L6-v2')
    os.environ['TRANSFORMERS_OFFLINE'] = '1'

# Categorías para el etiquetado semántico
CANDIDATE_TAGS = [
    "Factura", "Contrato", "Imagen", "Guion", "Codigo", 
    "Personal", "Trabajo", "Estudios", "Receta", "Manual",
    "Configuracion", "Audio", "Video", "Backup", "Importante","WINDOWS","PDF","EXCEL","WORD","OBSIDIAN"
]
TAG_EMBEDDINGS = model.encode(CANDIDATE_TAGS, convert_to_tensor=True)

def extract_list_from_md(filepath):
    list_items = []
    regex = r'^\s*[-*+]\s+(.*)|^\s*\d+\.\s+(.*)'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(regex, line)
                if match:
                    content = (match.group(1) or match.group(2)).strip()
                    is_already_link = bool(re.search(r'^\[.*\]\(.*\)$', content))
                    list_items.append({'text': content, 'skip': is_already_link})
    except Exception as e:
        log_message(f"❌ Error al leer archivo: {e}")
    return list_items

def get_tags_for_file(filename):
    file_emb = model.encode(filename, convert_to_tensor=True)
    scores = util.cos_sim(file_emb, TAG_EMBEDDINGS)[0]
    top_indices = torch.topk(scores, k=2).indices
    tags = [CANDIDATE_TAGS[i] for i in top_indices if scores[i] > 0.35]
    return " ".join([f"#{t.lower()}" for t in tags])

def find_best_match_ai(item_name, files_list, threshold):
    """Búsqueda semántica usando el umbral definido por el slider."""
    if not files_list: return None, 0
    item_emb = model.encode(item_name, convert_to_tensor=True)
    files_emb = model.encode(files_list, convert_to_tensor=True)
    scores = util.cos_sim(item_emb, files_emb)[0]
    best_idx = torch.argmax(scores).item()
    best_score = scores[best_idx].item()
    
    return (files_list[best_idx], best_score) if best_score >= threshold else (None, best_score)

def log_message(msg):
    log_box.configure(state='normal')
    log_box.insert(tk.END, msg + "\n")
    log_box.configure(state='disabled')
    log_box.see(tk.END)
    root.update_idletasks()

def process_files():
    md_file, search_dir = file_var.get(), dir_var.get()
    threshold = threshold_slider.get() # Obtenemos el valor del Slider

    if not md_file or not search_dir:
        messagebox.showwarning("Atención", "Por favor, selecciona el archivo y la carpeta.")
        return

    log_box.configure(state='normal'); log_box.delete('1.0', tk.END); log_box.configure(state='disabled')
    
    try:
        items = extract_list_from_md(md_file)
        if not items:
            log_message("⚠️ No se encontraron listas.")
            return

        all_files = [f for f in os.listdir(search_dir) if os.path.isfile(os.path.join(search_dir, f))]
        output_path = os.path.join(os.path.dirname(md_file), "resultado_ia_ajustable.md")
        
        log_message(f"🚀 Iniciando proceso (Umbral: {threshold})...")

        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(f"# Reporte IA (Umbral confianza: {threshold})\n\n")
            for item in items:
                if item['skip']:
                    out_f.write(f"- {item['text']}\n")
                    continue

                matched_file, score = find_best_match_ai(item['text'], all_files, threshold)
                
                if matched_file:
                    tags = get_tags_for_file(matched_file)
                    clean_path = os.path.join(search_dir, matched_file).replace('\\', '/').replace(' ', '%20')
                    out_f.write(f"- [{item['text']}]({clean_path}) {tags}\n")
                    log_message(f"✅ ({score:.2f}): {item['text']} ➔ {matched_file}")
                else:
                    out_f.write(f"- {item['text']}\n")
                    log_message(f"❓ Debajo del umbral ({score:.2f}): {item['text']}")

        messagebox.showinfo("Completado", f"Generado en:\n{output_path}")
    except Exception as e:
        log_message(f"🚨 Error: {str(e)}")

# --- INTERFAZ UI ---
root = tk.Tk()
root.title("AI Markdown Linker Pro")
root.geometry("800x700")

file_var, dir_var = tk.StringVar(), tk.StringVar()
main_frame = tk.Frame(root, padx=25, pady=20); main_frame.pack(fill=tk.BOTH, expand=True)

# 1. Archivos
tk.Label(main_frame, text="Fichero Markdown (.md):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
f_frame = tk.Frame(main_frame); f_frame.pack(fill=tk.X, pady=(2, 10))
tk.Entry(f_frame, textvariable=file_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(f_frame, text="Buscar", command=lambda: file_var.set(filedialog.askopenfilename())).pack(side=tk.RIGHT, padx=5)

tk.Label(main_frame, text="Carpeta de búsqueda:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
d_frame = tk.Frame(main_frame); d_frame.pack(fill=tk.X, pady=(2, 10))
tk.Entry(d_frame, textvariable=dir_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(d_frame, text="Buscar", command=lambda: dir_var.set(filedialog.askdirectory())).pack(side=tk.RIGHT, padx=5)

# 2. Slider de Umbral (Novedad)
tk.Label(main_frame, text="Ajuste de Confianza IA (Umbral):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(10, 0))
threshold_slider = tk.Scale(main_frame, from_=0.10, to=0.90, resolution=0.01, orient=tk.HORIZONTAL, length=400)
threshold_slider.set(0.45) # Valor inicial recomendado
threshold_slider.pack(anchor=tk.W)

help_text = ("💡 Ayuda: Sube a 0.60 para que solo enlace si está muy segura.\n"
             "Baja a 0.30 si tus nombres de archivo son muy caóticos y quieres que la IA arriesgue más.")
tk.Label(main_frame, text=help_text, font=("Segoe UI", 8, "italic"), justify=tk.LEFT, fg="#555").pack(anchor=tk.W, pady=(0, 15))

# 3. Botón y Log
tk.Button(main_frame, text="EJECUTAR PROCESO", command=process_files, 
          bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), pady=10).pack(fill=tk.X, pady=10)

log_box = scrolledtext.ScrolledText(main_frame, height=15, state='disabled', bg="#1e1e1e", fg="#33ff33", font=("Consolas", 9))
log_box.pack(fill=tk.BOTH, expand=True)

root.mainloop()