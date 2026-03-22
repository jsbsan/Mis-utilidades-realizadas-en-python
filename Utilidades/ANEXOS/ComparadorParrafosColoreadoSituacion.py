import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit)
from PyQt5.QtGui import QFont

class ComparadorTextos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparador de Textos")
        self.setGeometry(100, 100, 600, 500)  # Aumentamos un poco más la altura
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
        etiqueta_resultado = QLabel("Palabras que varían (posición original):")
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
        layout_principal.addLayout(layout_botones)
        layout_principal.addWidget(etiqueta_resultado)
        layout_principal.addWidget(self.area_resultado)

        self.setLayout(layout_principal)

    def comparar(self):
        texto1_original = self.campo_texto1.text()
        texto2_original = self.campo_texto2.text()
        texto1_lower = texto1_original.lower().split()
        texto2_lower = texto2_original.lower().split()

        palabras_texto1 = set(texto1_lower)
        palabras_texto2 = set(texto2_lower)

        solo_en_texto1 = palabras_texto1 - palabras_texto2
        solo_en_texto2 = palabras_texto2 - palabras_texto1

        resultado_html = ""

        if solo_en_texto1:
            resultado_html += "<b>Palabras solo en el Texto 1:</b><br>"
            for palabra in solo_en_texto1:
                indices = [i for i, p in enumerate(texto1_lower) if p == palabra]
                posiciones = [str(i + 1) for i in indices]
                azul = f"<span style='color: blue;'>{palabra}</span> (Posiciones: {', '.join(posiciones)})<br>"
                resultado_html += azul

        if solo_en_texto2:
            resultado_html += "<br><b>Palabras solo en el Texto 2:</b><br>"
            for palabra in solo_en_texto2:
                indices = [i for i, p in enumerate(texto2_lower) if p == palabra]
                posiciones = [str(i + 1) for i in indices]
                rojo = f"<span style='color: red;'>{palabra}</span> (Posiciones: {', '.join(posiciones)})<br>"
                resultado_html += rojo

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