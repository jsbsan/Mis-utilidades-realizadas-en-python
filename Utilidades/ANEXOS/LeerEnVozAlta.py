import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QIcon
import pyttsx3
import threading

class LectorTextoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = None  # Inicializar el motor TTS como None
        self.is_speaking = False  # Para controlar si el motor está hablando
        self.initUI()
        self.initTTS()

    def initUI(self):
        self.setWindowTitle('Lector de Texto')
        self.setGeometry(100, 100, 600, 400) # (x, y, ancho, alto)
        
        # Opcional: Icono de la ventana (necesitarías un archivo .ico o .png)
        # self.setWindowIcon(QIcon('icono.png')) 

        layout = QVBoxLayout()

        # Etiqueta de instrucción
        self.label = QLabel("Pega tu texto aquí para que sea leído en voz alta:")
        layout.addWidget(self.label)

        # Área de texto para pegar
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Introduce o pega el texto aquí...")
        layout.addWidget(self.text_area)

        # Botón para leer
        self.read_button = QPushButton('Leer Texto', self)
        self.read_button.clicked.connect(self.start_reading_thread)
        layout.addWidget(self.read_button)
        
        # Botón para detener la lectura
        self.stop_button = QPushButton('Detener Lectura', self)
        self.stop_button.clicked.connect(self.stop_reading)
        self.stop_button.setEnabled(False) # Deshabilitado al inicio
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def initTTS(self):
        try:
            self.engine = pyttsx3.init()
            # Opcional: Configurar propiedades de la voz
            # voices = self.engine.getProperty('voices')
            # self.engine.setProperty('voice', voices[0].id) # Cambia a otra voz si está disponible
            # self.engine.setProperty('rate', 150) # Velocidad de la voz (palabras por minuto)
            # self.engine.setProperty('volume', 0.9) # Volumen (0.0 a 1.0)
            
            # Conectar un callback para cuando la lectura termine
            self.engine.connect('finished-utterance', self.on_speaking_finished)
            
        except Exception as e:
            QMessageBox.critical(self, "Error de TTS", 
                                 f"No se pudo inicializar el motor de texto a voz. Asegúrate de tener las dependencias de TTS instaladas (ej. espeak, sapi5, nsspeech). Error: {e}")
            self.read_button.setEnabled(False) # Deshabilitar el botón de lectura si hay un error
            self.stop_button.setEnabled(False)
            self.engine = None # Asegurar que el motor sea None si falla la inicialización

    def start_reading_thread(self):
        text_to_read = self.text_area.toPlainText()
        if not text_to_read:
            QMessageBox.warning(self, "Advertencia", "Por favor, introduce algún texto para leer.")
            return

        if self.engine is None:
            QMessageBox.critical(self, "Error", "El motor de texto a voz no está inicializado.")
            return

        self.read_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.is_speaking = True
        
        # Iniciar la lectura en un hilo separado para no congelar la GUI
        self.read_thread = threading.Thread(target=self._read_text, args=(text_to_read,))
        self.read_thread.start()

    def _read_text(self, text):
        try:
            if self.engine and self.is_speaking:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            # Captura de errores durante la lectura (ej. motor detenido)
            print(f"Error durante la lectura: {e}")
        finally:
            # Asegúrate de que el estado de los botones se restablezca incluso si hay un error
            if self.is_speaking: # Solo si no fue detenido manualmente por stop_reading
                 self.on_speaking_finished(None, None) # Llama a la función de finalización

    def stop_reading(self):
        if self.engine and self.is_speaking:
            self.engine.stop()
            self.is_speaking = False
            self.read_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def on_speaking_finished(self, name, completed):
        # Esta función se llama cuando la lectura termina o se detiene.
        # 'name' y 'completed' son argumentos del callback de pyttsx3.
        # No los usamos directamente aquí, pero son parte de la firma.
        if self.is_speaking: # Solo si no fue detenido manualmente por stop_reading
            self.is_speaking = False
            self.read_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        # Asegúrate de detener el motor TTS al cerrar la aplicación
        if self.engine:
            self.engine.stop()
            # Puedes llamar a engine.endLoop() si usas runLoop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LectorTextoApp()
    ex.show()
    sys.exit(app.exec())