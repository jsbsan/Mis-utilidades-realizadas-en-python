import sys
import os
import subprocess # Para ejecutar otros scripts
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QFileDialog,
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QProcess # QProcess para mejor manejo de procesos externos

class ScriptRunnerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ejecutor de Scripts Python')
        self.setGeometry(200, 200, 700, 500) # Aumentado el ancho para mejor visualización

        # Layout principal
        self.main_layout = QVBoxLayout(self)

        # Sección para seleccionar carpeta
        folder_selection_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("Selecciona una carpeta con scripts .py")
        self.folder_path_edit.setReadOnly(True)
        select_folder_button = QPushButton("Seleccionar Carpeta")
        select_folder_button.clicked.connect(self.select_folder)

        folder_selection_layout.addWidget(QLabel("Carpeta de Scripts:"))
        folder_selection_layout.addWidget(self.folder_path_edit)
        folder_selection_layout.addWidget(select_folder_button)
        self.main_layout.addLayout(folder_selection_layout)

        # Área de scroll para los botones de los scripts
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Permite que el widget interior se redimensione
        self.scroll_content_widget = QWidget() # Contenedor para los botones dentro del scroll
        self.script_buttons_layout = QVBoxLayout(self.scroll_content_widget) # Layout para los botones
        self.script_buttons_layout.setAlignment(Qt.AlignTop) # Alinea los botones arriba
        self.scroll_area.setWidget(self.scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Etiqueta para mostrar la salida (opcional, pero útil)
        self.output_label = QLabel("Salida del script aparecerá aquí (o en la consola).")
        self.output_label.setWordWrap(True) # Para que el texto se ajuste
        self.output_label.setFixedHeight(60) # Altura fija para la etiqueta de salida
        self.main_layout.addWidget(self.output_label)

        self.current_processes = {} # Para rastrear procesos en ejecución

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Scripts")
        if folder_path:
            self.folder_path_edit.setText(folder_path)
            self.load_scripts(folder_path)
        else:
            self.folder_path_edit.clear()
            self.clear_script_buttons()
            self.output_label.setText("Selección de carpeta cancelada.")


    def clear_script_buttons(self):
        # Limpiar botones previos
        while self.script_buttons_layout.count():
            item = self.script_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Importante para liberar memoria correctamente

    def load_scripts(self, folder_path):
        self.clear_script_buttons()
        try:
            found_scripts = False
            for item_name in os.listdir(folder_path):
                if item_name.endswith(".py"):
                    found_scripts = True
                    script_full_path = os.path.join(folder_path, item_name)
                    button = QPushButton(item_name)
                    # Usamos una función lambda para pasar el path del script al método run_script
                    # y el nombre del botón para poder deshabilitarlo.
                    button.clicked.connect(
                        lambda checked, path=script_full_path, btn=button: self.run_script(path, btn)
                    )
                    self.script_buttons_layout.addWidget(button)
            if not found_scripts:
                self.output_label.setText(f"No se encontraron scripts .py en: {folder_path}")
            else:
                self.output_label.setText(f"Scripts cargados desde: {folder_path}. Haz clic para ejecutar.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"La carpeta no existe: {folder_path}")
            self.output_label.setText("Error: La carpeta seleccionada no existe.")
        except PermissionError:
            QMessageBox.warning(self, "Error", f"No tienes permisos para leer la carpeta: {folder_path}")
            self.output_label.setText("Error: Permiso denegado para acceder a la carpeta.")
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", f"Ocurrió un error al cargar scripts: {str(e)}")
            self.output_label.setText(f"Error al cargar scripts: {str(e)}")


    def run_script(self, script_path, button_pressed):
        script_name = os.path.basename(script_path)

        if script_path in self.current_processes and self.current_processes[script_path].state() != QProcess.NotRunning:
            self.output_label.setText(f"El script '{script_name}' ya está en ejecución.")
            return

        self.output_label.setText(f"Ejecutando: {script_name}...")
        button_pressed.setEnabled(False) # Deshabilitar botón mientras se ejecuta

        process = QProcess(self)
        self.current_processes[script_path] = process

        process.setProgram(sys.executable) # El intérprete de Python actual
        process.setArguments([script_path])
        process.setWorkingDirectory(os.path.dirname(script_path)) # Directorio de trabajo del script

        # Conectar señales para salida y finalización
        process.readyReadStandardOutput.connect(lambda: self.handle_stdout(script_name))
        process.readyReadStandardError.connect(lambda: self.handle_stderr(script_name))
        process.finished.connect(lambda exitCode, exitStatus: self.script_finished(script_path, script_name, button_pressed, exitCode, exitStatus))
        process.errorOccurred.connect(lambda error: self.script_error(script_path, script_name, button_pressed, error))


        process.start()

    def handle_stdout(self, script_name):
        process = self.sender() # Obtener el QProcess que emitió la señal
        if process:
            output = process.readAllStandardOutput().data().decode(errors='ignore').strip()
            if output:
                print(f"Salida de {script_name}: {output}")
                self.output_label.setText(f"Salida de {script_name} (ver consola para detalles).")

    def handle_stderr(self, script_name):
        process = self.sender()
        if process:
            error_output = process.readAllStandardError().data().decode(errors='ignore').strip()
            if error_output:
                print(f"Error de {script_name}: {error_output}")
                self.output_label.setText(f"Error de {script_name} (ver consola para detalles).")

    def script_finished(self, script_path, script_name, button, exit_code, exit_status):
        button.setEnabled(True) # Reactivar botón
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.output_label.setText(f"'{script_name}' finalizó correctamente.")
            print(f"'{script_name}' finalizó. Código de salida: {exit_code}")
        elif exit_status == QProcess.CrashExit:
            self.output_label.setText(f"'{script_name}' falló (Crash).")
            print(f"'{script_name}' falló (Crash). Código de salida: {exit_code}")
        else:
            self.output_label.setText(f"'{script_name}' finalizó con errores. Código: {exit_code}.")
            print(f"'{script_name}' finalizó con errores. Código de salida: {exit_code}")

        if script_path in self.current_processes:
            del self.current_processes[script_path]

    def script_error(self, script_path, script_name, button, error):
        button.setEnabled(True) # Reactivar botón
        error_string = ""
        # Mapeo de errores de QProcess.ProcessError a cadenas descriptivas
        if error == QProcess.FailedToStart: error_string = "Falló al iniciar"
        elif error == QProcess.Crashed: error_string = "Se colgó (Crash)"
        elif error == QProcess.Timedout: error_string = "Tiempo de espera agotado"
        elif error == QProcess.ReadError: error_string = "Error de lectura"
        elif error == QProcess.WriteError: error_string = "Error de escritura"
        elif error == QProcess.UnknownError: error_string = "Error desconocido"

        message = f"Error al ejecutar '{script_name}': {error_string}."
        self.output_label.setText(message)
        print(message)
        QMessageBox.warning(self, "Error de Ejecución", message)

        if script_path in self.current_processes:
            del self.current_processes[script_path]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScriptRunnerApp()
    ex.show()
    sys.exit(app.exec_())