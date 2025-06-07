from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)

class FormularzDodawaniaRundy(QWidget):
    def __init__(self, conn, tabela_rund, turniej_id):  # Dodanie tabela_rund
        super().__init__()
        self.setWindowTitle("Dodaj Rundę")
        self.conn = conn
        self.turniej_id = turniej_id
        self.tabela_rund = tabela_rund  # Przechowywanie referencji

        self.layout = QVBoxLayout()

        # Pola formularza
        self.form_layout = QFormLayout()
        self.name_label = QLabel("Nazwa:")
        self.name_input = QLineEdit()
        self.priority_label = QLabel("Priorytet:")
        self.priority_input = QLineEdit()
        # self.turniej_id_label = QLabel("Turniej ID:")
        # self.turniej_id_input = QLineEdit()
        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.priority_label, self.priority_input)
        # self.form_layout.addRow(self.turniej_id_label, self.turniej_id_input)

        # Przycisk "Dodaj"
        self.dodaj_button = QPushButton("Dodaj")
        self.dodaj_button.clicked.connect(self.dodaj_runde)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.dodaj_button)

        self.setLayout(self.layout)

    def dodaj_runde(self):
        try:
            name = self.name_input.text()
            priority = int(self.priority_input.text())
            turniej_id = int(self.turniej_id)

            if not all([name, priority, turniej_id]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO runda (name, priority, turniej_id) VALUES (?, ?, ?)", (name, priority, turniej_id))
            self.conn.commit()

            # Odświeżenie tabeli rund
            self.tabela_rund.load_data()

            QMessageBox.information(self, "Sukces", "Runda została dodana.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))