import os # <--- IMPORT OS
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QMessageBox, QHeaderView,
                             QHBoxLayout, QLabel, QAbstractItemView)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from tabela_gier import TabelaGier
from formularz_dodawania_rund import FormularzDodawaniaRundy
import random
from datetime import date

class TabelaRund(QWidget):
    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, stacked_widget, turniej_id, bundle_dir): # <--- ADDED bundle_dir
        super().__init__()
        self.setWindowTitle("Rundy Turniejowe")
        self.conn = conn
        self.stacked_widget = stacked_widget
        self.turniej_id = turniej_id
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here

        # Main layout for this widget
        self.main_layout = QVBoxLayout(self)

        # --- "SKOCKIE ASY" Label (consistent with TabelaZawodnikow) ---
        self.skockie_asy_label = QLabel("SKOCKIE ASY")
        self.skockie_asy_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700; margin-bottom: 10px;")
        self.skockie_asy_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.skockie_asy_label)

        # --- Table Widget ---
        self.table = QTableWidget()
        self.table.setColumnCount(8) # ID, Nazwa, Priorytet, Turniej ID, Szczegóły, Losuj, Wyczyść, Usuń
        self.table.setHorizontalHeaderLabels(["ID", "Nazwa", "Priorytet", "Turniej ID", "Szczegóły", "Losuj", "Wyczyść", "Usuń"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Make cells non-editable by default

        # Crucial for column spreading: Set stretch mode for all horizontal header sections
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.main_layout.addWidget(self.table) # Add table to main layout first

        # --- "Dodaj rundę" Button ---
        self.dodaj_runde_button = QPushButton("Dodaj rundę")
        self.dodaj_runde_button.clicked.connect(self.otworz_formularz_dodawania_rundy)
        self.main_layout.addWidget(self.dodaj_runde_button)

        self.setLayout(self.main_layout)

        self.load_data() # Load data when the widget is initialized

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, priority, turniej_id FROM runda WHERE turniej_id = ?", (self.turniej_id,))
        rundy = cursor.fetchall()

        self.table.setRowCount(len(rundy))
        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels(["ID", "Nazwa", "Priorytet", "Turniej ID", "Szczegóły", "Losuj", "Wyczyść", "Usuń"])

        for i, runda in enumerate(rundy):
            for j in range(4):
                item = QTableWidgetItem(str(runda[j]))
                self.table.setItem(i, j, item)

            runda_id = runda[0]

            # --- Create and style buttons for each cell ---

            # Szczegóły Button (view games in this round)
            szczegoly_button = QPushButton()
            szczegoly_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "eye.png"))) # <--- FIXED PATH
            szczegoly_button.setToolTip("Pokaż szczegóły (gry)")
            szczegoly_button.clicked.connect(lambda _, rid=runda_id: self.pokaz_szczegoly_rundy(rid))
            self.table.setCellWidget(i, 4, szczegoly_button)

            # Losuj (Generate pairings for this round)
            losuj_button = QPushButton()
            losuj_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "draw.png"))) # <--- FIXED PATH
            losuj_button.setToolTip("Losuj gry w rundzie")
            losuj_button.clicked.connect(lambda _, rid=runda_id: self.losuj_gry(rid, self.turniej_id))
            self.table.setCellWidget(i, 5, losuj_button)

            # Wyczyść (Clear games for this round)
            wyczysc_button = QPushButton()
            wyczysc_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "clean.png"))) # <--- FIXED PATH
            wyczysc_button.setToolTip("Wyczyść gry w rundzie")
            wyczysc_button.clicked.connect(lambda _, rid=runda_id: self.wyczysc_gry(rid))
            self.table.setCellWidget(i, 6, wyczysc_button)

            # Usuń (Delete round)
            usun_button = QPushButton()
            usun_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "trash.png"))) # <--- FIXED PATH
            usun_button.setToolTip("Usuń rundę")
            usun_button.clicked.connect(lambda _, rid=runda_id: self.usun_runde(rid))
            self.table.setCellWidget(i, 7, usun_button)

            # Apply consistent styling to all cell buttons
            for button in [szczegoly_button, losuj_button, wyczysc_button, usun_button]:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFD700;
                        color: #1A2E4B;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #FFC400;
                    }
                    QPushButton:pressed {
                        background-color: #E6B800;
                    }
                """)

    def pokaz_szczegoly_rundy(self, runda_id):
        # This also needs bundle_dir if TabelaGier uses external resources
        self.szczegoly_rundy_window = TabelaGier(self.conn, runda_id, self.bundle_dir) # <-- TabelaGier might need bundle_dir too
        self.stacked_widget.addWidget(self.szczegoly_rundy_window)
        self.stacked_widget.setCurrentWidget(self.szczegoly_rundy_window)

    def otworz_formularz_dodawania_rundy(self):
        # Pass self (reference to TabelaRund) as 'tabela_rund' parameter
        self.formularz_dodawania_rundy = FormularzDodawaniaRundy(self.conn, self, self.turniej_id, self.bundle_dir)


        self.stacked_widget.addWidget(self.formularz_dodawania_rundy)
        self.stacked_widget.setCurrentWidget(self.formularz_dodawania_rundy)

    def usun_runde(self, runda_id):
        odpowiedz = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć rundę o ID {runda_id}? To usunie również powiązane gry.",
            QMessageBox.Yes | QMessageBox.No
        )
        if odpowiedz == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM gra WHERE runda_id = ?", (runda_id,))
                cursor.execute("DELETE FROM runda WHERE id = ?", (runda_id,))
                self.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Sukces", "Runda została usunięta.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć rundy: {e}")

    def losuj_gry(self, runda_id, turniej_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT tables_number FROM turniej WHERE id = ?", (turniej_id,))
            turniej_data = cursor.fetchone()
            if not turniej_data:
                QMessageBox.warning(self, "Błąd", "Nie znaleziono danych turnieju.")
                return
            liczba_stolow = turniej_data[0]
            cursor.execute("SELECT id FROM zawodnicy ORDER BY kolejnosc ASC")
            zawodnicy_available = [row[0] for row in cursor.fetchall()]
            if len(zawodnicy_available) < 3:
                QMessageBox.warning(self, "Błąd", "Za mało zawodników, aby utworzyć gry.")
                return
            cursor.execute("SELECT COUNT(*) FROM gra WHERE runda_id = ?", (runda_id,))
            existing_games_count = cursor.fetchone()[0]
            if existing_games_count > 0:
                reply = QMessageBox.question(self, "Istniejące Gry",
                                             f"Runda {runda_id} ma już istniejące gry. Czy chcesz je wyczyścić i wylosować nowe?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.wyczysc_gry(runda_id)
                    cursor.execute("SELECT id FROM zawodnicy ORDER BY kolejnosc ASC")
                    zawodnicy_available = [row[0] for row in cursor.fetchall()]
                    if len(zawodnicy_available) < 3:
                        QMessageBox.warning(self, "Błąd", "Za mało zawodników po wyczyszczeniu, aby utworzyć gry.")
                        return
                else:
                    return

            dzisiejsza_data = date.today().strftime("%Y-%m-%d")
            numer_stolika = 1
            games_to_insert = []

            while len(zawodnicy_available) >= 3:
                if len(zawodnicy_available) >= 4 and (len(zawodnicy_available) % 3 != 0 or len(zawodnicy_available) >= 6):
                    if numer_stolika <= liczba_stolow:
                        p1 = zawodnicy_available.pop(0)
                        p2 = zawodnicy_available.pop(0)
                        p3 = zawodnicy_available.pop(0)
                        p4 = zawodnicy_available.pop(0)
                        games_to_insert.append((dzisiejsza_data, runda_id, turniej_id, numer_stolika, p1, p2, p3, p4, 0, 0, 0, 0))
                        numer_stolika += 1
                    else:
                        if len(zawodnicy_available) >= 3:
                            p1 = zawodnicy_available.pop(0)
                            p2 = zawodnicy_available.pop(0)
                            p3 = zawodnicy_available.pop(0)
                            games_to_insert.append((dzisiejsza_data, runda_id, turniej_id, numer_stolika, p1, p2, p3, None, 0, 0, 0))
                            numer_stolika += 1
                        else:
                            break
                elif len(zawodnicy_available) >= 3:
                    if numer_stolika <= liczba_stolow:
                        p1 = zawodnicy_available.pop(0)
                        p2 = zawodnicy_available.pop(0)
                        p3 = zawodnicy_available.pop(0)
                        games_to_insert.append((dzisiejsza_data, runda_id, turniej_id, numer_stolika, p1, p2, p3, None, 0, 0, 0))
                        numer_stolika += 1
                    else:
                        break
                else:
                    break

            if games_to_insert:
                for game in games_to_insert:
                    if len(game) == 12:
                        cursor.execute('''
                            INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', game)
                    elif len(game) == 11:
                        cursor.execute('''
                            INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, wynik_1, wynik_2, wynik_3)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', game)
                self.conn.commit()
                QMessageBox.information(self, "Sukces", "Gry zostały wylosowane.")
                # You might want to refresh TabelaGier here if it's the target view
                # self.stacked_widget.setCurrentWidget(self.szczegoly_rundy_window) # This will cause an error if szczegoly_rundy_window is not created/added yet.
                                                                                 # If you want to show it, you'll need to create it here.
            else:
                QMessageBox.warning(self, "Błąd", "Nie udało się utworzyć żadnych gier z dostępnych zawodników lub stołów.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wylosować gier: {e}")
            self.conn.rollback()

    def wyczysc_gry(self, runda_id):
        odpowiedz = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć wszystkie gry dla rundy o ID {runda_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if odpowiedz == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM gra WHERE runda_id = ?", (runda_id,))
                self.conn.commit()
                QMessageBox.information(self, "Sukces", "Gry zostały usunięte.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć gier: {e}")