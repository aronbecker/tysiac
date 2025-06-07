from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from sqlite.zawodnik import Zawodnik

class FormularzDodawaniaZawodnika(QWidget):
    def __init__(self, conn, tabela_zawodnikow):
        super().__init__()
        self.setWindowTitle("Dodaj Zawodnika")
        self.tabela_zawodnikow = tabela_zawodnikow
        self.conn = conn
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
        points = self.points_input.text()
        kolejnosc = self.kolejnosc_input.text()

        if not firstname or not lastname or not points or not kolejnosc:
            QMessageBox.warning(self, "Błąd", "Wszystkie pola muszą być wypełnione.")
            return

        try:
            points = int(points)  # Konwersja na int
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Punkty muszą być liczbą całkowitą.")
            return

        # Zawodnik1 = Zawodnik(firstname, lastname, points, kolejnosc)
        # print(Zawodnik1.firstname, Zawodnik1.lastname, Zawodnik1.points, Zawodnik1.kolejnosc)
        # Zawodnik1.zapisz()
        # self.tabela_zawodnikow.load_data()  # Wywołanie load_data w TabelaZawodnikow
        # self.close()
        self.cursor = self.conn.cursor()
        try
            self.cursor.execute("INSERT INTO zawodnicy (firstname, lastname, points) VALUES (?, ?, ?)",
                                (firstname, lastname, points))
            self.conn.commit()
            self.tabela_zawodnikow.load_data()  # Wywołanie load_data w TabelaZawodnikow
            QMessageBox.information(self, "Sukces", "Zawodnik został dodany.")
            self.player_added.emit() # Emit the signal after successful addition

            self.close() # Zamknij formularz po dodaniu zawodnika
        except Exception as e:
            QMessageBox.critical(self, "Błąd Bazy Danych", f"Wystąpił błąd podczas dodawania zawodnika: {e}")
            self.conn.rollback() # Rollback changes if an error occurs

