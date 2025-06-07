from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)


class FormularzEdycjiTurnieju(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Edytuj Turniej")
        self.conn = conn

        self.layout = QVBoxLayout()

        # Pobranie danych turnieju (zakładamy, że jest tylko jeden turniej)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM turniej LIMIT 1")
        turniej = cursor.fetchone()

        # Pola formularza
        self.form_layout = QFormLayout()
        self.name_label = QLabel("Nazwa:")
        self.name_input = QLineEdit(turniej[1])  # Wypełnienie nazwą
        self.begin_date_label = QLabel("Data rozpoczęcia (YYYY-MM-DD):")
        self.begin_date_input = QLineEdit(turniej[2])  # Wypełnienie datą
        self.tables_number_label = QLabel("Liczba stołów:")
        self.tables_number_input = QLineEdit(str(turniej[3]))  # Wypełnienie liczbą stołów
        self.rounds_number_label = QLabel("Liczba rund:")
        self.rounds_number_input = QLineEdit(str(turniej[4]))  # Wypełnienie liczbą rund

        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.begin_date_label, self.begin_date_input)
        self.form_layout.addRow(self.tables_number_label, self.tables_number_input)
        self.form_layout.addRow(self.rounds_number_label, self.rounds_number_input)

        # Przycisk "Zapisz"
        self.zapisz_button = QPushButton("Zapisz")
        self.zapisz_button.clicked.connect(self.zapisz_zmiany)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.zapisz_button)

        self.setLayout(self.layout)

    def zapisz_zmiany(self):
        try:
            name = self.name_input.text()
            begin_date = self.begin_date_input.text()
            tables_number = int(self.tables_number_input.text())
            rounds_number = int(self.rounds_number_input.text())

            if not all([name, begin_date, tables_number, rounds_number]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE turniej 
                SET name = ?, begin_date = ?, tables_number = ?, rounds_number = ? 
                WHERE id = ?
            """, (name, begin_date, tables_number, rounds_number, 1))  # Zakładamy, że ID turnieju to 1
            self.conn.commit()
            QMessageBox.information(self, "Sukces", "Dane turnieju zostały zaktualizowane.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))