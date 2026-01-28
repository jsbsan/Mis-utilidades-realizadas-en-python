import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QTextEdit, QMessageBox, QStatusBar
)
from PyQt6.QtCore import QObject, pyqtSignal

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGGING (VERSIÓN CORREGIDA)
# -----------------------------------------------------------------------------

# Manejador de logs personalizado para enviar registros a la GUI
class QtLogHandler(logging.Handler, QObject):
    """
    Un manejador de logs que emite una señal de PyQt6 por cada registro.
    Debe heredar de logging.Handler para ser un handler y de QObject para usar señales.
    """
    # Define la señal que se emitirá con cada nuevo registro de log
    new_record = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        """
        Constructor que inicializa ambas clases padre: QObject y logging.Handler.
        """
        QObject.__init__(self)
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        """
        Formatea el mensaje del log y emite la señal para que la GUI la reciba.
        """
        msg = self.format(record)
        self.new_record.emit(msg)

def setup_logging():
    """
    Configura el logging para que escriba en un archivo y en la GUI.
    """
    log_format = "%(asctime)s - [%(levelname)s] - %(message)s"
    
    # Configuración del logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Captura niveles desde INFO (INFO, WARNING, ERROR)

    # Crear manejador para escribir en el archivo 'merger_app.log'
    file_handler = logging.FileHandler("merger_app.log", mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)
    
    logging.info("Sistema de logging inicializado.")


# -----------------------------------------------------------------------------
# 2. CLASE PRINCIPAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------

class FileMergerApp(QMainWindow):
    """
    Clase principal de la aplicación que construye la interfaz gráfica y
    contiene toda la lógica de la aplicación.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusionador de Archivos con Log")
        self.setGeometry(100, 100, 700, 500)

        # Almacena la lista de rutas de los archivos seleccionados
        self.selected_files = []

        # Inicializar la interfaz de usuario
        self._init_ui()
        
        # Conectar el logger a la GUI para mostrar los registros en tiempo real
        self._connect_logger()
        
        logging.info("Aplicación iniciada y ventana principal mostrada.")

    def _init_ui(self):
        """
        Crea y organiza todos los widgets de la interfaz gráfica.
        """
        # Layout principal vertical
        main_layout = QVBoxLayout()

        # Botón para seleccionar archivos
        self.select_button = QPushButton("1. Seleccionar Archivos (.txt, .csv)")
        self.select_button.clicked.connect(self.select_files)
        main_layout.addWidget(self.select_button)

        # Lista para mostrar los archivos seleccionados por el usuario
        self.file_list_widget = QListWidget()
        main_layout.addWidget(self.file_list_widget)

        # Botón para unir los archivos
        self.merge_button = QPushButton("2. Unir y Guardar Archivo")
        self.merge_button.setEnabled(False)  # Deshabilitado hasta que se seleccionen archivos
        self.merge_button.clicked.connect(self.merge_files)
        main_layout.addWidget(self.merge_button)

        # Área de texto para mostrar los logs en tiempo real
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        main_layout.addWidget(self.log_display)

        # Widget central que contendrá el layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Barra de estado para mensajes cortos
        self.setStatusBar(QStatusBar(self))

    def _connect_logger(self):
        """
        Crea y conecta el manejador de logs personalizado a la GUI.
        """
        self.log_handler = QtLogHandler()
        log_format = "%(asctime)s - [%(levelname)s] - %(message)s"
        self.log_handler.setFormatter(logging.Formatter(log_format))
        
        # Conectar la señal del handler al método que actualiza el QTextEdit
        self.log_handler.new_record.connect(self.update_log_display)
        
        # Añadir el nuevo handler al logger raíz
        logging.getLogger().addHandler(self.log_handler)

    def update_log_display(self, record_str):
        """
        Slot que recibe los mensajes de log y los añade al widget de texto.
        """
        self.log_display.append(record_str)
        # Mueve el scroll al final para ver siempre el último log
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    def select_files(self):
        """
        Abre un diálogo para que el usuario seleccione múltiples archivos.
        """
        logging.info("El usuario ha hecho clic en 'Seleccionar Archivos'.")
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos para unir",
            "",
            "Archivos de texto (*.txt *.csv *.*)"
        )

        if files:
            self.selected_files = files
            self.file_list_widget.clear()
            self.file_list_widget.addItems(self.selected_files)
            self.merge_button.setEnabled(True)
            self.statusBar().showMessage(f"{len(self.selected_files)} archivos seleccionados.")
            logging.info(f"Usuario seleccionó {len(self.selected_files)} archivos: {self.selected_files}")
        else:
            self.statusBar().showMessage("Selección cancelada por el usuario.")
            logging.warning("El usuario canceló la selección de archivos.")

    def merge_files(self):
        """
        Une los archivos seleccionados en un único archivo de salida.
        """
        if not self.selected_files:
            QMessageBox.warning(self, "Advertencia", "No hay archivos seleccionados para unir.")
            logging.warning("Intento de fusión sin archivos seleccionados.")
            return

        logging.info("El usuario ha iniciado el proceso de fusión.")
        
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo fusionado",
            "",
            "Archivo de texto (*.txt);;Archivo CSV (*.csv);; Todos (*.*)"
        )

        if output_file:
            logging.info(f"El archivo de salida será: {output_file}")
            self.statusBar().showMessage("Fusionando archivos...")
            
            try:
                with open(output_file, 'w', encoding='utf-8') as outfile:
                    for i, filename in enumerate(self.selected_files):
                        logging.info(f"Procesando y añadiendo el archivo: {filename}")
                        with open(filename, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                            # Añade un salto de línea entre archivos, excepto en el último
                            if i < len(self.selected_files) - 1:
                                outfile.write("\n")
                
                self.statusBar().showMessage(f"Archivos fusionados con éxito en {output_file}")
                logging.info(f"Éxito: Todos los archivos han sido fusionados en '{output_file}'.")
                QMessageBox.information(self, "Éxito", f"Los archivos se han unido correctamente en:\n{output_file}")

            except Exception as e:
                self.statusBar().showMessage("Error durante la fusión.")
                logging.error(f"Ocurrió un error al fusionar los archivos: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"No se pudieron unir los archivos.\nError: {e}")
        else:
            self.statusBar().showMessage("Proceso de guardado cancelado.")
            logging.warning("El usuario canceló el diálogo para guardar el archivo.")
            
    def closeEvent(self, event):
        """
        Se ejecuta cuando el usuario cierra la ventana para registrar el evento.
        """
        logging.info("El usuario ha cerrado la aplicación.")
        super().closeEvent(event)

# -----------------------------------------------------------------------------
# 3. PUNTO DE ENTRADA DE LA APLICACIÓN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Primero, configurar el sistema de logging
    setup_logging()
    
    # Crear y ejecutar la aplicación PyQt6
    app = QApplication(sys.argv)
    window = FileMergerApp()
    window.show()
    sys.exit(app.exec())