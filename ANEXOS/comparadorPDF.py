import sys
import fitz  # PyMuPDF
import difflib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt

class PDFComparator(QMainWindow):
    """
    Ventana principal de la aplicación para comparar archivos PDF.
    Utiliza botones para seleccionar los archivos.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparador de Archivos PDF")
        self.setGeometry(100, 100, 1200, 600)

        # Variables para almacenar las rutas de los archivos
        self.file_path1 = None
        self.file_path2 = None

        # Contenedor principal y layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # --- Layout para la selección de archivos ---
        selection_layout = QHBoxLayout()

        # Panel para el Archivo 1
        file1_vbox = QVBoxLayout()
        self.btn_select_file1 = QPushButton("Seleccionar Archivo 1")
        self.btn_select_file1.clicked.connect(lambda: self.select_file(1))
        self.lbl_file1 = QLabel("Ningún archivo seleccionado.")
        self.lbl_file1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file1.setWordWrap(True)
        file1_vbox.addWidget(self.btn_select_file1)
        file1_vbox.addWidget(self.lbl_file1)

        # Panel para el Archivo 2
        file2_vbox = QVBoxLayout()
        self.btn_select_file2 = QPushButton("Seleccionar Archivo 2")
        self.btn_select_file2.clicked.connect(lambda: self.select_file(2))
        self.lbl_file2 = QLabel("Ningún archivo seleccionado.")
        self.lbl_file2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file2.setWordWrap(True)
        file2_vbox.addWidget(self.btn_select_file2)
        file2_vbox.addWidget(self.lbl_file2)

        selection_layout.addLayout(file1_vbox)
        selection_layout.addLayout(file2_vbox)
        main_layout.addLayout(selection_layout)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # --- Layout para los resultados de la comparación ---
        results_layout = QHBoxLayout()
        self.result1_text = QTextEdit()
        self.result1_text.setReadOnly(True)
        self.result1_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        self.result2_text = QTextEdit()
        self.result2_text.setReadOnly(True)
        self.result2_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Sincronizar el desplazamiento vertical de los paneles de resultados
        self.result1_text.verticalScrollBar().valueChanged.connect(
            self.result2_text.verticalScrollBar().setValue
        )
        self.result2_text.verticalScrollBar().valueChanged.connect(
            self.result1_text.verticalScrollBar().setValue
        )

        results_layout.addWidget(self.result1_text)
        results_layout.addWidget(self.result2_text)
        main_layout.addLayout(results_layout, 1) # El '1' le da más espacio a este layout

    def select_file(self, file_number):
        """
        Abre un diálogo para seleccionar un archivo PDF.
        file_number: 1 para el primer archivo, 2 para el segundo.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo PDF",
            "", # Directorio inicial
            "Archivos PDF (*.pdf)"
        )

        if file_path:
            file_name = file_path.split('/')[-1]
            if file_number == 1:
                self.file_path1 = file_path
                self.lbl_file1.setText(f"Archivo 1: {file_name}")
            else:
                self.file_path2 = file_path
                self.lbl_file2.setText(f"Archivo 2: {file_name}")
            
            self.compare_pdfs()

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extrae el texto de un archivo PDF.
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text")
            doc.close()
            return text
        except Exception as e:
            return f"Error al leer el archivo: {e}"

    def compare_pdfs(self):
        """
        Compara los dos archivos PDF si ambos han sido seleccionados
        y muestra las diferencias en los paneles de texto.
        """
        if self.file_path1 and self.file_path2:
            # Limpiar resultados anteriores
            self.result1_text.clear()
            self.result2_text.clear()
            QApplication.processEvents() # Forzar actualización de la UI

            text1 = self.extract_text_from_pdf(self.file_path1)
            text2 = self.extract_text_from_pdf(self.file_path2)

            lines1 = text1.splitlines()
            lines2 = text2.splitlines()

            # Usamos difflib para encontrar las diferencias
            differ = difflib.SequenceMatcher(None, lines1, lines2)
            
            html1 = ""
            html2 = ""

            for opcode, i1, i2, j1, j2 in differ.get_opcodes():
                if opcode == 'equal':
                    for i in range(i1, i2):
                        html1 += f"{lines1[i]}<br>"
                    for j in range(j1, j2):
                        html2 += f"{lines2[j]}<br>"
                elif opcode == 'replace' or opcode == 'delete':
                    for i in range(i1, i2):
                        html1 += f'<span style="background-color: #ffcdd2;">{lines1[i]}</span><br>'
                elif opcode == 'insert':
                    for j in range(j1, j2):
                        html2 += f'<span style="background-color: #c8e6c9;">{lines2[j]}</span><br>'
                
                # Para 'replace', el 'insert' se maneja por separado
                if opcode == 'replace':
                    for j in range(j1, j2):
                         html2 += f'<span style="background-color: #c8e6c9;">{lines2[j]}</span><br>'

            # Usamos formato <pre> para mantener los espacios y saltos de línea
            self.result1_text.setHtml(f"<pre>{html1}</pre>")
            self.result2_text.setHtml(f"<pre>{html2}</pre>")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    comparator = PDFComparator()
    comparator.show()
    sys.exit(app.exec())