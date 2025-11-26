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
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

from tabela_zawodnikow import TabelaZawodnikow
from tabela_rund import TabelaRund
from tabela_gier import TabelaGier
from tabela_gier2 import TabelaGier2 
from formularz_dodawania_zawodnika import FormularzDodawaniaZawodnika
from formularz_dodawania_rund import FormularzDodawaniaRundy
from formularz_dodawania_turnieju import FormularzDodawaniaTurnieju
from formularz_obliczania_wynikow import FormularzObliczaniaWynikow
from prezentacja import Prezentacja
from widok_zarzadzania_grami import WidokZarzadzaniaGrami
from tabela_wynikow import TabelaWynikow

class MainWindow(QWidget):
    # Removed bundle_dir from __init__ parameters, will define it inside
    def __init__(self):
        super().__init__()

        # --- Define self.bundle_dir here, at the start of MainWindow.__init__ ---
        if getattr(sys, 'frozen', False):
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        # --- End of self.bundle_dir definition ---

        self.setWindowTitle("Turniej Tysiąca")
        # Połączenie z bazą danych
        # Now use self.bundle_dir for db_path
        self.db_path = os.path.join(self.bundle_dir, 'my.db')
        self.conn = sqlite3.connect(self.db_path)
        self.stworz_baze_danych()
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT name, begin_date, id FROM turniej LIMIT 1")
        turniej_data = self.cursor.fetchone()
        
        if turniej_data:
            turniej_name, begin_date, turniej_id = turniej_data
        else:
            turniej_name = "Brak danych turnieju"
            begin_date = ""
            turniej_id = "1"
        
        self.turniej_id = turniej_id
        # Pass self.bundle_dir when initializing Prezentacja
        self.prezentacja = Prezentacja(self.conn, self.bundle_dir) 

        self.main_layout = QVBoxLayout(self)

        # --- TOP SECTION: Logo and Main App Header ---
        top_header_section_layout = QHBoxLayout()
        top_header_section_layout.setAlignment(Qt.AlignVCenter)

        # Add Logo (use self.bundle_dir for logo path)
        self.logo_label = QLabel()
        # Zmieniono na "logo2.png", zgodnie z kodem
        pixmap = QPixmap(os.path.join(self.bundle_dir, "logo2.png")) 
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            print("Warning: logo.png not found or could not be loaded from", os.path.join(self.bundle_dir, "logo2.png"))
            self.logo_label.setText("LOGO")
        top_header_section_layout.addWidget(self.logo_label)

        # ----------------------------------------------------
        # --- ZMIENIONY BLOK: Nagłówek Turnieju (Centrum) ---
        # ----------------------------------------------------
        self.main_app_header_container_layout = QVBoxLayout()
        self.main_app_header_container_layout.setAlignment(Qt.AlignCenter)

        self.main_app_header_label = QLabel(turniej_name)
        self.main_app_header_label.setAlignment(Qt.AlignCenter)
        self.main_app_header_label.setFixedHeight(50) # Dopasowanie do paska
        self.main_app_header_label.setStyleSheet("""
            QLabel {
                background-color: transparent; /* Kluczowe: usuwa białe tło */
                color: #EB414F; /* Czerwony kolor tekstu */
                font-family: 'Verdana', sans-serif;
                font-size: 30px; /* Większa czcionka */
                font-weight: bold;
                padding: 0px; /* Minimalny padding */
                border-radius: 5px;
                border: none; 
            }
        """)
        # KLUCZOWA POPRAWKA: Dodanie etykiety do jej kontenera
        self.main_app_header_container_layout.addWidget(self.main_app_header_label)

        # Dodanie kontenera nagłówka do głównego układu HBox (z rozciąganiem 1)
        top_header_section_layout.addLayout(self.main_app_header_container_layout, 1)

        # top_header_section_layout.addStretch(1) # Usunięto nadmiarowe rozciąganie
        # ----------------------------------------------------
        # ----------------------------------------------------

        self.main_layout.addLayout(top_header_section_layout)

        # --- Dynamic Header (Tournament Name and Date) ---
        dynamic_info_layout = QHBoxLayout()
        dynamic_info_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        dynamic_info_layout.setContentsMargins(0, 0, 10, 5)

        # Etykieta daty
        # ZMIANA 1: Zapisano 'date_label' jako 'self.date_label'
        self.date_label = QLabel(f"Data: {begin_date}")
        self.date_label.setStyleSheet("color: #1A1A1A; font-size: 10px;") # Ciemny tekst na jasnym tle

        dynamic_info_layout.addStretch(1)
        dynamic_info_layout.addWidget(self.date_label) # Zaktualizowano na self.date_label

        # self.main_layout.addLayout(dynamic_info_layout)


        # --- Navigation Buttons ---
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        navigation_layout.setContentsMargins(1, 0, 1, 1)

        lista_zawodnikow_button = QPushButton("Lista zawodników")
        dodaj_zawodnika_button = QPushButton("Dodaj zawodnika")
        rundy_button = QPushButton("Rundy")
        prezentacja_button = QPushButton("Prezentacja")
        wyniki_button = QPushButton("Wyniki")

        menu_turniej = QMenu("Turniej", self)
        dodaj_turniej_action = QAction("Dodaj turniej", self)
        dodaj_turniej_action.triggered.connect(self.otworz_formularz_dodawania_turnieju)
        menu_turniej.addAction(dodaj_turniej_action)

        edytuj_turniej_action = QAction("Edytuj turniej", self)
        edytuj_turniej_action.triggered.connect(self.otworz_formularz_edycji_turnieju)
        menu_turniej.addAction(edytuj_turniej_action)

        wyczysc_dane_action = QAction("Wyczyść dane", self)
        wyczysc_dane_action.triggered.connect(self.otworz_czyszczenie_danych)
        menu_turniej.addAction(wyczysc_dane_action)

        menu_button = QPushButton("Turniej")
        menu_button.setMenu(menu_turniej)

        navigation_layout.addWidget(lista_zawodnikow_button)
        navigation_layout.addWidget(dodaj_zawodnika_button)
        navigation_layout.addWidget(rundy_button)
        navigation_layout.addWidget(prezentacja_button)
        navigation_layout.addWidget(wyniki_button)
        navigation_layout.addStretch(1)
        navigation_layout.addWidget(menu_button)

        self.main_layout.addLayout(navigation_layout)


        # --- Stacked Widget (Main Content Area) ---
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)

        # Utworzenie widoków (Pass self.bundle_dir to all relevant constructors)
        self.tabela_zawodnikow = TabelaZawodnikow(self.conn, self.turniej_id, self.stacked_widget, self.bundle_dir) 
        self.tabela_rund = TabelaRund(self.conn, self.stacked_widget, self.turniej_id, self.bundle_dir) 
        self.tabela_wynikow = TabelaWynikow(self.conn, self.stacked_widget, self.bundle_dir)
        self.formularz_obliczania_wynikow = FormularzObliczaniaWynikow(self.conn, self.bundle_dir)
        self.tabela_wynikow.open_calculate_form.connect(self.show_calculate_form)
        self.formularz_obliczania_wynikow.results_calculated.connect(self.tabela_wynikow.load_data)
        # Prezentacja is already done above
        self.formularz_dodawania = FormularzDodawaniaZawodnika(self.conn, self.tabela_zawodnikow, self.bundle_dir) 
        self.formularz_dodawania_turnieju = FormularzDodawaniaTurnieju(self.conn, self.bundle_dir) 

        self.formularz_dodawania.player_added.connect(self.show_players_list)

        # Dodanie widoków do QStackedWidget
        self.stacked_widget.addWidget(self.tabela_zawodnikow)
        self.stacked_widget.addWidget(self.tabela_rund)
        self.stacked_widget.addWidget(self.tabela_wynikow)
        self.stacked_widget.addWidget(self.formularz_obliczania_wynikow)
        self.stacked_widget.addWidget(self.formularz_dodawania)
        self.stacked_widget.addWidget(self.formularz_dodawania_turnieju)
        self.stacked_widget.addWidget(self.prezentacja)

        lista_zawodnikow_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.tabela_zawodnikow))
        dodaj_zawodnika_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.formularz_dodawania))
        rundy_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.tabela_rund))
        prezentacja_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.prezentacja))
        wyniki_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.tabela_wynikow))

        # --- FOOTER ---
        self.footer_label = QLabel("@2025 Autor Aron Becker")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("""
            QLabel {
                color: #1A1A1A; /* Ciemny tekst na jasnym tle */
                font-size: 12px;
                padding: 5px;
                margin-top: 5px;
            }
        """)
        self.main_layout.addWidget(self.footer_label)

    # ZMIANA 2: Dodano nową funkcję do odświeżania etykiet
    def odswiez_dane_turnieju(self):
        """Ta funkcja jest wywoływana przez sygnał z formularza edycji."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, begin_date FROM turniej WHERE id = ?", (self.turniej_id,))
            turniej_data = cursor.fetchone()
            if turniej_data:
                # Zaktualizuj etykiety o nowe dane
                self.main_app_header_label.setText(turniej_data[0])
                self.date_label.setText(f"Data: {turniej_data[1]}")
                print("Interfejs główny odświeżony.") # Wiadomość dla Ciebie
            else:
                print("Nie udało się odświeżyć danych (nie znaleziono turnieju).")
        except Exception as e:
            print(f"Błąd podczas odświeżania danych turnieju: {e}")


    def otworz_czyszczenie_danych(self):
        self.czyszczenie_danych_window = CzyszczenieDanych(self.conn)
        self.czyszczenie_danych_window.show()

    def otworz_formularz_edycji_turnieju(self):
        self.formularz_edycji_turnieju = FormularzEdycjiTurnieju(self.conn)
        
        # ZMIANA 3: Podłączenie sygnału z formularza do funkcji odświeżającej
        self.formularz_edycji_turnieju.zmiany_zapisane.connect(self.odswiez_dane_turnieju)
        
        self.stacked_widget.addWidget(self.formularz_edycji_turnieju)
        self.stacked_widget.setCurrentWidget(self.formularz_edycji_turnieju)

    def otworz_formularz_dodawania_turnieju(self):
        self.formularz_dodawania_turnieju = FormularzDodawaniaTurnieju(self.conn, self.bundle_dir)
        self.stacked_widget.addWidget(self.formularz_dodawania_turnieju)
        self.stacked_widget.setCurrentWidget(self.formularz_dodawania_turnieju)

    def show_players_list(self):
        self.stacked_widget.setCurrentWidget(self.tabela_zawodnikow)
    
    def show_calculate_form(self):
        self.stacked_widget.setCurrentWidget(self.formularz_obliczania_wynikow)

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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wyniki (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                punkty INTEGER NOT NULL,
                turnament INTEGER NOT NULL,
                tdate DATE NOT NULL
            )
        ''')

        self.conn.commit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Determine the base path for bundled resources (like style.css, logo.png, icons)
    # This logic remains here for the main application stylesheet loading.
    if getattr(sys, 'frozen', False):
        bundle_dir_for_app_stylesheet = sys._MEIPASS
    else:
        bundle_dir_for_app_stylesheet = os.path.dirname(os.path.abspath(__file__))

    style_sheet_path = os.path.join(bundle_dir_for_app_stylesheet, "style.css")
    try:
        with open(style_sheet_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Error: style.css not found at {style_sheet_path}. Running without stylesheet.")
    except Exception as e:
        print(f"Error loading stylesheet: {e}")

    font = QFont()
    font.setPointSize(14)
    app.setFont(font)
    window = MainWindow() 
    window.show()
    sys.exit(app.exec_())