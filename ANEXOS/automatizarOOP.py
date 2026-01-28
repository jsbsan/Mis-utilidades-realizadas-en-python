import sys
import pyautogui
import time
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit
)

# ===================================================================
# 1. INTERFAZ DEL PATRÓN COMANDO (Command)
# ===================================================================
class Comando(ABC):
    """
    La interfaz del Comando declara un método para ejecutar una operación.
    """
    @abstractmethod
    def execute(self) -> None:
        pass

# ===================================================================
# 2. COMANDOS CONCRETOS (Concrete Commands)
# ===================================================================
class CursorCommand(Comando):
    """ Mueve el cursor del ratón a una posición específica. """
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def execute(self) -> None:
        pyautogui.moveTo(self._x, self._y, duration=0.25)
        print(f"Moviendo cursor a: ({self._x}, {self._y})")

class TextoCommand(Comando):
    """ Escribe un texto usando el teclado. """
    def __init__(self, text: str):
        self._text = text

    def execute(self) -> None:
        pyautogui.write(self._text, interval=0.05)
        print(f"Escribiendo texto: {self._text}")

class ReturnCommand(Comando):
    """ Presiona la tecla Enter/Return. """
    def execute(self) -> None:
        pyautogui.press('enter')
        print("Pulsando tecla: Enter")

class ClickCommand(Comando):
    """ Realiza un click izquierdo del ratón. """
    def execute(self) -> None:
        pyautogui.click()
        print("Haciendo click izquierdo")

class EsperaCommand(Comando):
    """ Pausa la ejecución por un número de segundos. """
    def __init__(self, duration: float):
        self._duration = duration

    def execute(self) -> None:
        print(f"Esperando durante {self._duration} segundos...")
        time.sleep(self._duration)

class InvalidCommand(Comando):
    """ Comando para líneas mal formadas o desconocidas. """
    def __init__(self, line: str):
        self._line = line

    def execute(self) -> None:
        print(f"Comando desconocido o mal formado: {self._line}")

# ===================================================================
# 3. CLIENTE / PARSER - Crea los objetos comando
# ===================================================================
def parse_line_to_command(line: str) -> Comando:
    """
    Analiza una línea de texto y devuelve el objeto Comando correspondiente.
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split(',', 2)
    command_name = parts[0].strip().lower()

    try:
        if command_name == 'cursor' and len(parts) == 3:
            x = int(parts[1].strip())
            y = int(parts[2].strip())
            return CursorCommand(x, y)
        elif command_name == 'texto' and len(parts) == 2:
            text_to_type = parts[1].strip().strip('"')
            return TextoCommand(text_to_type)
        elif command_name == 'return':
            return ReturnCommand()
        elif command_name == 'click':
            return ClickCommand()
        elif command_name == 'espera' and len(parts) >= 2:
            duration = float(parts[1].strip())
            return EsperaCommand(duration)
        else:
            return InvalidCommand(line)
    except (ValueError, IndexError):
        # Captura errores si los parámetros no son del tipo correcto o faltan
        return InvalidCommand(line)

# ===================================================================
# 4. INVOCADOR (Invoker) - La clase de la GUI
# ===================================================================
class CommandExecutor(QWidget):
    """
    La GUI que actúa como Invocador. Lee el archivo y ejecuta los
    objetos comando sin conocer los detalles de su implementación.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Ejecutor de Comandos (Patrón Comando)')
        self.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        self.select_button = QPushButton('Seleccionar Archivo de Comandos')
        self.select_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_button)
        self.file_label = QLabel('Ningún archivo seleccionado')
        layout.addWidget(self.file_label)
        self.command_view = QTextEdit()
        self.command_view.setReadOnly(True)
        layout.addWidget(self.command_view)
        self.run_button = QPushButton('Ejecutar Comandos')
        self.run_button.clicked.connect(self.execute_commands)
        self.run_button.setEnabled(False)
        layout.addWidget(self.run_button)
        self.setLayout(layout)
        self.file_path = None

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos de Texto (*.txt)")
        if file_name:
            self.file_path = file_name
            self.file_label.setText(f'Archivo: {self.file_path}')
            self.run_button.setEnabled(True)
            self.display_file_content()

    def display_file_content(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.command_view.setText(f.read())
        except Exception as e:
            self.command_view.setText(f"Error al leer el archivo:\n{e}")

    def execute_commands(self):
        """
        Método del Invocador. Lee el archivo, crea objetos comando
        usando el parser y los ejecuta.
        """
        if not self.file_path:
            return

        print("Iniciando ejecución en 3 segundos...")
        time.sleep(3)

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # El cliente/parser crea el objeto comando
                    command_obj = parse_line_to_command(line)
                    
                    # El invocador solo necesita llamar a execute()
                    if command_obj:
                        command_obj.execute()
                        time.sleep(0.1) # Pequeña pausa entre comandos

        except Exception as e:
            print(f"Ocurrió un error al ejecutar los comandos: {e}")
        
        print("✅ Ejecución finalizada.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    executor = CommandExecutor()
    executor.show()
    sys.exit(app.exec())