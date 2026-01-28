import sys
import os
import difflib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
# Importa la biblioteca para leer .docx, manejando el posible error si no está instalada
try:
    import docx
except ImportError:
    print("Error: La biblioteca 'python-docx' no está instalada.")
    print("Por favor, instálala ejecutando: pip install python-docx")
    sys.exit(1)

# --- Funciones Auxiliares ---

def read_docx(filepath):
    """Lee el contenido de un archivo .docx y devuelve una lista de líneas."""
    try:
        doc = docx.Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            # Agrega saltos de línea explícitos entre párrafos para difflib
            full_text.append(para.text + '\n') 
        # Une todo y luego divide por líneas reales (incluyendo las añadidas)
        # Esto ayuda a difflib a tratar cada párrafo como un bloque potencial
        return "".join(full_text).splitlines(keepends=True) 
    except Exception as e:
        print(f"Error al leer el archivo {filepath}: {e}")
        # Retorna None o una lista vacía para indicar error
        return None 

# --- Clase Principal de la Aplicación ---

class WordComparerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file1_path = None
        self.file2_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Comparador de Archivos Word (.docx)')
        self.setGeometry(100, 100, 800, 600) # Posición x, y, ancho, alto

        # Habilitar Arrastrar y Soltar en la ventana principal
        self.setAcceptDrops(True)

        # --- Layout Principal ---
        main_layout = QVBoxLayout()

        # --- Sección de Selección de Archivos ---
        selection_layout = QHBoxLayout()

        # Layout para Archivo 1
        file1_layout = QVBoxLayout()
        self.lbl_file1 = QLabel("Archivo 1: (Arrastra aquí o selecciona)")
        self.lbl_file1.setWordWrap(True) # Para que el texto se ajuste
        self.lbl_file1.setFrameShape(QFrame.StyledPanel) # Añade un borde
        self.lbl_file1.setAlignment(Qt.AlignCenter)
        self.lbl_file1.setMinimumHeight(50) # Altura mínima para el área de drop
        btn_select1 = QPushButton("Seleccionar Archivo 1")
        btn_select1.clicked.connect(self.select_file1)
        file1_layout.addWidget(self.lbl_file1)
        file1_layout.addWidget(btn_select1)

        # Layout para Archivo 2
        file2_layout = QVBoxLayout()
        self.lbl_file2 = QLabel("Archivo 2: (Arrastra aquí o selecciona)")
        self.lbl_file2.setWordWrap(True)
        self.lbl_file2.setFrameShape(QFrame.StyledPanel)
        self.lbl_file2.setAlignment(Qt.AlignCenter)
        self.lbl_file2.setMinimumHeight(50)
        btn_select2 = QPushButton("Seleccionar Archivo 2")
        btn_select2.clicked.connect(self.select_file2)
        file2_layout.addWidget(self.lbl_file2)
        file2_layout.addWidget(btn_select2)

        selection_layout.addLayout(file1_layout)
        selection_layout.addLayout(file2_layout)
        main_layout.addLayout(selection_layout)

        # --- Botón de Comparar ---
        self.btn_compare = QPushButton("Comparar Archivos")
        self.btn_compare.clicked.connect(self.compare_files)
        main_layout.addWidget(self.btn_compare)

        # --- Área de Resultados ---
        self.lbl_results = QLabel("Resultados de la Comparación:")
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True) # Hacer el área de texto no editable
        self.results_display.setFontFamily("Courier New") # Fuente monoespaciada para diff
        
        main_layout.addWidget(self.lbl_results)
        main_layout.addWidget(self.results_display, stretch=1) # stretch=1 hace que ocupe el espacio restante

        # Establecer el layout principal
        self.setLayout(main_layout)

    # --- Métodos para Selección de Archivos ---

    def select_file1(self):
        """Abre un diálogo para seleccionar el primer archivo."""
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Descomentar si hay problemas con el diálogo nativo
        filepath, _ = QFileDialog.getOpenFileName(self, 
                                                  "Seleccionar Archivo Word 1", 
                                                  "", # Directorio inicial (vacío usa el último)
                                                  "Word Documents (*.docx);;All Files (*)", 
                                                  options=options)
        if filepath:
            self.update_filepath(1, filepath)

    def select_file2(self):
        """Abre un diálogo para seleccionar el segundo archivo."""
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(self, 
                                                  "Seleccionar Archivo Word 2", 
                                                  "", 
                                                  "Word Documents (*.docx);;All Files (*)", 
                                                  options=options)
        if filepath:
            self.update_filepath(2, filepath)

    def update_filepath(self, file_index, filepath):
        """Actualiza la ruta del archivo y la etiqueta correspondiente."""
        # Validar que sea .docx (aunque el filtro ayuda, el drag-drop no filtra)
        if not filepath.lower().endswith(".docx"):
             QMessageBox.warning(self, "Archivo no válido", 
                                 f"El archivo seleccionado no es un .docx:\n{filepath}")
             return

        if file_index == 1:
            self.file1_path = filepath
            self.lbl_file1.setText(f"Archivo 1:\n{os.path.basename(filepath)}")
        elif file_index == 2:
            self.file2_path = filepath
            self.lbl_file2.setText(f"Archivo 2:\n{os.path.basename(filepath)}")
        
        # Limpiar resultados anteriores si se cambia un archivo
        self.results_display.clear()

    # --- Métodos para Arrastrar y Soltar ---

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Se activa cuando algo entra arrastrándose en la ventana."""
        # Verificar si los datos arrastrados contienen URLs (rutas de archivo)
        if event.mimeData().hasUrls():
            # Verificar si son archivos .docx
            urls = event.mimeData().urls()
            docx_files = [url for url in urls if url.isLocalFile() and url.toLocalFile().lower().endswith('.docx')]
            
            if docx_files: # Si hay al menos un .docx, acepta el evento
                event.acceptProposedAction()
            else:
                event.ignore() # Ignora si no hay .docx
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Se activa cuando se sueltan los archivos."""
        urls = event.mimeData().urls()
        docx_files = [url.toLocalFile() for url in urls if url.isLocalFile() and url.toLocalFile().lower().endswith('.docx')]

        if not docx_files:
             event.ignore() # No debería pasar si dragEnterEvent funcionó, pero por si acaso
             return

        # Asignar los archivos soltados
        if len(docx_files) == 1:
            # Si se suelta un archivo, asignarlo al primer slot libre
            if self.file1_path is None:
                self.update_filepath(1, docx_files[0])
            elif self.file2_path is None:
                 self.update_filepath(2, docx_files[0])
            else:
                 # Si ambos están llenos, reemplazar el primero (o mostrar mensaje)
                 reply = QMessageBox.question(self, 'Reemplazar Archivo',
                                              "Ambos espacios están ocupados. ¿Desea reemplazar el Archivo 1?",
                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                 if reply == QMessageBox.Yes:
                    self.update_filepath(1, docx_files[0])

        elif len(docx_files) >= 2:
            # Si se sueltan dos o más, usar los dos primeros
            self.update_filepath(1, docx_files[0])
            self.update_filepath(2, docx_files[1])
            if len(docx_files) > 2:
                 QMessageBox.information(self, "Archivos Ignorados", 
                                         "Se soltaron más de dos archivos .docx. Solo se usarán los dos primeros.")

        event.acceptProposedAction()

    # --- Método de Comparación ---

    def compare_files(self):
        """Realiza la comparación de los dos archivos seleccionados."""
        if not self.file1_path or not self.file2_path:
            QMessageBox.warning(self, "Archivos Faltantes", 
                                "Por favor, selecciona dos archivos .docx para comparar.")
            return

        # Limpiar resultados anteriores
        self.results_display.clear()
        self.results_display.setText("Comparando archivos...")
        QApplication.processEvents() # Forzar actualización de la GUI (importante sin threads)

        # Leer el contenido de los archivos
        content1 = read_docx(self.file1_path)
        content2 = read_docx(self.file2_path)

        # Verificar si la lectura fue exitosa
        if content1 is None or content2 is None:
             QMessageBox.critical(self, "Error de Lectura", 
                                 "No se pudo leer uno o ambos archivos. Revisa la consola para más detalles.")
             self.results_display.setText("Error al leer los archivos.")
             return

        # Realizar la comparación usando difflib
        # unified_diff genera un formato estándar de diferencias
        diff = difflib.unified_diff(
            content1, 
            content2, 
            fromfile=os.path.basename(self.file1_path), # Nombre del archivo 1
            tofile=os.path.basename(self.file2_path),   # Nombre del archivo 2
            lineterm='' # Evita dobles saltos de línea en la salida
        )

        # Crear el informe de diferencias
        diff_report = list(diff) # Convertir el generador a lista

        if not diff_report:
            self.results_display.setText("Los archivos son idénticos.")
        else:
            # Añadir una cabecera explicativa simple
            report_header = (
                f"Comparación entre '{os.path.basename(self.file1_path)}' y '{os.path.basename(self.file2_path)}'\n"
                f"{'-'*80}\n"
                "Leyenda:\n"
                "  --- Nombre Archivo Original\n"
                "  +++ Nombre Archivo Modificado\n"
                "  @@ -línea_original,longitud +línea_modificada,longitud @@ Encabezado de Sección\n"
                "  - Línea eliminada (presente solo en el archivo original)\n"
                "  + Línea añadida (presente solo en el archivo modificado)\n"
                "    Línea sin cambios (contexto)\n"
                 f"{'-'*80}\n\n"
            )
            # Unir las líneas del diff con saltos de línea
            self.results_display.setText(report_header + "\n".join(diff_report))

        QMessageBox.information(self, "Comparación Completa", 
                                "La comparación ha finalizado. Revisa los resultados.")


# --- Ejecución Principal ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WordComparerApp()
    ex.show()
    sys.exit(app.exec_())