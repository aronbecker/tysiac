# formularz_dodawania_turnieju.py
import os # <--- ADD THIS IMPORT
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from datetime import date

class FormularzDodawaniaTurnieju(QWidget):
    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, bundle_dir): # <--- ADDED bundle_dir here!
        super().__init__()
        self.setWindowTitle("Dodaj Turniej")
        self.conn = conn
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here (for future use if needed)

        self.layout = QVBoxLayout()

        # Pola formularza
        self.form_layout = QFormLayout()
        self.name_label = QLabel("Nazwa:")
        self.name_input = QLineEdit()
        self.begin_date_label = QLabel("Data rozpoczęcia (YYYY-MM-DD):")
        self.begin_date_input = QLineEdit(date.today().strftime("%Y-%m-%d"))
        self.tables_number_label = QLabel("Liczba stołów:")
        self.tables_number_input = QLineEdit()
        self.rounds_number_label = QLabel("Liczba rund:")
        self.rounds_number_input = QLineEdit()

        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.begin_date_label, self.begin_date_input)
        self.form_layout.addRow(self.tables_number_label, self.tables_number_input)
        self.form_layout.addRow(self.rounds_number_label, self.rounds_number_input)

        # Przycisk "Dodaj"
        self.dodaj_button = QPushButton("Dodaj")
        self.dodaj_button.clicked.connect(self.dodaj_turniej)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.dodaj_button)

        self.setLayout(self.layout)

    def dodaj_turniej(self):
        try:
            name = self.name_input.text()
            begin_date = self.begin_date_input.text()
            tables_number_text = self.tables_number_input.text()
            rounds_number_text = self.rounds_number_input.text()

            # Basic validation
            if not all([name, begin_date, tables_number_text, rounds_number_text]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            try:
                tables_number = int(tables_number_text)
                rounds_number = int(rounds_number_text)
            except ValueError:
                raise ValueError("Liczba stołów i liczba rund muszą być liczbami całkowitymi.")

            # Validate date format (optional but good practice)
            # from datetime import datetime
            # try:
            #     datetime.strptime(begin_date, "%Y-%m-%d")
            # except ValueError:
            #     raise ValueError("Nieprawidłowy format daty. Użyj YYYY-MM-DD.")

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO turniej (name, begin_date, tables_number, rounds_number)
                VALUES (?, ?, ?, ?)
            ''', (name, begin_date, tables_number, rounds_number))
            self.conn.commit()

            QMessageBox.information(self, "Sukces", "Turniej został dodany.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))
        except Exception as e: # Catch other potential database errors
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas dodawania turnieju do bazy danych: {e}")
            self.conn.rollback() # Rollback on database error