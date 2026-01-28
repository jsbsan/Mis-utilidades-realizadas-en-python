import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit)
from PyQt5.QtGui import QFont

class ComparadorTextos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparador de Textos")
        self.setGeometry(100, 100, 600, 450)  # Aumentamos un poco la altura
        self.fuente_principal = QFont("Arial", 12)
        self.initUI()

    def initUI(self):
        # Etiquetas y campos de texto para la entrada
        etiqueta_texto1 = QLabel("Texto 1:")
        etiqueta_texto1.setFont(self.fuente_principal)
        self.campo_texto1 = QLineEdit()
        self.campo_texto1.setFont(self.fuente_principal)

        etiqueta_texto2 = QLabel("Texto 2:")
        etiqueta_texto2.setFont(self.fuente_principal)
        self.campo_texto2 = QLineEdit()
        self.campo_texto2.setFont(self.fuente_principal)

        # Botón de comparar
        boton_comparar = QPushButton("Comparar Textos")
        boton_comparar.setFont(self.fuente_principal)
        boton_comparar.clicked.connect(self.comparar)

        # Botón de limpiar
        boton_limpiar = QPushButton("Limpiar")
        boton_limpiar.setFont(self.fuente_principal)
        boton_limpiar.clicked.connect(self.limpiar)

        # Layout para los botones
        layout_botones = QHBoxLayout()
        layout_botones.addWidget(boton_comparar)
        layout_botones.addWidget(boton_limpiar)

        # Área de texto para mostrar los resultados
        etiqueta_resultado = QLabel("Palabras que varían:")
        etiqueta_resultado.setFont(self.fuente_principal)
        self.area_resultado = QTextEdit()
        self.area_resultado.setFont(self.fuente_principal)
        self.area_resultado.setReadOnly(True)

        # Layout principal
        layout_principal = QVBoxLayout()
        layout_entrada = QVBoxLayout()
        layout_entrada.addWidget(etiqueta_texto1)
        layout_entrada.addWidget(self.campo_texto1)
        layout_entrada.addWidget(etiqueta_texto2)
        layout_entrada.addWidget(self.campo_texto2)

        layout_principal.addLayout(layout_entrada)
        layout_principal.addLayout(layout_botones)  # Añadimos el layout de los botones
        layout_principal.addWidget(etiqueta_resultado)
        layout_principal.addWidget(self.area_resultado)

        self.setLayout(layout_principal)

    def comparar(self):
        texto1 = self.campo_texto1.text().lower().split()
        texto2 = self.campo_texto2.text().lower().split()

        palabras_texto1 = set(texto1)
        palabras_texto2 = set(texto2)

        solo_en_texto1 = palabras_texto1 - palabras_texto2
        solo_en_texto2 = palabras_texto2 - palabras_texto1

        resultado_html = ""
        if solo_en_texto1:
            azul = "<span style='color: blue;'>{}</span>".format(" ".join(solo_en_texto1))
            resultado_html += f"Palabras solo en el Texto 1: {azul}<br>"
        if solo_en_texto2:
            rojo = "<span style='color: red;'>{}</span>".format(" ".join(solo_en_texto2))
            resultado_html += f"Palabras solo en el Texto 2: {rojo}"

        if resultado_html:
            self.area_resultado.setHtml(resultado_html)
        else:
            self.area_resultado.setText("No hay palabras que varíen entre los dos textos.")

    def limpiar(self):
        """Limpia los campos de texto y el área de resultados."""
        self.campo_texto1.clear()
        self.campo_texto2.clear()
        self.area_resultado.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = ComparadorTextos()
    ventana.show()
    sys.exit(app.exec_())