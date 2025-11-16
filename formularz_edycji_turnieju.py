import sys # Upewnij się, że masz ten import
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal # <--- WAŻNY IMPORT

class FormularzEdycjiTurnieju(QWidget):
    
    # KROK 1: Dodajemy sygnał, który wyślemy po zapisaniu zmian
    zmiany_zapisane = pyqtSignal()

    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Edytuj Turniej")
        self.conn = conn
        self.turniej_id = None # <--- ZMIANA: Zmienna do przechowania ID

        self.layout = QVBoxLayout()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM turniej LIMIT 1")
        turniej = cursor.fetchone()

        if not turniej:
            QMessageBox.critical(self, "Błąd", "Nie znaleziono żadnego turnieju do edycji.")
            self.close()
            return
            
        # KROK 2: Zapisujemy ID turnieju
        self.turniej_id = turniej[0]

        # Pola formularza
        self.form_layout = QFormLayout()
        self.name_label = QLabel("Nazwa:")
        self.name_input = QLineEdit(turniej[1]) 
        self.begin_date_label = QLabel("Data rozpoczęcia (YYYY-MM-DD):")
        self.begin_date_input = QLineEdit(turniej[2]) 
        self.tables_number_label = QLabel("Liczba stołów:")
        self.tables_number_input = QLineEdit(str(turniej[3])) 
        self.rounds_number_label = QLabel("Liczba rund:")
        self.rounds_number_input = QLineEdit(str(turniej[4])) 

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
        # Sprawdzenie, czy ID zostało poprawnie wczytane
        if self.turniej_id is None:
            QMessageBox.critical(self, "Błąd krytyczny", "Nie udało się wczytać ID turnieju.")
            return

        try:
            name = self.name_input.text()
            begin_date = self.begin_date_input.text()
            tables_number = int(self.tables_number_input.text())
            rounds_number = int(self.rounds_number_input.text())

            if not all([name, begin_date, tables_number, rounds_number]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            cursor = self.conn.cursor()
            
            # KROK 3: Używamy zapisanego 'self.turniej_id' zamiast '1'
            cursor.execute("""
                UPDATE turniej 
                SET name = ?, begin_date = ?, tables_number = ?, rounds_number = ? 
                WHERE id = ?
            """, (name, begin_date, tables_number, rounds_number, self.turniej_id)) 
            
            self.conn.commit()
            QMessageBox.information(self, "Sukces", "Dane turnieju zostały zaktualizowane.")
            
            # KROK 4: Emitujemy sygnał do głównego okna
            self.zmiany_zapisane.emit() 
            
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))
        except Exception as e:
            # Lepsze logowanie błędów bazy danych
            QMessageBox.critical(self, "Błąd bazy danych", f"Wystąpił błąd: {e}")