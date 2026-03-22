import sys
import subprocess
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLineEdit, QTextEdit, QLabel)
from PySide6.QtCore import QThread, Signal, Qt

# Hilo secundario para no bloquear la interfaz
class WorkerInstalador(QThread):
    # Señales para enviar datos desde el hilo a la interfaz
    progreso = Signal(str)
    finalizado = Signal(bool)

    def __init__(self, libreria):
        super().__init__()
        self.libreria = libreria

    def run(self):
        try:
            # Ejecutamos pip y leemos la salida estándar (stdout) y errores (stderr)
            proceso = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", self.libreria],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Leemos línea por línea mientras el proceso corre
            for linea in proceso.stdout:
                self.progreso.emit(linea.strip())
            
            proceso.wait()
            self.finalizado.emit(proceso.returncode == 0)
        except Exception as e:
            self.progreso.emit(f"Error crítico: {str(e)}")
            self.finalizado.emit(False)

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Instalador Python con Qt6")
        self.resize(500, 400)
        layout = QVBoxLayout()

        # Info Versión
        self.lbl_version = QLabel(f"<b>Python Detectado:</b> {sys.version.split()[0]}")
        layout.addWidget(self.lbl_version)

        # Input
        self.input_lib = QLineEdit()
        self.input_lib.setPlaceholderText("Nombre de la librería...")
        layout.addWidget(self.input_lib)

        # Botón
        self.btn_instalar = QPushButton("Instalar")
        self.btn_instalar.clicked.connect(self.iniciar_instalacion)
        layout.addWidget(self.btn_instalar)

        # Consola de salida
        self.consola = QTextEdit()
        self.consola.setReadOnly(True)
        self.consola.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace;")
        layout.addWidget(self.consola)

        self.setLayout(layout)

    def iniciar_instalacion(self):
        libreria = self.input_lib.text().strip()
        if not libreria:
            return

        self.consola.append(f"--- Iniciando instalación de {libreria} ---")
        self.btn_instalar.setEnabled(False) # Bloqueamos el botón para evitar clics dobles

        # Creamos y lanzamos el hilo
        self.worker = WorkerInstalador(libreria)
        self.worker.progreso.connect(self.actualizar_consola)
        self.worker.finalizado.connect(self.finalizar_proceso)
        self.worker.start()

    def actualizar_consola(self, texto):
        self.consola.append(texto)
        # Scroll automático hacia abajo
        self.consola.verticalScrollBar().setValue(self.consola.verticalScrollBar().maximum())

    def finalizar_proceso(self, exito):
        self.btn_instalar.setEnabled(True)
        mensaje = "\n✅ Instalación completada con éxito." if exito else "\n❌ Hubo un error en la instalación."
        self.consola.append(mensaje)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())