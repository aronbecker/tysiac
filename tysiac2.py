import os
import sys
import sqlite3
from sqlite.zawodnik import Zawodnik
from sqlite.gra import Gra
import random
from datetime import date
from tysiac_czysc import CzyszczenieDanych
from formularz_edycji_turnieju import FormularzEdycjiTurnieju


from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
                             QMessageBox, QTableWidget, QTableWidgetItem, QStackedWidget, QMenu, QAction)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

from tabela_zawodnikow import TabelaZawodnikow
from tabela_rund import TabelaRund
from tabela_gier import TabelaGier
from formularz_dodawania_zawodnika import FormularzDodawaniaZawodnika
from formularz_dodawania_rund import FormularzDodawaniaRundy
from formularz_dodawania_turnieju import FormularzDodawaniaTurnieju
from prezentacja import Prezentacja

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skockie Asy - Turniej Tysiąca z okazji Dnia Miasta i Gminy Skoki")

        # Połączenie z bazą danych
        self.conn = sqlite3.connect('./my.db')  # Zmień nazwę bazy danych
        self.stworz_baze_danych()
        self.cursor = self.conn.cursor()

        # Pobierz dane turnieju (załóżmy, że jest tylko jeden aktywny turniej)
        self.cursor.execute("SELECT name, begin_date, id FROM turniej LIMIT 1")  # Dostosuj zapytanie
        turniej_data = self.cursor.fetchone()

        if turniej_data:
            turniej_name, begin_date, turniej_id = turniej_data
        else:
            turniej_name = "Brak danych turnieju"
            begin_date = ""
            turniej_id = "1"

        self.turniej_id = turniej_id
        self.prezentacja = Prezentacja(self.conn)
        # Nagłówek
        header_layout = QHBoxLayout()
        name_label = QLabel(f"Turniej: {turniej_name}")
        date_label = QLabel(f"Data: {begin_date}")

        name_label.setStyleSheet("font-size: 18px; font-weight: bold;") # Dodano style
        date_label.setStyleSheet("font-size: 16px;") # Dodano style

        header_layout.addWidget(name_label)
        header_layout.addWidget(date_label)

        # Przyciski
        lista_zawodnikow_button = QPushButton("Lista zawodników")
        dodaj_zawodnika_button = QPushButton("Dodaj zawodnika")
        rundy_button = QPushButton("Rundy")
        prezentacja_button = QPushButton("Prezentacja")
        dodaj_turniej_button = QPushButton("Dodaj turniej")
        edytuj_turniej_button = QPushButton("Edytuj turniej")  # Dodanie przycisku

        # Przycisk "Wyczyść dane"
        wyczysc_dane_button = QPushButton("Wyczyść dane")
        wyczysc_dane_button.clicked.connect(self.otworz_czyszczenie_danych)

        edytuj_turniej_button.clicked.connect(self.otworz_formularz_edycji_turnieju)  # Podłączenie sygnału

        menu_turniej = QMenu("Turniej", self)

        # Akcje w menu
        dodaj_turniej_action = QAction("Dodaj turniej", self)
        dodaj_turniej_action.triggered.connect(self.otworz_formularz_dodawania_turnieju)
        menu_turniej.addAction(dodaj_turniej_action)

        edytuj_turniej_action = QAction("Edytuj turniej", self)
        edytuj_turniej_action.triggered.connect(self.otworz_formularz_edycji_turnieju)
        menu_turniej.addAction(edytuj_turniej_action)

        wyczysc_dane_action = QAction("Wyczyść dane", self)
        wyczysc_dane_action.triggered.connect(self.otworz_czyszczenie_danych)
        menu_turniej.addAction(wyczysc_dane_action)

        # Przycisk menu
        menu_button = QPushButton("Turniej")
        menu_button.setMenu(menu_turniej)

        # # Dodanie przycisku menu do layoutu
        # header_layout.addWidget(menu_button)


        # Layout główny
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)

        # Przyciski nawigacji
        navigation_layout = QHBoxLayout()
        navigation_layout.addWidget(lista_zawodnikow_button)
        navigation_layout.addWidget(dodaj_zawodnika_button)
        navigation_layout.addWidget(rundy_button)
        navigation_layout.addWidget(prezentacja_button)        
        # navigation_layout.addWidget(dodaj_turniej_button)
        # navigation_layout.addWidget(wyczysc_dane_button)  # Dodanie do layoutu
        # navigation_layout.addWidget(edytuj_turniej_button)
        # Dodanie przycisku menu do layoutu
        navigation_layout.addWidget(menu_button)
        main_layout.addLayout(navigation_layout)


        # QStackedWidget
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Utworzenie widoków
        self.tabela_zawodnikow = TabelaZawodnikow(self.conn, self.turniej_id, self.stacked_widget)
        self.tabela_rund = TabelaRund(self.conn, self.stacked_widget, self.turniej_id)
        self.prezentacja = Prezentacja(self.conn)
        self.formularz_dodawania = FormularzDodawaniaZawodnika(self.conn, self.tabela_zawodnikow)
        # self.okno_lista_rund = TabelaRund(self.conn)
        self.formularz_dodawania_turnieju = FormularzDodawaniaTurnieju(self.conn)
        # ... (utwórz pozostałe widoki) ...

        # Dodanie widoków do QStackedWidget
        self.stacked_widget.addWidget(self.tabela_zawodnikow)
        self.stacked_widget.addWidget(self.tabela_rund)
        self.stacked_widget.addWidget(self.formularz_dodawania)
        self.stacked_widget.addWidget(self.formularz_dodawania_turnieju)
        self.stacked_widget.addWidget(self.prezentacja)
        # ... (dodaj pozostałe widoki) ...

        self.setLayout(main_layout)

        lista_zawodnikow_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.tabela_zawodnikow))
        dodaj_zawodnika_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.formularz_dodawania))
        rundy_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.tabela_rund))
        prezentacja_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.prezentacja))
        dodaj_turniej_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.formularz_dodawania_turnieju))  # Podłączenie sygnału


    def otworz_czyszczenie_danych(self):
        self.czyszczenie_danych_window = CzyszczenieDanych(self.conn)
        self.czyszczenie_danych_window.show()

    def otworz_formularz_edycji_turnieju(self):
        self.formularz_edycji_turnieju = FormularzEdycjiTurnieju(self.conn)
        self.stacked_widget.addWidget(self.formularz_edycji_turnieju)
        self.stacked_widget.setCurrentWidget(self.formularz_edycji_turnieju)

    def otworz_formularz_dodawania_turnieju(self):
        self.formularz_dodawania_turnieju = FormularzDodawaniaTurnieju(self.conn)
        self.stacked_widget.addWidget(self.formularz_dodawania_turnieju)
        self.stacked_widget.setCurrentWidget(self.formularz_dodawania_turnieju)

    def stworz_baze_danych(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turniej (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text NOT NULL, 
                begin_date DATE, 
                tables_number INT,
                rounds_number INT
            )
        ''')
        # Tworzenie tabel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zawodnicy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT,
                lastname TEXT,
                points INTEGER,
                kolejnosc INT DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runda (
                id INTEGER PRIMARY KEY, 
                name text,
                priority INT,
                turniej_id INT NOT NULL,
                FOREIGN KEY (turniej_id) REFERENCES turniej (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gra (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                data DATE NOT NULL, 
                turniej_id INT NOT NULL,
                stol INT NOT NULL,
                runda_id INT NOT NULL,
                zawodnik_1 INT,
                zawodnik_2 INT,
                zawodnik_3 INT,
                zawodnik_4 INT,
                wynik_1 INT,
                wynik_2 INT,
                wynik_3 INT,
                wynik_4 INT
            )
        ''')

        self.conn.commit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ustawienie domyślnej czcionki
    # Załaduj styl CSS
    with open("style.css", "r") as f:
        app.setStyleSheet(f.read())
    font = QFont()
    font.setPointSize(14)  # Ustaw większy rozmiar czcionki
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())