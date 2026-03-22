import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os
from sentence_transformers import SentenceTransformer, util
import torch

# Cargamos el modelo de IA (se descarga la primera vez que lo uses)
# 'all-MiniLM-L6-v2' es rápido y excelente para comparaciones cortas
print("Cargando modelo de lenguaje...")
model = SentenceTransformer('all-MiniLM-L6-v2')

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
        log_message(f"Error: {e}")
    return list_items

def find_best_match_ai(item_name, files_list):
    """Utiliza IA para encontrar el archivo con mayor similitud semántica."""
    if not files_list: return None, 0
    
    # 1. Convertimos el ítem y la lista de archivos a vectores (embeddings)
    item_embedding = model.encode(item_name, convert_to_tensor=True)
    files_embeddings = model.encode(files_list, convert_to_tensor=True)
    
    # 2. Calculamos la similitud de coseno entre el ítem y todos los archivos
    cosine_scores = util.cos_sim(item_embedding, files_embeddings)[0]
    
    # 3. Buscamos el índice con la puntuación más alta
    best_idx = torch.argmax(cosine_scores).item()
    best_score = cosine_scores[best_idx].item()
    
    # Umbral de confianza: si es menor a 0.45, probablemente no sea el mismo archivo
    if best_score > 0.45:
        return files_list[best_idx], best_score
    return None, best_score

def log_message(msg):
    log_box.configure(state='normal')
    log_box.insert(tk.END, msg + "\n")
    log_box.configure(state='disabled')
    log_box.see(tk.END)
    root.update_idletasks()

def process_files():
    md_file, search_dir = file_var.get(), dir_var.get()
    if not md_file or not search_dir:
        messagebox.showwarning("Atención", "Selecciona archivo y carpeta.")
        return

    log_box.configure(state='normal'); log_box.delete('1.0', tk.END); log_box.configure(state='disabled')
    
    try:
        items = extract_list_from_md(md_file)
        all_files = [f for f in os.listdir(search_dir) if os.path.isfile(os.path.join(search_dir, f))]
        output_file = os.path.join(os.path.dirname(md_file), "resultado_ia_enlazado.md")
        
        log_message("🧠 Usando IA para analizar similitudes...")

        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write("# Lista Enlazada por IA\n\n")
            for item in items:
                if item['skip']:
                    out_f.write(f"- {item['text']}\n")
                    log_message(f"ℹ️ Omitido: {item['text'][:20]}...")
                    continue

                matched_file, score = find_best_match_ai(item['text'], all_files)
                
                if matched_file:
                    link = os.path.join(search_dir, matched_file).replace('\\', '/').replace(' ', '%20')
                    out_f.write(f"- [{item['text']}]({link})\n")
                    log_message(f"✅ AI ({score:.2f}): {item['text']} -> {matched_file}")
                else:
                    out_f.write(f"- {item['text']}\n")
                    log_message(f"❌ No match seguro para: {item['text']}")

        messagebox.showinfo("Éxito", "Procesamiento con IA finalizado.")
    except Exception as e:
        log_message(f"Error: {e}")

# --- Interfaz (Misma estructura anterior con ligeros ajustes) ---
root = tk.Tk(); root.title("Markdown AI Linker"); root.geometry("700x550")
file_var, dir_var = tk.StringVar(), tk.StringVar()
main_frame = tk.Frame(root, padx=20, pady=10); main_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(main_frame, text="1. Archivo MD:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
f_frame = tk.Frame(main_frame); f_frame.pack(fill=tk.X)
tk.Entry(f_frame, textvariable=file_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(f_frame, text="...", command=lambda: file_var.set(filedialog.askopenfilename())).pack(side=tk.RIGHT)

tk.Label(main_frame, text="2. Carpeta:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10,0))
d_frame = tk.Frame(main_frame); d_frame.pack(fill=tk.X)
tk.Entry(d_frame, textvariable=dir_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(d_frame, text="...", command=lambda: dir_var.set(filedialog.askdirectory())).pack(side=tk.RIGHT)

tk.Button(main_frame, text="PROCESAR CON INTELIGENCIA ARTIFICIAL", command=process_files, bg="#3498db", fg="white", font=("Arial", 10, "bold"), pady=10).pack(fill=tk.X, pady=20)
log_box = scrolledtext.ScrolledText(main_frame, height=15, state='disabled', bg="#2c3e50", fg="#ecf0f1", font=("Consolas", 9))
log_box.pack(fill=tk.BOTH, expand=True)
root.mainloop()