import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt

class FusionadorDeArchivos(QWidget):
    """
    Una aplicación de interfaz gráfica para fusionar múltiples archivos de texto en uno solo.

    Esta clase crea una ventana con un botón que, al ser presionado, abre un diálogo 
    para seleccionar archivos. Los archivos seleccionados se unen y se guardan en un 
    nuevo archivo que el usuario especifica.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Inicializa la interfaz de usuario de la ventana."""
        self.setWindowTitle('Fusionador de Archivos de Texto')
        self.setGeometry(300, 300, 400, 150)  # Posición x, y, ancho, alto

        # Layout vertical para organizar los widgets
        layout = QVBoxLayout()

        # Botón para iniciar el proceso de fusión
        self.btn_seleccionar = QPushButton('Seleccionar Archivos y Fusionar', self)
        self.btn_seleccionar.clicked.connect(self.iniciar_proceso)
        layout.addWidget(self.btn_seleccionar)

        self.setLayout(layout)

    def iniciar_proceso(self):
        """
        Gestiona el flujo completo de selección de archivos, fusión y guardado.
        """
        # Abre el diálogo para que el usuario seleccione los archivos de entrada
        archivos_entrada, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecciona los archivos de texto que quieres unir",
            "",  # Directorio inicial
            "Archivos de Texto (*.txt);;Todos los Archivos (*)"
        )

        if not archivos_entrada:
            # Si el usuario no selecciona ningún archivo, no hacemos nada
            return

        # Abre el diálogo para que el usuario elija dónde guardar el archivo fusionado
        archivo_salida, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo fusionado como...",
            "",  # Directorio inicial sugerido
            "Archivo de Texto (*.txt);;Todos los Archivos (*)"
        )

        if not archivo_salida:
            # Si el usuario no especifica un archivo de salida, cancelamos
            return

        # Realiza la fusión de los archivos mostrando una barra de progreso
        self.fusionar_archivos(archivos_entrada, archivo_salida)

    def fusionar_archivos(self, archivos_entrada, archivo_salida):
        """
        Lee el contenido de los archivos de entrada y lo escribe en el archivo de salida.

        Args:
            archivos_entrada (list): Una lista de rutas a los archivos de texto de entrada.
            archivo_salida (str): La ruta al archivo de texto donde se guardará el contenido fusionado.
        """
        # Configuración de la barra de progreso
        progreso = QProgressDialog("Fusionando archivos...", "Cancelar", 0, len(archivos_entrada), self)
        progreso.setWindowModality(Qt.WindowModality.WindowModal)
        progreso.setWindowTitle("Progreso")
        progreso.show()

        try:
            # Abrimos el archivo de salida en modo escritura ('w') con codificación UTF-8
            with open(archivo_salida, 'w', encoding='utf-8') as f_salida:
                for i, archivo in enumerate(archivos_entrada):
                    progreso.setValue(i)
                    if progreso.wasCanceled():
                        break  # Permite al usuario cancelar la operación

                    try:
                        # Abrimos cada archivo de entrada en modo lectura ('r')
                        with open(archivo, 'r', encoding='utf-8') as f_entrada:
                            f_salida.write(f_entrada.read())  # Leemos y escribimos el contenido
                            #f_salida.write('\n')  # Añadimos un salto de línea entre archivos
                    except Exception as e:
                        # Mostramos un error si no se puede leer un archivo específico
                        QMessageBox.warning(self, "Error de Lectura", 
                                            f"No se pudo leer el archivo {archivo}:\n{e}")
                        continue # Continuamos con el siguiente archivo
            
            progreso.setValue(len(archivos_entrada)) # Completa la barra de progreso
            # Mostramos un mensaje de éxito al finalizar
            QMessageBox.information(self, "Proceso Completado", 
                                    f"¡Archivos fusionados con éxito en '{archivo_salida}'!")

        except Exception as e:
            # Mostramos un error si ocurre un problema al escribir el archivo de salida
            QMessageBox.critical(self, "Error Crítico", 
                                 f"Ocurrió un error al escribir en el archivo de salida:\n{e}")


def main():
    """Función principal que inicia la aplicación."""
    app = QApplication(sys.argv)
    ventana = FusionadorDeArchivos()
    ventana.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()