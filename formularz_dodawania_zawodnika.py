# formularz_dodawania_zawodnika.py
import os # <--- ADD THIS IMPORT
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal # <--- MAKE SURE THIS IS IMPORTED

from sqlite.zawodnik import Zawodnik # Assuming Zawodnik class is correctly modified to accept 'conn'

class FormularzDodawaniaZawodnika(QWidget):
    player_added = pyqtSignal()

    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, tabela_zawodnikow, bundle_dir): # <--- ADDED bundle_dir here!
        super().__init__()
        self.setWindowTitle("Dodaj Zawodnika")
        self.tabela_zawodnikow = tabela_zawodnikow
        self.conn = conn
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here (for future use if needed)
        self.layout = QVBoxLayout()

        self.firstname_label = QLabel("Imię:")
        self.firstname_input = QLineEdit()
        self.lastname_label = QLabel("Nazwisko:")
        self.lastname_input = QLineEdit()
        self.points_label = QLabel("Punkty:")
        self.points_input = QLineEdit()
        self.kolejnosc_label = QLabel("Kolejność:")
        self.kolejnosc_input = QLineEdit()

        self.dodaj_button = QPushButton("Dodaj")
        self.dodaj_button.clicked.connect(self.dodaj_zawodnika)

        form_layout = QFormLayout()
        form_layout.addRow(self.firstname_label, self.firstname_input)
        form_layout.addRow(self.lastname_label, self.lastname_input)
        form_layout.addRow(self.points_label, self.points_input)
        form_layout.addRow(self.kolejnosc_label, self.kolejnosc_input)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.dodaj_button)
        self.setLayout(self.layout)

    def dodaj_zawodnika(self):
        firstname = self.firstname_input.text()
        lastname = self.lastname_input.text()
        points_text = self.points_input.text() # Get as text first
        kolejnosc_text = self.kolejnosc_input.text() # Get as text first

        if not all([firstname, lastname, points_text, kolejnosc_text]): # Use all() for cleaner check
            QMessageBox.warning(self, "Błąd", "Wszystkie pola muszą być wypełnione.")
            return

        try:
            points = int(points_text) # Convert after initial check
            kolejnosc = int(kolejnosc_text) # Convert after initial check
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Punkty i Kolejność muszą być liczbami całkowitymi.")
            return

        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("INSERT INTO zawodnicy (firstname, lastname, points, kolejnosc) VALUES (?, ?, ?, ?)",
                                (firstname, lastname, points, kolejnosc))
            self.conn.commit() # This commit is correct and essential

            self.tabela_zawodnikow.load_data() # This refreshes the main table, correctly using self.conn

            QMessageBox.information(self, "Sukces", "Zawodnik został dodany.")
            self.player_added.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd Bazy Danych", f"Wystąpił błąd podczas dodawania zawodnika: {e}")
            self.conn.rollback() # Correctly rolls back on error