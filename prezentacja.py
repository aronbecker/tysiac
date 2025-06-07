from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class Prezentacja(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Prezentacja")

        # Załaduj styl CSS
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

        self.conn = conn
        self.layout = QVBoxLayout()
        self.label = QLabel()
        font = QFont()
        font.setPointSize(24)  # Ustaw większy rozmiar czcionki dla prezentacji
        self.label.setFont(font)
        # Przycisk "Następny"
        self.nastepny_button = QPushButton("Następny")
        self.nastepny_button.clicked.connect(self.pokaz_nastepnego_zawodnika)
        self.layout.addWidget(self.nastepny_button)

        self.poprzedni_button = QPushButton("Poprzedni")
        self.poprzedni_button.clicked.connect(self.pokaz_poprzedniego_zawodnika)
        self.layout.addWidget(self.poprzedni_button)

        self.layout.addWidget(self.nastepny_button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.pokaz_nastepnego_zawodnika)
        self.aktualny_indeks = 0
                # Wyśrodkowanie za pomocą layoutu
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)  # Dodanie pustego miejsca po lewej
        h_layout.addWidget(self.label)
        h_layout.addStretch(1)  # Dodanie pustego miejsca po prawej
        self.layout.addLayout(h_layout)

        self.layout.addStretch(1)  # Dodanie pustego miejsca u góry
        self.layout.addStretch(1)  # Dodanie pustego miejsca u dołu

    def pokaz_prezentacje(self):
        self.aktualny_indeks = 0
        self.pokaz_nastepnego_zawodnika()
        #self.timer.start(3000)  # Zmiana zawodnika co 3 sekundy

    def pokaz_nastepnego_zawodnika(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT firstname, lastname, points FROM zawodnicy ORDER BY points ASC")
        zawodnicy = cursor.fetchall()

        if self.aktualny_indeks < len(zawodnicy):
            zawodnik = zawodnicy[self.aktualny_indeks]
            miejsce = self.aktualny_indeks + 1  # Obliczenie miejsca

            # Wyświetlenie miejsca dla ostatnich 5 zawodników
            if miejsce > len(zawodnicy) - 5:
                self.label.setText(f"{len(zawodnicy) - miejsce+1}. {zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")
            else:
                self.label.setText(f"{zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")

            self.aktualny_indeks += 1
        else:
            self.label.setText("Dziękujemy !!!")

    def pokaz_poprzedniego_zawodnika(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT firstname, lastname, points FROM zawodnicy ORDER BY points ASC")
        zawodnicy = cursor.fetchall()

        self.aktualny_indeks -= 1  # Zmniejszenie indeksu

        # Zabezpieczenie przed wyjściem poza zakres listy
        if self.aktualny_indeks < 0:
            self.aktualny_indeks = 0  # Ustawienie na pierwszy element

        if 0 <= self.aktualny_indeks < len(zawodnicy):
            zawodnik = zawodnicy[self.aktualny_indeks]
            miejsce = self.aktualny_indeks + 1  # Obliczenie miejsca

            # Wyświetlenie miejsca dla ostatnich 5 zawodników
            if miejsce > len(zawodnicy) - 5:
                self.label.setText(f"{len(zawodnicy) - miejsce+1}. {zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")
            else:
                self.label.setText(f"{zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")

        else:
            self.label.setText("Dziękujemy !!!")