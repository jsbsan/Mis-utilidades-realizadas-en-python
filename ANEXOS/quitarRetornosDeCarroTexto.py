import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


class RemovedorDeRetornos(QWidget):
    """
    Una aplicación de escritorio para eliminar retornos de carro de un texto.
    El botón de pegar también procesa el texto automáticamente.
    """

    def __init__(self):
        super().__init__()
        self.inicializarUI()

    def inicializarUI(self):
        """
        Configura la interfaz de usuario de la aplicación.
        """
        self.setWindowTitle("Eliminador de Retornos de Carro")
        self.setWindowIcon(QIcon("icono.png"))  # Opcional: añade un icono
        self.setGeometry(200, 200, 500, 450)

        # Layout principal vertical
        layout_principal = QVBoxLayout()

        # --- Zona de Entrada ---
        layout_entrada_horizontal = QHBoxLayout()
        label_entrada = QLabel("Pega tu texto aquí o usa el botón:")
        
        # Botón modificado para pegar y limpiar en un solo paso
        boton_pegar_limpiar = QPushButton("Pegar y Limpiar")
        boton_pegar_limpiar.clicked.connect(self.pegar_y_limpiar)
        
        layout_entrada_horizontal.addWidget(label_entrada)
        layout_entrada_horizontal.addStretch()
        layout_entrada_horizontal.addWidget(boton_pegar_limpiar)

        layout_principal.addLayout(layout_entrada_horizontal)

        self.texto_entrada = QTextEdit()
        self.texto_entrada.setPlaceholderText("El texto con saltos de línea...")
        layout_principal.addWidget(self.texto_entrada)

        # Botón central (se mantiene por si se edita el texto manualmente)
        boton_procesar = QPushButton("Quitar Retornos de Carro (si editas manualmente)")
        boton_procesar.clicked.connect(self.procesar_texto)
        layout_principal.addWidget(boton_procesar)

        # --- Zona de Salida ---
        layout_salida_horizontal = QHBoxLayout()
        label_salida = QLabel("Texto resultante:")
        
        boton_copiar = QPushButton("Copiar Resultado")
        boton_copiar.clicked.connect(self.copiar_resultado)
        
        layout_salida_horizontal.addWidget(label_salida)
        layout_salida_horizontal.addStretch()
        layout_salida_horizontal.addWidget(boton_copiar)

        layout_principal.addLayout(layout_salida_horizontal)

        self.texto_salida = QTextEdit()
        self.texto_salida.setReadOnly(True)
        self.texto_salida.setPlaceholderText("Aquí aparecerá el texto procesado...")
        layout_principal.addWidget(self.texto_salida)

        self.setLayout(layout_principal)

    def procesar_texto(self):
        """
        Toma el texto del campo de entrada, elimina los retornos de carro
        y lo muestra en el campo de salida.
        """
        texto_original = self.texto_entrada.toPlainText()
        # Reemplaza retornos de carro (\r) y saltos de línea (\n) por un espacio
        # .strip() elimina espacios sobrantes al inicio y al final.
        texto_procesado = texto_original.replace("\r", " ").replace("\n", " ").strip()
        self.texto_salida.setPlainText(texto_procesado)

    def pegar_y_limpiar(self):
        """
        Obtiene texto del portapapeles, lo pone en la entrada y lo procesa.
        """
        portapapeles = QApplication.clipboard()
        texto_pegado = portapapeles.text()
        self.texto_entrada.setPlainText(texto_pegado)
        # Llama a la función de procesado justo después de pegar
        self.procesar_texto()

    def copiar_resultado(self):
        """
        Copia el texto del campo de resultado al portapapeles del sistema.
        """
        texto_a_copiar = self.texto_salida.toPlainText()
        if texto_a_copiar:  # Solo copia si hay algo que copiar
            portapapeles = QApplication.clipboard()
            portapapeles.setText(texto_a_copiar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = RemovedorDeRetornos()
    ventana.show()
    sys.exit(app.exec())