import sys
import os
import pandas as pd
from openpyxl.utils import get_column_letter
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QSizePolicy, QFrame
)
# QThread, QObject, pyqtSignal ya no son necesarios
from PyQt6.QtCore import pyqtSlot, Qt # Mantenemos pyqtSlot y Qt

# Ya no necesitamos la clase ComparisonWorker

# --- Aplicación Principal PyQt (Sin Hilos) ---
class ExcelComparatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file1_path = None
        self.file2_path = None
        # No necesitamos self.comparison_thread ni self.comparison_worker
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Comparador de Archivos Excel (PyQt6 - Sin Hilos)")
        self.setGeometry(100, 100, 850, 700)

        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        selection_layout = QHBoxLayout()
        file1_layout = QVBoxLayout()
        file2_layout = QVBoxLayout()

        # --- Widgets ---
        # File 1 Selection
        self.btn_select1 = QPushButton("Seleccionar Archivo 1...")
        self.lbl_file1 = QLabel("Ningún archivo seleccionado")
        self.lbl_file1.setFrameShape(QFrame.Shape.Panel)
        self.lbl_file1.setFrameShadow(QFrame.Shadow.Sunken)
        self.lbl_file1.setMinimumHeight(30)
        self.lbl_file1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file1_layout.addWidget(self.btn_select1)
        file1_layout.addWidget(self.lbl_file1)

        # File 2 Selection
        self.btn_select2 = QPushButton("Seleccionar Archivo 2...")
        self.lbl_file2 = QLabel("Ningún archivo seleccionado")
        self.lbl_file2.setFrameShape(QFrame.Shape.Panel)
        self.lbl_file2.setFrameShadow(QFrame.Shadow.Sunken)
        self.lbl_file2.setMinimumHeight(30)
        self.lbl_file2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file2_layout.addWidget(self.btn_select2)
        file2_layout.addWidget(self.lbl_file2)

        selection_layout.addLayout(file1_layout)
        selection_layout.addLayout(file2_layout)

        # Compare Button
        self.btn_compare = QPushButton("Comparar Archivos")
        self.btn_compare.setFixedHeight(40)
        self.btn_compare.setStyleSheet("font-size: 11pt;")

        # Status Label
        self.lbl_status = QLabel("Listo.")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Tab Widget for Reports
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # --- Assemble Main Layout ---
        main_layout.addLayout(selection_layout)
        main_layout.addWidget(self.btn_compare)
        main_layout.addWidget(self.lbl_status)
        main_layout.addWidget(self.tab_widget)

        # --- Connections (Signals and Slots) ---
        self.btn_select1.clicked.connect(self.select_file1)
        self.btn_select2.clicked.connect(self.select_file2)
        # Conectar el botón de comparación directamente a la lógica
        self.btn_compare.clicked.connect(self.run_comparison_directly)

        self.setLayout(main_layout)

    # --- Métodos de Slots ---
    @pyqtSlot()
    def select_file1(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Excel 1", "",
            "Archivos Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )
        if filepath:
            self.file1_path = filepath
            self.lbl_file1.setText(os.path.basename(filepath))
            self.lbl_file1.setToolTip(filepath)

    @pyqtSlot()
    def select_file2(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Excel 2", "",
            "Archivos Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )
        if filepath:
            self.file2_path = filepath
            self.lbl_file2.setText(os.path.basename(filepath))
            self.lbl_file2.setToolTip(filepath)

    @pyqtSlot()
    def run_comparison_directly(self):
        """
        Ejecuta la comparación directamente en el hilo principal de la GUI.
        Esto bloqueará la interfaz durante la ejecución.
        """
        if not self.file1_path or not self.file2_path:
            QMessageBox.warning(self, "Archivos Faltantes",
                                "Por favor, selecciona ambos archivos Excel antes de comparar.")
            return

        # Deshabilitar botón, limpiar UI anterior
        self.btn_compare.setEnabled(False)
        self.clear_tabs()
        self.lbl_status.setText("Comparando... (la interfaz puede bloquearse)")
        QApplication.processEvents() # Intenta forzar la actualización de la GUI antes de bloquear

        # --- Lógica de Comparación (integrada aquí) ---
        summary_lines = []
        summary_lines.append(f"Comparando Archivo 1: {os.path.basename(self.file1_path)}")
        summary_lines.append(f"Comparando Archivo 2: {os.path.basename(self.file2_path)}")
        summary_lines.append("=" * 40 + "\n")

        xls1 = None
        xls2 = None

        try:
            self.lbl_status.setText("Abriendo archivos...")
            QApplication.processEvents()
            xls1 = pd.ExcelFile(self.file1_path)
            xls2 = pd.ExcelFile(self.file2_path)
            sheets1 = set(xls1.sheet_names)
            sheets2 = set(xls2.sheet_names)

            # 1. Comparar Nombres de Pestañas
            self.lbl_status.setText("Comparando nombres de pestañas...")
            QApplication.processEvents()
            summary_lines.append("*** Comparación de Pestañas ***")
            common_sheets = sheets1.intersection(sheets2)
            sheets_only_in_1 = sheets1 - sheets2
            sheets_only_in_2 = sheets2 - sheets1

            # (Construcción de líneas de resumen igual que antes)
            if common_sheets: summary_lines.append(f"Pestañas Comunes ({len(common_sheets)}): {', '.join(sorted(list(common_sheets)))}")
            else: summary_lines.append("No hay pestañas con el mismo nombre.")
            if sheets_only_in_1: summary_lines.append(f"Pestañas solo en Archivo 1 ({len(sheets_only_in_1)}): {', '.join(sorted(list(sheets_only_in_1)))}")
            if sheets_only_in_2: summary_lines.append(f"Pestañas solo en Archivo 2 ({len(sheets_only_in_2)}): {', '.join(sorted(list(sheets_only_in_2)))}")

            summary_lines.append("\n" + "=" * 40 + "\n")
            summary_lines.append("Ver las pestañas individuales para detalles de contenido.")

            # Llamada directa para actualizar la pestaña de resumen
            self.update_summary_tab("\n".join(summary_lines))
            QApplication.processEvents() # Intenta actualizar GUI


            # 2. Comparar Contenido de Pestañas Comunes
            if not common_sheets:
                 summary_lines.append("\nNo hay pestañas comunes para comparar contenido.")
                 self.update_summary_tab("\n".join(summary_lines)) # Actualiza resumen
            else:
                total_sheets = len(common_sheets)
                for i, sheet_name in enumerate(sorted(list(common_sheets))):
                    self.lbl_status.setText(f"Comparando contenido de '{sheet_name}' ({i+1}/{total_sheets})...")
                    QApplication.processEvents() # Intenta actualizar estado

                    sheet_report_lines = []
                    sheet_report_lines.append(f"--- Comparando Pestaña: '{sheet_name}' ---")

                    try:
                        # (Lectura de DataFrames df1, df2 igual que antes)
                        df1 = pd.read_excel(xls1, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)
                        df2 = pd.read_excel(xls2, sheet_name=sheet_name, header=None, dtype=str, na_filter=False)

                        differences_found_in_sheet = False
                        # (Comparación de dimensiones igual que antes)
                        if df1.shape != df2.shape:
                            sheet_report_lines.append(f"  - Diferencia de dimensiones: Archivo 1 ({df1.shape[0]}x{df1.shape[1]}) vs Archivo 2 ({df2.shape[0]}x{df2.shape[1]})")
                            differences_found_in_sheet = True

                        # (Comparación celda por celda igual que antes)
                        max_rows = max(df1.shape[0], df2.shape[0])
                        max_cols = max(df1.shape[1], df2.shape[1])
                        cell_diff_count = 0
                        for r in range(max_rows):
                            for c in range(max_cols):
                                # (Obtener val1_str, val2_str igual que antes)
                                val1_str = ""
                                val2_str = ""
                                cell_ref = f"{get_column_letter(c + 1)}{r + 1}"
                                try:
                                    if r < df1.shape[0] and c < df1.shape[1]: val1_str = str(df1.iloc[r, c])
                                    else: val1_str = "[CELDA NO EXISTE]"
                                except IndexError: val1_str = "[ERROR LECTURA F1]"
                                try:
                                    if r < df2.shape[0] and c < df2.shape[1]: val2_str = str(df2.iloc[r, c])
                                    else: val2_str = "[CELDA NO EXISTE]"
                                except IndexError: val2_str = "[ERROR LECTURA F2]"
                                
                                if val1_str != val2_str:
                                    sheet_report_lines.append(f"  - Celda {cell_ref}: '{val1_str}' (F1) != '{val2_str}' (F2)")
                                    differences_found_in_sheet = True
                                    cell_diff_count += 1

                        # (Lógica para reportar si no hubo diferencias igual que antes)
                        if not differences_found_in_sheet:
                            sheet_report_lines.append("  - Sin diferencias encontradas en el contenido.")
                        elif cell_diff_count == 0 and df1.shape != df2.shape:
                            sheet_report_lines.append("  - No se encontraron diferencias en los valores de las celdas dentro del área común comparada.")

                        # Llamada directa para añadir la pestaña de esta hoja
                        self.add_sheet_tab(sheet_name, "\n".join(sheet_report_lines))
                        QApplication.processEvents() # Intenta actualizar GUI

                    except Exception as e_sheet:
                        error_msg_sheet = f"\n*** Error al procesar esta pestaña '{sheet_name}' ***\n{e_sheet}\n"
                        sheet_report_lines.append(error_msg_sheet)
                        # Llamada directa para añadir la pestaña con el error
                        self.add_sheet_tab(sheet_name, "\n".join(sheet_report_lines))
                        QApplication.processEvents()


            # Actualización final del resumen (si es necesario)
            # summary_lines.append("\nComparación completada.")
            # self.update_summary_tab("\n".join(summary_lines))

        except Exception as e_global:
            # Llamada directa para manejar el error global
            self.handle_error(f"Error general durante la comparación: {e_global}")
            # Actualizar resumen con el error
            summary_lines.append(f"\n*** ERROR GENERAL ***\n{e_global}")
            self.update_summary_tab("\n".join(summary_lines))

        finally:
            # Asegurar que los archivos se cierren
            try:
                if xls1: xls1.close()
                if xls2: xls2.close()
            except Exception as e_close:
                print(f"Advertencia: no se pudieron cerrar los archivos Excel: {e_close}")

            # Reactivar el botón y estado final
            self.btn_compare.setEnabled(True)
            self.lbl_status.setText("Comparación finalizada.")
            QApplication.processEvents() # Asegurar que el estado final sea visible


    # --- Métodos de Actualización de GUI (Llamados directamente) ---
    def clear_tabs(self):
        """Elimina todas las pestañas del QTabWidget."""
        self.tab_widget.clear()

    def update_summary_tab(self, summary_content):
        """Actualiza o crea la pestaña de Resumen General."""
        summary_tab = None
        summary_tab_index = -1
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Resumen General":
                summary_tab_widget = self.tab_widget.widget(i)
                # Asegurarse de que el widget existe y tiene un QTextEdit
                if summary_tab_widget:
                    summary_tab = summary_tab_widget.findChild(QTextEdit)
                summary_tab_index = i
                break

        if summary_tab:
            summary_tab.setPlainText(summary_content)
        else:
            summary_widget = QWidget()
            layout = QVBoxLayout(summary_widget)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(summary_content)
            layout.addWidget(text_edit)
            layout.setContentsMargins(0,0,0,0)
            # Insertar al principio o añadir si no hay pestañas
            self.tab_widget.insertTab(0, summary_widget, "Resumen General")
            self.tab_widget.setCurrentIndex(0)


    def add_sheet_tab(self, sheet_name, sheet_content):
        """Añade una nueva pestaña para el reporte de una hoja específica."""
        sheet_widget = QWidget()
        layout = QVBoxLayout(sheet_widget)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(sheet_content)
        layout.addWidget(text_edit)
        layout.setContentsMargins(0,0,0,0)
        self.tab_widget.addTab(sheet_widget, sheet_name)

    def handle_error(self, error_message):
        """Muestra un mensaje de error crítico."""
        QMessageBox.critical(self, "Error en la Comparación", error_message)
        self.lbl_status.setText(f"Error.") # Actualiza estado
        # El botón se reactiva en el bloque finally de run_comparison_directly

    # closeEvent se mantiene igual (opcional)
    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExcelComparatorApp()
    ex.show()
    sys.exit(app.exec())