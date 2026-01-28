import sys
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit,
    QVBoxLayout, QWidget, QFileDialog, QLabel, QStatusBar
)
from PyQt6.QtCore import Qt

class PDFCommentExtractor(QMainWindow):
    """
    Una aplicación de escritorio para extraer comentarios de archivos PDF.

    Esta aplicación permite al usuario seleccionar un archivo PDF y muestra
    todos los comentarios de tipo "Texto" (anotaciones de texto libre) que
    se encuentran en el documento.
    """

    def __init__(self):
        super().__init__()

        # --- Configuración de la ventana principal ---
        self.setWindowTitle("Extractor de Comentarios de PDF")
        self.setGeometry(100, 100, 700, 500)

        # --- Widgets principales ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Etiqueta de instrucciones
        self.instructions_label = QLabel(
            "1. Haz clic en 'Abrir PDF' para seleccionar un archivo.\n"
            "2. Los comentarios del PDF se mostrarán a continuación."
        )
        self.layout.addWidget(self.instructions_label)

        # Botón para abrir el archivo PDF
        self.open_button = QPushButton("Abrir PDF")
        self.open_button.clicked.connect(self.open_pdf_file)
        self.layout.addWidget(self.open_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Área de texto para mostrar los comentarios
        self.comments_text_edit = QTextEdit()
        self.comments_text_edit.setReadOnly(True)
        self.layout.addWidget(self.comments_text_edit)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")

    def open_pdf_file(self):
        """
        Abre un diálogo para seleccionar un archivo PDF y
        lanza la extracción de comentarios.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo PDF", "", "Archivos PDF (*.pdf)"
        )

        if file_path:
            self.status_bar.showMessage(f"Procesando: {file_path}")
            QApplication.processEvents()  # Actualiza la GUI
            self.extract_comments(file_path)

    def extract_comments(self, file_path):
        """
        Extrae los comentarios de un archivo PDF y los muestra en el área de texto.

        Args:
            file_path (str): La ruta al archivo PDF.
        """
        self.comments_text_edit.clear()
        extracted_comments = []

        try:
            doc = fitz.open(file_path)
            comment_count = 0

            for page_num, page in enumerate(doc):
                # Buscamos anotaciones en cada página
                for annot in page.annots():
                    # Filtramos por anotaciones de tipo "Texto"
                    if annot.type[0] == 8:  # 8 corresponde a 'Text'
                        comment_info = annot.info
                        content = comment_info.get("content", "Comentario sin texto.")
                        author = comment_info.get("title", "Anónimo")

                        extracted_comments.append(
                            f"--- Página {page_num + 1} (Autor: {author}) ---\n"
                            f"{content}\n"
                        )
                        comment_count += 1

            if extracted_comments:
                self.comments_text_edit.setText("\n".join(extracted_comments))
                self.status_bar.showMessage(f"Se encontraron {comment_count} comentarios.")
            else:
                self.comments_text_edit.setText("No se encontraron comentarios en el archivo.")
                self.status_bar.showMessage("Proceso finalizado. No hay comentarios.")

        except Exception as e:
            self.comments_text_edit.setText(f"Error al procesar el archivo:\n{e}")
            self.status_bar.showMessage("Error")
        finally:
            if 'doc' in locals():
                doc.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    extractor = PDFCommentExtractor()
    extractor.show()
    sys.exit(app.exec())