# formularz_edycji_zawodnika.py
import os # <--- ADD THIS IMPORT
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)

# No direct import of Zawodnik class is needed here, as it uses self.conn directly.

class FormularzEdycjiZawodnika(QWidget):
    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, zawodnik_id, tabela_zawodnikow, bundle_dir): # <--- ADDED bundle_dir here!
        super().__init__()
        self.setWindowTitle("Edytuj Zawodnika")
        self.conn = conn
        self.zawodnik_id = zawodnik_id
        self.tabela_zawodnikow = tabela_zawodnikow
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here (for future use if needed)

        self.layout = QVBoxLayout()

        # Pobranie danych zawodnika
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM zawodnicy WHERE id = ?", (zawodnik_id,))
        zawodnik = cursor.fetchone()

        if not zawodnik: # Add a check in case player ID is invalid
            QMessageBox.critical(self, "Błąd", f"Nie znaleziono zawodnika o ID {zawodnik_id}.")
            self.close()
            return

        # Pola formularza
        self.form_layout = QFormLayout()
        self.firstname_label = QLabel("Imię:")
        self.firstname_input = QLineEdit(zawodnik[1])
        self.lastname_label = QLabel("Nazwisko:")
        self.lastname_input = QLineEdit(zawodnik[2])
        self.points_label = QLabel("Punkty:")
        self.points_input = QLineEdit(str(zawodnik[3]))
        self.kolejnosc_label = QLabel("Kolejność:")
        self.kolejnosc_input = QLineEdit(str(zawodnik[4]))
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
            points_text = self.points_input.text()
            kolejnosc_text = self.kolejnosc_input.text()

            # Basic validation
            if not all([firstname, lastname, points_text, kolejnosc_text]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            try:
                points = int(points_text)
                kolejnosc = int(kolejnosc_text)
            except ValueError:
                raise ValueError("Punkty i Kolejność muszą być liczbami całkowitymi.")

            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE zawodnicy
                SET firstname = ?, lastname = ?, points = ?, kolejnosc = ?
                WHERE id = ?
            """, (firstname, lastname, points, kolejnosc, self.zawodnik_id))
            self.conn.commit() # Correctly commits changes

            # Odświeżenie tabeli zawodników
            self.tabela_zawodnikow.load_data() # Correctly refreshes the parent table

            QMessageBox.information(self, "Sukces", "Dane zawodnika zostały zaktualizowane.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))
        except Exception as e: # Catch other potential database errors
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas aktualizacji zawodnika w bazie danych: {e}")
            self.conn.rollback() # Rollback on database error