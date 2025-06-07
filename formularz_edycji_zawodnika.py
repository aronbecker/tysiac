from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)


class FormularzEdycjiZawodnika(QWidget):
    def __init__(self, conn, zawodnik_id, tabela_zawodnikow):
        super().__init__()
        self.setWindowTitle("Edytuj Zawodnika")
        self.conn = conn
        self.zawodnik_id = zawodnik_id
        self.tabela_zawodnikow = tabela_zawodnikow  # Przechowywanie referencji

        self.layout = QVBoxLayout()

        # Pobranie danych zawodnika
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM zawodnicy WHERE id = ?", (zawodnik_id,))
        zawodnik = cursor.fetchone()

        # Pola formularza
        self.form_layout = QFormLayout()
        self.firstname_label = QLabel("Imię:")
        self.firstname_input = QLineEdit(zawodnik[1])  # Wypełnienie imieniem
        self.lastname_label = QLabel("Nazwisko:")
        self.lastname_input = QLineEdit(zawodnik[2])  # Wypełnienie nazwiskiem
        self.points_label = QLabel("Punkty:")
        self.points_input = QLineEdit(str(zawodnik[3]))  # Wypełnienie punktami
        self.kolejnosc_label = QLabel("Kolejność:")
        self.kolejnosc_input = QLineEdit(str(zawodnik[4]))  # Wypełnienie kolejnością
        self.form_layout.addRow(self.firstname_label, self.firstname_input)
        self.form_layout.addRow(self.lastname_label, self.lastname_input)
        self.form_layout.addRow(self.points_label, self.points_input)
        self.form_layout.addRow(self.kolejnosc_label, self.kolejnosc_input)

        # Przycisk "Zapisz"
        self.zapisz_button = QPushButton("Zapisz")
        self.zapisz_button.clicked.connect(self.zapisz_zmiany)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.zapisz_button)

        self.setLayout(self.layout)

    def zapisz_zmiany(self):
        try:
            firstname = self.firstname_input.text()
            lastname = self.lastname_input.text()
            points = int(self.points_input.text())
            kolejnosc = int(self.kolejnosc_input.text())

            if not all([firstname, lastname, points, kolejnosc]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE zawodnicy 
                SET firstname = ?, lastname = ?, points = ?, kolejnosc = ? 
                WHERE id = ?
            """, (firstname, lastname, points, kolejnosc, self.zawodnik_id))
            self.conn.commit()

            # Odświeżenie tabeli zawodników
            self.tabela_zawodnikow.load_data()

            QMessageBox.information(self, "Sukces", "Dane zawodnika zostały zaktualizowane.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))