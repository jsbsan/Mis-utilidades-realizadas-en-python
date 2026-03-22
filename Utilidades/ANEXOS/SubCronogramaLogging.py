import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QPlainTextEdit, QLineEdit
)
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# --- 1. CLASE PARA EL HANDLER DE LOGGING DE QT ---
# Esta clase redirige los mensajes de logging estándar de Python a un widget de texto.
class QPlainTextEditLogger(logging.Handler, QObject):
    # Señal para emitir el mensaje de log (seguro para hilos, aunque este script es de un solo hilo principal)
    appendPlainText = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QObject.__init__(self)
        self.widget = widget
        self.widget.setReadOnly(True)  # El área de log solo es de lectura
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        # Emitimos la señal con el mensaje formateado
        self.appendPlainText.emit(msg)

# --- 2. CLASE PRINCIPAL DE LA APLICACIÓN ---
class TextoCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texto Cleaner con Logging")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()
        self.setup_logging()
        self.logger.info("Aplicación iniciada.")

    def init_ui(self):
        # Layout principal vertical
        main_layout = QVBoxLayout()

        # 1. Área de entrada de texto
        self.input_text_area = QTextEdit()
        self.input_text_area.setPlaceholderText("Introduce el texto aquí...")
        main_layout.addWidget(self.input_text_area)

        # 2. Botones de acción
        button_layout = QHBoxLayout()
        
        # Botón de Procesar y Copiar
        self.process_button = QPushButton("Procesar y Copiar")
        self.process_button.clicked.connect(self.process_and_copy)
        button_layout.addWidget(self.process_button)

        # Botón de Limpiar Formulario
        self.clear_button = QPushButton("Limpiar Formulario")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)

        # 3. Área de texto resultante
        self.output_text_area = QLineEdit()
        self.output_text_area.setReadOnly(True)
        self.output_text_area.setPlaceholderText("Texto resultante aparecerá aquí (listo para copiar).")
        main_layout.addWidget(self.output_text_area)
        
        # 4. Área de logging
        log_label = QLineEdit("Registro de Eventos (Log):")
        log_label.setReadOnly(True)
        main_layout.addWidget(log_label)
        
        self.log_widget = QPlainTextEdit()
        main_layout.addWidget(self.log_widget)

        self.setLayout(main_layout)

    def setup_logging(self):
        # Configuramos el logger
        self.logger = logging.getLogger('TextoCleanerApp')
        self.logger.setLevel(logging.DEBUG)

        # Creamos el handler para redirigir a nuestro QPlainTextEdit
        log_handler = QPlainTextEditLogger(self.log_widget)
        # Definimos un formato
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        log_handler.setFormatter(formatter)
        
        # Añadimos el handler al logger
        self.logger.addHandler(log_handler)

    def process_and_copy(self):
        self.logger.info("Botón 'Procesar y Copiar' presionado. Procesando texto...")
        
        input_text = self.input_text_area.toPlainText()
        
        if not input_text:
            self.logger.warning("El campo de texto de entrada está vacío.")
            self.output_text_area.setText("¡Error! Introduce texto primero.")
            return

        # 1. Reemplazos de caracteres:
        # el Espacio " " por nada
        # el punto "." por nada
        # la coma "," por punto "."
        # el signo euro "€" por nada
        
        # Usamos una cadena de reemplazo para aplicar todos los cambios eficientemente
        
        # Primero reemplazamos "," por un carácter temporal (para que no se elimine en el paso 2)
        temp_text = input_text.replace(",", "TEMP_DOT_PLACEHOLDER")
        
        # Segundo, reemplazamos los caracteres por "nada"
        chars_to_remove = [" ", ".", "€"]
        cleaned_text = temp_text
        for char in chars_to_remove:
            cleaned_text = cleaned_text.replace(char, "")
            
        # Tercero, reemplazamos el placeholder temporal por el punto final
        final_text = cleaned_text.replace("TEMP_DOT_PLACEHOLDER", ".")
        
        self.output_text_area.setText(final_text)
        self.logger.debug(f"Texto procesado: '{final_text[:50]}...'")

        # 2. Copiar al portapapeles
        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)
        
        self.logger.info("Texto resultante copiado al portapapeles.")

    def clear_form(self):
        self.logger.info("Botón 'Limpiar Formulario' presionado. Limpiando campos.")
        self.input_text_area.clear()
        self.output_text_area.clear()
        self.log_widget.clear() # También limpiamos el log
        self.logger.info("Campos y log limpiados. Listo para empezar de cero.")

# --- 3. EJECUCIÓN DEL SCRIPT ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextoCleanerApp()
    window.show()
    sys.exit(app.exec_())