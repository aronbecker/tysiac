from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QMessageBox, QHeaderView,
                             QHBoxLayout, QLabel, QAbstractItemView) # <--- Add QAbstractItemView here!
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from tabela_gier import TabelaGier
from formularz_dodawania_rund import FormularzDodawaniaRundy
import random
from datetime import date

# Rest of your TabelaRund class code...

class TabelaRund(QWidget):
    def __init__(self, conn, stacked_widget, turniej_id):
        super().__init__()
        self.setWindowTitle("Rundy Turniejowe")
        # Remove setFixedSize to allow layout to manage sizing
        # self.setFixedSize(1200, 900)

        self.conn = conn
        self.stacked_widget = stacked_widget
        self.turniej_id = turniej_id

        # Main layout for this widget
        self.main_layout = QVBoxLayout(self) # Set QVBoxLayout for the widget

        # --- "SKOCKIE ASY" Label (consistent with TabelaZawodnikow) ---
        self.skockie_asy_label = QLabel("SKOCKIE ASY")
        self.skockie_asy_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700; margin-bottom: 10px;")
        self.skockie_asy_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.skockie_asy_label)

        # --- Table Widget ---
        self.table = QTableWidget()
        self.table.setColumnCount(8) # ID, Nazwa, Priorytet, Turniej ID, Szczegóły, Losuj, Wyczyść, Usuń
        self.table.setHorizontalHeaderLabels(["ID", "Nazwa", "Priorytet", "Turniej ID", "Szczegóły", "Losuj", "Wyczyść", "Usuń"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # Import QAbstractItemView
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Make cells non-editable by default

        # Crucial for column spreading: Set stretch mode for all horizontal header sections
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.main_layout.addWidget(self.table) # Add table to main layout first

        # --- "Dodaj rundę" Button ---
        # No need for a separate 'layout' variable, use self.main_layout directly
        self.dodaj_runde_button = QPushButton("Dodaj rundę")
        self.dodaj_runde_button.clicked.connect(self.otworz_formularz_dodawania_rundy)
        self.main_layout.addWidget(self.dodaj_runde_button) # Add button to main layout

        self.setLayout(self.main_layout) # Set the main layout for the widget

        self.load_data() # Load data when the widget is initialized

    def load_data(self):
        cursor = self.conn.cursor()
        # Fetch rounds for the current tournament_id
        cursor.execute("SELECT id, name, priority, turniej_id FROM runda WHERE turniej_id = ?", (self.turniej_id,))
        rundy = cursor.fetchall()

        self.table.setRowCount(len(rundy))
        self.table.setColumnCount(8) # Data columns + button columns

        self.table.setHorizontalHeaderLabels(["ID", "Nazwa", "Priorytet", "Turniej ID", "Szczegóły", "Losuj", "Wyczyść", "Usuń"])

        for i, runda in enumerate(rundy):
            # Populate data columns (first 4 columns)
            for j in range(4):
                item = QTableWidgetItem(str(runda[j])) # Use runda[j] directly
                self.table.setItem(i, j, item)

            runda_id = runda[0] # Assuming ID is the first column

            # --- Create and style buttons for each cell ---

            # Szczegóły Button (view games in this round)
            szczegoly_button = QPushButton()
            szczegoly_button.setIcon(QIcon("icons/eye.png")) # Using consistent icon
            szczegoly_button.setToolTip("Pokaż szczegóły (gry)")
            szczegoly_button.clicked.connect(lambda _, rid=runda_id: self.pokaz_szczegoly_rundy(rid))
            self.table.setCellWidget(i, 4, szczegoly_button) # Column 4

            # Losuj (Generate pairings for this round)
            losuj_button = QPushButton()
            losuj_button.setIcon(QIcon("icons/draw.png")) # Assuming a shuffle icon. Ensure this icon exists.
            losuj_button.setToolTip("Losuj gry w rundzie")
            losuj_button.clicked.connect(lambda _, rid=runda_id: self.losuj_gry(rid, self.turniej_id))
            self.table.setCellWidget(i, 5, losuj_button) # Column 5

            # Wyczyść (Clear games for this round)
            wyczysc_button = QPushButton()
            wyczysc_button.setIcon(QIcon("icons/clean.png")) # Assuming a clear icon. Ensure this icon exists.
            wyczysc_button.setToolTip("Wyczyść gry w rundzie")
            wyczysc_button.clicked.connect(lambda _, rid=runda_id: self.wyczysc_gry(rid))
            self.table.setCellWidget(i, 6, wyczysc_button) # Column 6

            # Usuń (Delete round)
            usun_button = QPushButton()
            usun_button.setIcon(QIcon("icons/trash.png")) # Using consistent icon
            usun_button.setToolTip("Usuń rundę")
            usun_button.clicked.connect(lambda _, rid=runda_id: self.usun_runde(rid))
            self.table.setCellWidget(i, 7, usun_button) # Column 7

            # Apply consistent styling to all cell buttons
            for button in [szczegoly_button, losuj_button, wyczysc_button, usun_button]:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFD700; /* Golden yellow */
                        color: #1A2E4B; /* Dark blue for text on buttons */
                        border: none;
                        padding: 5px; /* Smaller padding for cell buttons */
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
        # Removed resizeColumnsToContents() here, as QHeaderView.Stretch handles it.
        # If you want initial "snug fit" before stretching, you can keep it.
        # self.table.resizeColumnsToContents()

    # --- Methods for button actions ---

    def pokaz_szczegoly_rundy(self, runda_id):
        self.szczegoly_rundy_window = TabelaGier(self.conn, runda_id)
        self.stacked_widget.addWidget(self.szczegoly_rundy_window)
        self.stacked_widget.setCurrentWidget(self.szczegoly_rundy_window)

    def otworz_formularz_dodawania_rundy(self):
        # Assuming FormularzDodawaniaRundy has a signal like 'round_added'
        self.formularz_dodawania_rundy = FormularzDodawaniaRundy(self.conn, self.turniej_id)
        self.formularz_dodawania_rundy.round_added.connect(self.load_data) # Connect to refresh table
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
                # Ensure transactions to delete associated games first
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

            cursor.execute("SELECT id FROM zawodnicy ORDER BY kolejnosc ASC") # Order by 'kolejnosc' for fair distribution
            zawodnicy_available = [row[0] for row in cursor.fetchall()]

            if len(zawodnicy_available) < 3:
                QMessageBox.warning(self, "Błąd", "Za mało zawodników, aby utworzyć gry.")
                return

            # Check for existing games in this round to prevent duplicates on re-roll
            cursor.execute("SELECT COUNT(*) FROM gra WHERE runda_id = ?", (runda_id,))
            existing_games_count = cursor.fetchone()[0]
            if existing_games_count > 0:
                reply = QMessageBox.question(self, "Istniejące Gry",
                                             f"Runda {runda_id} ma już istniejące gry. Czy chcesz je wyczyścić i wylosować nowe?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.wyczysc_gry(runda_id) # Call the clear method
                    # After clearing, reload available players if necessary, or assume it's fresh
                    cursor.execute("SELECT id FROM zawodnicy ORDER BY kolejnosc ASC")
                    zawodnicy_available = [row[0] for row in cursor.fetchall()]
                    if len(zawodnicy_available) < 3: # Re-check after clearing
                        QMessageBox.warning(self, "Błąd", "Za mało zawodników po wyczyszczeniu, aby utworzyć gry.")
                        return
                else:
                    return # User cancelled

            # Randomize only if not ordering by points, or for specific rules.
            # If 'kolejnosc' already defines the order for pairings, don't shuffle here.
            # If you want to use the 'kolejnosc' as a base but still randomize groups,
            # you might need a more complex pairing algorithm. For now, we'll
            # assume 'kolejnosc' provides the order.
            # random.shuffle(zawodnicy_available) # Uncomment if you want full randomization regardless of 'kolejnosc'

            dzisiejsza_data = date.today().strftime("%Y-%m-%d")
            numer_stolika = 1
            games_to_insert = []
            
            # Simple pairing logic based on available players, trying for 4-player games first
            while len(zawodnicy_available) >= 3:
                if len(zawodnicy_available) >= 4 and (len(zawodnicy_available) % 3 != 0 or len(zawodnicy_available) >= 6): # Prioritize 4-player games, but avoid leaving 1 or 2 players if total is for 3-player tables
                    # Try to form 4-player games
                    if numer_stolika <= liczba_stolow: # Check if we have tables available
                        p1 = zawodnicy_available.pop(0)
                        p2 = zawodnicy_available.pop(0)
                        p3 = zawodnicy_available.pop(0)
                        p4 = zawodnicy_available.pop(0)
                        games_to_insert.append((dzisiejsza_data, runda_id, turniej_id, numer_stolika, p1, p2, p3, p4, 0, 0, 0, 0))
                        numer_stolika += 1
                    else: # No more tables for 4-player, try 3-player if enough
                        if len(zawodnicy_available) >= 3:
                            p1 = zawodnicy_available.pop(0)
                            p2 = zawodnicy_available.pop(0)
                            p3 = zawodnicy_available.pop(0)
                            games_to_insert.append((dzisiejsza_data, runda_id, turniej_id, numer_stolika, p1, p2, p3, None, 0, 0, 0)) # None for p4, 3 zeros for scores
                            numer_stolika += 1
                        else: # Can't form any more games
                            break
                elif len(zawodnicy_available) >= 3:
                    # Form 3-player games
                    if numer_stolika <= liczba_stolow: # Check if we have tables available
                        p1 = zawodnicy_available.pop(0)
                        p2 = zawodnicy_available.pop(0)
                        p3 = zawodnicy_available.pop(0)
                        games_to_insert.append((dzisiejsza_data, runda_id, turniej_id, numer_stolika, p1, p2, p3, None, 0, 0, 0)) # None for p4, 3 zeros for scores
                        numer_stolika += 1
                    else: # No more tables
                        break
                else: # Less than 3 players left
                    break

            if games_to_insert:
                for game in games_to_insert:
                    if len(game) == 12: # 4 players game
                        cursor.execute('''
                            INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', game)
                    elif len(game) == 11: # 3 players game
                        cursor.execute('''
                            INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, wynik_1, wynik_2, wynik_3)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', game)
                self.conn.commit()
                QMessageBox.information(self, "Sukces", "Gry zostały wylosowane.")
                # You might want to refresh TabelaGier here if it's the target view
                self.stacked_widget.setCurrentWidget(self.szczegoly_rundy_window) # Assuming you want to show games after creation
            else:
                QMessageBox.warning(self, "Błąd", "Nie udało się utworzyć żadnych gier z dostępnych zawodników lub stołów.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wylosować gier: {e}")
            self.conn.rollback() # Rollback changes if an error occurs

    def wyczysc_gry(self, runda_id):
        """Usuwa wszystkie gry przypisane do danej rundy."""
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
                # After clearing games, refresh TabelaGier if it's visible, or just load_data() if needed
                # self.load_data() # Only if clearing games affects something in this table
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć gier: {e}")