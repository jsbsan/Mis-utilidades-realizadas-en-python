import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QListWidget, QLineEdit, QHBoxLayout, QRadioButton, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt

class FileRenamerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_directory = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Renombrador de Ficheros")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # --- Selección de Directorio ---
        dir_selection_layout = QHBoxLayout()
        self.dir_label = QLabel("Directorio Seleccionado: Ninguno")
        dir_selection_layout.addWidget(self.dir_label)
        self.select_dir_button = QPushButton("Seleccionar Directorio")
        self.select_dir_button.clicked.connect(self.select_directory)
        dir_selection_layout.addWidget(self.select_dir_button)
        main_layout.addLayout(dir_selection_layout)

        # --- Lista de Ficheros ---
        self.file_list_widget = QListWidget()
        main_layout.addWidget(self.file_list_widget)

        # --- Opciones de Renombrado ---
        options_group_box = QGroupBox("Opciones de Renombrado")
        options_layout = QVBoxLayout()

        # Radio buttons for options
        self.add_prefix_radio = QRadioButton("a) Añadir letras delante")
        self.add_suffix_radio = QRadioButton("b) Añadir letras detrás")
        self.replace_text_radio = QRadioButton("c) Reemplazar letras")
        self.add_number_prefix_radio = QRadioButton("d) Añadir numeración automática (001, 002...)")


        self.add_prefix_radio.toggled.connect(self.toggle_options_visibility)
        self.add_suffix_radio.toggled.connect(self.toggle_options_visibility)
        self.replace_text_radio.toggled.connect(self.toggle_options_visibility)
        self.add_number_prefix_radio.toggled.connect(self.toggle_options_visibility)


        options_layout.addWidget(self.add_prefix_radio)
        options_layout.addWidget(self.add_suffix_radio)
        options_layout.addWidget(self.replace_text_radio)
        options_layout.addWidget(self.add_number_prefix_radio)


        # Prefix option
        self.prefix_layout = QHBoxLayout()
        self.prefix_label = QLabel("Texto a añadir (prefijo):")
        self.prefix_input = QLineEdit()
        self.prefix_layout.addWidget(self.prefix_label)
        self.prefix_layout.addWidget(self.prefix_input)
        options_layout.addLayout(self.prefix_layout)

        # Suffix option
        self.suffix_layout = QHBoxLayout()
        self.suffix_label = QLabel("Texto a añadir (sufijo):")
        self.suffix_input = QLineEdit()
        self.suffix_layout.addWidget(self.suffix_label)
        self.suffix_layout.addWidget(self.suffix_input)
        options_layout.addLayout(self.suffix_layout)

        # Replace option
        self.replace_layout = QHBoxLayout()
        self.replace_old_label = QLabel("Texto a reemplazar:")
        self.replace_old_input = QLineEdit()
        self.replace_new_label = QLabel("Texto nuevo:")
        self.replace_new_input = QLineEdit()
        self.replace_layout.addWidget(self.replace_old_label)
        self.replace_layout.addWidget(self.replace_old_input)
        self.replace_layout.addWidget(self.replace_new_label)
        self.replace_layout.addWidget(self.replace_new_input)
        options_layout.addLayout(self.replace_layout)
        
        # Number prefix option (no extra input needed)
        # This layout is mostly a placeholder for consistent spacing/margins
        self.number_prefix_layout = QHBoxLayout() 
        options_layout.addLayout(self.number_prefix_layout)


        options_group_box.setLayout(options_layout)
        main_layout.addWidget(options_group_box)

        self.toggle_options_visibility() # Set initial visibility

        # --- Botones de Acción ---
        action_buttons_layout = QHBoxLayout()
        self.preview_button = QPushButton("Previsualizar")
        self.preview_button.clicked.connect(self.preview_changes)
        action_buttons_layout.addWidget(self.preview_button)

        self.apply_button = QPushButton("Aplicar Cambios")
        self.apply_button.clicked.connect(self.apply_changes)
        action_buttons_layout.addWidget(self.apply_button)
        main_layout.addLayout(action_buttons_layout)

        self.setLayout(main_layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directory:
            self.current_directory = directory
            self.dir_label.setText(f"Directorio Seleccionado: {self.current_directory}")
            self.load_files()

    def load_files(self):
        self.file_list_widget.clear()
        if self.current_directory:
            files = [f for f in os.listdir(self.current_directory) if os.path.isfile(os.path.join(self.current_directory, f))]
            files.sort()
            for f in files:
                self.file_list_widget.addItem(f)

    def toggle_options_visibility(self):
        self.prefix_layout.setContentsMargins(0, 0, 0, 0)
        self.suffix_layout.setContentsMargins(0, 0, 0, 0)
        self.replace_layout.setContentsMargins(0, 0, 0, 0)
        self.number_prefix_layout.setContentsMargins(0, 0, 0, 0)

        self.prefix_label.setVisible(self.add_prefix_radio.isChecked())
        self.prefix_input.setVisible(self.add_prefix_radio.isChecked())

        self.suffix_label.setVisible(self.add_suffix_radio.isChecked())
        self.suffix_input.setVisible(self.add_suffix_radio.isChecked())

        self.replace_old_label.setVisible(self.replace_text_radio.isChecked())
        self.replace_old_input.setVisible(self.replace_text_radio.isChecked())
        self.replace_new_label.setVisible(self.replace_text_radio.isChecked())
        self.replace_new_input.setVisible(self.replace_text_radio.isChecked())
        
        # Eliminamos la línea problemática. El layout en sí no necesita ser visible/invisible,
        # solo los widgets que contiene (en este caso, no hay widgets de entrada aquí).
        # self.number_prefix_layout.setVisible(self.add_number_prefix_radio.isChecked()) 


        self.prefix_layout.setSpacing(0 if not self.add_prefix_radio.isChecked() else -1)
        self.suffix_layout.setSpacing(0 if not self.add_suffix_radio.isChecked() else -1)
        self.replace_layout.setSpacing(0 if not self.replace_text_radio.isChecked() else -1)
        self.number_prefix_layout.setSpacing(0 if not self.add_number_prefix_radio.isChecked() else -1)


    def get_renamed_files(self):
        renamed_files_map = {}
        if not self.current_directory:
            return renamed_files_map

        actual_files = [f for f in os.listdir(self.current_directory) if os.path.isfile(os.path.join(self.current_directory, f))]
        actual_files.sort()

        if self.add_number_prefix_radio.isChecked():
            for i, old_name in enumerate(actual_files):
                new_prefix = f"{i + 1:03d}"
                new_name = new_prefix + "_" + old_name 
                if old_name != new_name:
                    renamed_files_map[old_name] = new_name
        else:
            for old_name in actual_files:
                new_name = old_name
                if self.add_prefix_radio.isChecked():
                    prefix = self.prefix_input.text()
                    new_name = prefix + old_name
                elif self.add_suffix_radio.isChecked():
                    suffix = self.suffix_input.text()
                    name, ext = os.path.splitext(old_name)
                    new_name = name + suffix + ext
                elif self.replace_text_radio.isChecked():
                    old_text = self.replace_old_input.text()
                    new_text = self.replace_new_input.text()
                    if old_text:
                        new_name = old_name.replace(old_text, new_text)
                
                if old_name != new_name:
                    renamed_files_map[old_name] = new_name
        return renamed_files_map

    def preview_changes(self):
        self.file_list_widget.clear()
        renamed_files = self.get_renamed_files()
        
        if renamed_files:
            sorted_preview = sorted(renamed_files.items(), key=lambda item: item[0])
            for old_name, new_name in sorted_preview:
                self.file_list_widget.addItem(f"{old_name}  ->  {new_name}")
        else:
            self.load_files()

    def apply_changes(self):
        renamed_files = self.get_renamed_files()
        if not renamed_files or not self.current_directory:
            QMessageBox.information(self, "Información", "No hay cambios para aplicar o no se ha seleccionado un directorio.")
            return

        changes_made = False
        for old_name, new_name in renamed_files.items():
            old_path = os.path.join(self.current_directory, old_name)
            new_path = os.path.join(self.current_directory, new_name)
            try:
                if os.path.exists(old_path) and old_path != new_path:
                    os.rename(old_path, new_path)
                    changes_made = True
            except OSError as e:
                print(f"Error al renombrar '{old_name}' a '{new_name}': {e}")
        
        self.load_files()

        if changes_made:
            QMessageBox.information(self, "Confirmación", "¡Cambios aplicados correctamente!")
        else:
            QMessageBox.information(self, "Información", "No se realizaron cambios en los archivos.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamerApp()
    window.show()
    sys.exit(app.exec())