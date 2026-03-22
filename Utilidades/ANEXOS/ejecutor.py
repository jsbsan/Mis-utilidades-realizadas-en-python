import tkinter as tk
from tkinter import scrolledtext, messagebox
import logging
import sys
import io
import traceback
import datetime

class TextHandler(logging.Handler):
    """
    Clase personalizada para redirigir los logs de Python
    al widget de texto de la interfaz gráfica (ScrolledText).
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            # Insertar el log al final
            self.text_widget.insert(tk.END, msg + '\n')
            # Hacer scroll automático hacia abajo
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        
        # Asegurarse de actualizar la GUI en el hilo principal
        self.text_widget.after(0, append)

class PythonRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ejecutor de Scripts Python con Logging")
        self.root.geometry("800x600")

        # --- Configuración del Layout ---
        
        # 1. Etiqueta y Área de Entrada de Código
        lbl_input = tk.Label(root, text="Escribe o pega tu código Python aquí:", font=("Arial", 10, "bold"))
        lbl_input.pack(pady=(10, 0), anchor="w", padx=10)

        self.code_input = scrolledtext.ScrolledText(root, height=15, font=("Consolas", 10))
        self.code_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Código de ejemplo por defecto
        default_code = (
            "# Ejemplo de código\n"
            "import time\n\n"
            "print('Iniciando proceso...')\n"
            "for i in range(3):\n"
            "    print(f'Procesando elemento {i+1}')\n"
            "print('Proceso finalizado con éxito.')"
        )
        self.code_input.insert(tk.END, default_code)

        # 2. Botonera
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_run = tk.Button(btn_frame, text="▶ Ejecutar Código", bg="#4CAF50", fg="white", 
                                 font=("Arial", 11, "bold"), command=self.ejecutar_codigo)
        self.btn_run.pack(side=tk.LEFT, padx=5)

        # Botón nuevo para Borrar y Pegar
        self.btn_paste = tk.Button(btn_frame, text="📋 Borrar y Pegar", 
                                   command=self.pegar_desde_portapapeles)
        self.btn_paste.pack(side=tk.LEFT, padx=5)

        self.btn_clear_log = tk.Button(btn_frame, text="Limpiar Logs", command=self.limpiar_logs)
        self.btn_clear_log.pack(side=tk.RIGHT, padx=5)

        # 3. Etiqueta y Área de Logs/Salida
        lbl_output = tk.Label(root, text="Logs del Sistema y Salida:", font=("Arial", 10, "bold"))
        lbl_output.pack(pady=(10, 0), anchor="w", padx=10)

        self.log_output = scrolledtext.ScrolledText(root, height=12, state='disabled', bg="#f0f0f0", font=("Consolas", 9))
        self.log_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # --- Configuración del Logger ---
        self.setup_logging()

    def setup_logging(self):
        """Configura el sistema de logging para escribir en la GUI."""
        self.logger = logging.getLogger("GuiLogger")
        self.logger.setLevel(logging.INFO)

        # Formato del log: [HORA] [NIVEL] Mensaje
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

        # Crear nuestro handler personalizado y añadirlo
        gui_handler = TextHandler(self.log_output)
        gui_handler.setFormatter(formatter)
        self.logger.addHandler(gui_handler)

        self.logger.info("Sistema listo. Esperando código...")

    def limpiar_logs(self):
        """Limpia el área de logs."""
        self.log_output.configure(state='normal')
        self.log_output.delete(1.0, tk.END)
        self.log_output.configure(state='disabled')
        self.logger.info("Logs limpiados.")

    def pegar_desde_portapapeles(self):
        """Borra el código actual y pega el contenido del portapapeles si existe."""
        # 1. Borrar contenido actual
        self.code_input.delete("1.0", tk.END)
        
        try:
            # 2. Intentar obtener texto del portapapeles
            texto = self.root.clipboard_get()
            self.code_input.insert(tk.END, texto)
            self.logger.info("Código reemplazado con el contenido del portapapeles.")
        except tk.TclError:
            # Si el portapapeles está vacío o no tiene texto, solo avisamos en el log
            self.logger.warning("Portapapeles vacío o sin texto válido. El editor se ha limpiado.")

    def ejecutar_codigo(self):
        """Toma el código del input y lo ejecuta capturando stdout."""
        codigo = self.code_input.get("1.0", tk.END).strip()
        
        if not codigo:
            messagebox.showwarning("Advertencia", "El área de código está vacía.")
            return

        self.logger.info("-" * 30)
        self.logger.info("Iniciando ejecución del script...")

        # Capturamos stdout (prints) para redirigirlos a nuestro logger o variable
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            # --- ZONA DE PELIGRO: Ejecución de código dinámico ---
            # Se crea un diccionario local para mantener el scope limpio
            local_scope = {}
            exec(codigo, {}, local_scope)
            # -----------------------------------------------------

            # Recuperar lo que se haya impreso con print()
            salida = redirected_output.getvalue()
            if salida:
                # Logueamos la salida línea por línea para que se vea ordenado
                for linea in salida.strip().split('\n'):
                    self.logger.info(f"[STDOUT] {linea}")
            else:
                self.logger.info("El código se ejecutó pero no generó salida (print).")

            self.logger.info("Ejecución finalizada correctamente.")

        except Exception as e:
            # Si el código falla, capturamos el error completo
            self.logger.error("Error durante la ejecución:")
            # Obtenemos el traceback (la pila de errores)
            error_details = traceback.format_exc()
            self.logger.error(f"\n{error_details.strip()}")

        finally:
            # Restaurar stdout original para no romper la consola del sistema
            sys.stdout = old_stdout

if __name__ == "__main__":
    root = tk.Tk()
    app = PythonRunnerApp(root)
    root.mainloop()