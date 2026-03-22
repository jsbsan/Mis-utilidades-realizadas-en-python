import sys
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt

class ExtractorAnotaciones(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Extractor de Comentarios y Anotaciones PDF')
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()

    def init_ui(self):
        # Crear el layout principal
        layout = QVBoxLayout()

        # Botón para seleccionar archivo
        self.btn_abrir = QPushButton('Seleccionar Archivo PDF')
        self.btn_abrir.clicked.connect(self.abrir_dialogo_archivo)
        layout.addWidget(self.btn_abrir)

        # Etiqueta para mostrar el archivo seleccionado
        self.lbl_archivo = QLabel('Ningún archivo seleccionado')
        self.lbl_archivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_archivo.setWordWrap(True)
        layout.addWidget(self.lbl_archivo)

        # Área de texto para mostrar los resultados
        self.txt_resultados = QTextEdit()
        self.txt_resultados.setReadOnly(True)
        self.txt_resultados.setPlaceholderText('Aquí aparecerán las anotaciones extraídas...')
        layout.addWidget(self.txt_resultados)

        # Establecer el layout en la ventana
        self.setLayout(layout)

    def abrir_dialogo_archivo(self):
        """
        Abre un diálogo para que el usuario seleccione un archivo PDF.
        """
        # Abre el explorador de archivos y filtra por .pdf
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar PDF",
            "",  # Directorio inicial (vacío para el por defecto)
            "Archivos PDF (*.pdf)"
        )

        # Si el usuario selecciona un archivo (no cancela)
        if ruta_archivo:
            self.lbl_archivo.setText(f"Procesando: {ruta_archivo}")
            self.txt_resultados.clear()
            self.extraer_anotaciones(ruta_archivo)
            self.lbl_archivo.setText(f"Archivo: {ruta_archivo}")

    def extraer_anotaciones(self, ruta_pdf):
        """
        Abre el PDF y extrae todas las anotaciones de texto.
        """
        try:
            doc = fitz.open(ruta_pdf)
            resultados = []
            
            # Iterar por cada página del documento
            for num_pagina in range(len(doc)):
                pagina = doc.load_page(num_pagina)
                
                # Obtener todas las anotaciones de la página
                for anot in pagina.annots():
                    # 'info' contiene un diccionario con los detalles
                    info = anot.info
                    
                    # Buscamos anotaciones que tengan contenido de texto
                    # (como notas adhesivas o comentarios en resaltados)
                    contenido = info.get('content', '').strip()
                    
                    if contenido:
                        autor = info.get('title', 'Autor Desconocido')
                        
                        # --- LÍNEA CORREGIDA ---
                        # Usamos la propiedad .type_name del objeto anotación
                        tipo_anot_str = f"Tipo numérico: {anot.type}"
                        
                        resultados.append(f"--- Página {num_pagina + 1} ---")
                        resultados.append(f"Tipo: {tipo_anot_str}")
                        resultados.append(f"Autor: {autor}")
                        resultados.append(f"Comentario: {contenido}")
                        resultados.append("-" * 20 + "\n")
            doc.close()
            # Mostrar los resultados en el área de texto
            if resultados:
                self.txt_resultados.setText("\n".join(resultados))
            else:
                self.txt_resultados.setText("No se encontraron anotaciones con texto en el documento.")
        except Exception as e:
            self.txt_resultados.setText(f"Ocurrió un error al procesar el archivo:\n{e}")
            self.lbl_archivo.setText("Error al procesar el archivo")


# --- Bloque principal para ejecutar la aplicación ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = ExtractorAnotaciones()
    ventana.show()
    sys.exit(app.exec())