import sys
import pyautogui
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit
)

class CommandExecutor(QWidget):
    """
    Una aplicación de interfaz gráfica para seleccionar un archivo de comandos y ejecutarlos.

    Args:
        QWidget (QWidget): El widget base de PyQt6.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Inicializa la interfaz de usuario de la aplicación.
        """
        self.setWindowTitle('Ejecutor de Comandos')
        self.setGeometry(300, 300, 400, 300)

        # Diseño principal
        layout = QVBoxLayout()

        # Botón para seleccionar archivo
        self.select_button = QPushButton('Seleccionar Archivo de Comandos')
        self.select_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_button)

        # Etiqueta para mostrar la ruta del archivo
        self.file_label = QLabel('Ningún archivo seleccionado')
        layout.addWidget(self.file_label)

        # Área de texto para mostrar los comandos
        self.command_view = QTextEdit()
        self.command_view.setReadOnly(True)
        layout.addWidget(self.command_view)

        # Botón para ejecutar los comandos
        self.run_button = QPushButton('Ejecutar Comandos')
        self.run_button.clicked.connect(self.execute_commands)
        self.run_button.setEnabled(False)  # Deshabilitado hasta que se seleccione un archivo
        layout.addWidget(self.run_button)

        self.setLayout(layout)

        self.file_path = None

    def open_file_dialog(self):
        """
        Abre un diálogo para seleccionar un archivo de texto plano.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos de Texto (*.txt)")
        if file_name:
            self.file_path = file_name
            self.file_label.setText(f'Archivo: {self.file_path}')
            self.run_button.setEnabled(True)
            self.display_file_content()

    def display_file_content(self):
        """
        Muestra el contenido del archivo seleccionado en el área de texto.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.command_view.setText(f.read())
        except Exception as e:
            self.command_view.setText(f"Error al leer el archivo:\n{e}")

    def execute_commands(self):
        """
        Lee y ejecuta los comandos del archivo seleccionado.
        """
        if not self.file_path:
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(',', 2)
                    command = parts[0].strip().lower()

                    if command == 'cursor' and len(parts) == 3:
                        try:
                            x = int(parts[1].strip())
                            y = int(parts[2].strip())
                            pyautogui.moveTo(x, y, duration=0.25)
                            print(f"Moviendo cursor a: ({x}, {y})")
                        except ValueError:
                            print(f"Error: Coordenadas inválidas en la línea: {line}")

                    elif command == 'texto' and len(parts) == 2:
                        text_to_type = parts[1].strip().strip('"')
                        pyautogui.write(text_to_type)
                        print(f"Escribiendo texto: {text_to_type}")

                    elif command == 'return':
                        pyautogui.press('enter')
                        print("Pulsando tecla: Enter")
                    # --- NUEVO COMANDO AÑADIDO ---
                    elif command == 'click':
                        pyautogui.click()
                        print("Haciendo click izquierdo")
                    # ---------------------------
                    else:
                        print(f"Comando desconocido o mal formado: {line}")
                    
                    # Pequeña pausa entre comandos para evitar problemas
                    time.sleep(0.1)

        except Exception as e:
            print(f"Ocurrió un error al ejecutar los comandos: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    executor = CommandExecutor()
    executor.show()
    sys.exit(app.exec())