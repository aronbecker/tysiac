from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QMessageBox, QComboBox,
                             QHBoxLayout, QHeaderView, QAbstractItemView, QLabel, QLineEdit) # Added QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt # Import Qt for alignment

from formularz_edycji_zawodnika import FormularzEdycjiZawodnika
from tabela_gier_zawodnika import TabelaGierZawodnika

import random

class TabelaZawodnikow(QWidget):
    def __init__(self, conn, turniej_id, stacked_widget):
        super().__init__()
        self.setWindowTitle("Lista Zawodników")
        self.stacked_widget = stacked_widget
        self.conn = conn # Ensure conn is set here for all methods
        self.turniej_id = turniej_id

        # Main layout for this specific widget (TabelaZawodnikow)
        self.main_layout = QVBoxLayout(self) # <-- Set this as the main layout for TabelaZawodnikow

        # --- "SKOCKIE ASY" Label (as seen in screenshot) ---
        self.skockie_asy_label = QLabel("SKOCKIE ASY")
        # Apply styling from your CSS if you want, or here directly
        self.skockie_asy_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700; margin-bottom: 10px;")
        self.skockie_asy_label.setAlignment(Qt.AlignCenter) # Center the text
        self.main_layout.addWidget(self.skockie_asy_label)

        # --- Filtering/Sorting Controls (Top Row below SKOCKIE ASY) ---
        self.filter_sort_layout = QHBoxLayout()

        self.filter_id_label = QLabel("ID:")
        self.filter_id_input = QLineEdit()
        self.filter_id_input.setPlaceholderText("Filtruj po ID")
        self.filter_id_input.textChanged.connect(self.load_data) # Live filter

        self.sort_column_combo = QComboBox()
        self.sort_column_combo.addItems(["id", "firstname", "lastname", "points", "kolejnosc"])
        self.sort_column_combo.currentIndexChanged.connect(self.load_data) # Re-load on sort change

        self.sort_direction_combo = QComboBox() # Renamed to avoid conflict with sort_direction variable
        self.sort_direction_combo.addItems(["ASC", "DESC"])
        self.sort_direction_combo.currentIndexChanged.connect(self.load_data) # Re-load on sort change

        # Add widgets to sort_layout
        self.filter_sort_layout.addWidget(self.filter_id_label)
        self.filter_sort_layout.addWidget(self.filter_id_input)
        self.filter_sort_layout.addStretch(1) # Pushes elements to the left
        self.filter_sort_layout.addWidget(QLabel("Sortuj po:"))
        self.filter_sort_layout.addWidget(self.sort_column_combo)
        self.filter_sort_layout.addWidget(self.sort_direction_combo)
        # Removed the separate "Sortuj" button as sorting will happen on combo box change
        # If you still want a button, keep it and connect it to load_data()

        self.main_layout.addLayout(self.filter_sort_layout) # Add this layout to the main layout

        # --- Action Buttons (Losuj, Ustaw, Oblicz) ---
        self.action_buttons_layout = QHBoxLayout() # Use QHBoxLayout for horizontal buttons

        self.losuj_kolejnosc_button = QPushButton("Losuj kolejność")
        self.losuj_kolejnosc_button.clicked.connect(self.losuj_kolejnosc)
        self.action_buttons_layout.addWidget(self.losuj_kolejnosc_button)

        self.ustaw_kolejnosc_button = QPushButton("Ustaw kolejność wg punktów")
        self.ustaw_kolejnosc_button.clicked.connect(self.ustaw_kolejnosc_wg_punktow)
        self.action_buttons_layout.addWidget(self.ustaw_kolejnosc_button)

        self.oblicz_wszystkich_button = QPushButton("Oblicz punkty dla wszystkich")
        self.oblicz_wszystkich_button.clicked.connect(self.oblicz_punkty_wszystkich)
        self.action_buttons_layout.addWidget(self.oblicz_wszystkich_button)

        self.main_layout.addLayout(self.action_buttons_layout) # Add this layout to the main layout

        # --- Table Widget ---
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Imię", "Nazwisko", "Punkty", "Kolejność", "Oblicz", "Szczegóły", "Usuń", "Edytuj"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)


        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table) # Add the table to the main layout of this widget

        self.setLayout(self.main_layout) # <-- IMPORTANT: Set the main_layout for the QWidget itself

        self.load_data() # Initial data load

    def load_data(self):
        self.cursor = self.conn.cursor()

        # Get sorting and filtering parameters
        sort_column = self.sort_column_combo.currentText()
        sort_direction = self.sort_direction_combo.currentText() # Use the corrected combo box name
        filter_id = self.filter_id_input.text().strip()

        query = "SELECT id, firstname, lastname, points, kolejnosc FROM zawodnicy"
        params = []

        if filter_id:
            query += " WHERE id = ?"
            params.append(filter_id)

        query += f" ORDER BY {sort_column} {sort_direction}"

        self.cursor.execute(query, tuple(params)) # Pass parameters as a tuple
        data = self.cursor.fetchall()

        self.table.setRowCount(len(data))
        self.table.setColumnCount(9) # Always 9 columns for data + 4 buttons

        # Set headers (already done in __init__, but useful if column count changes dynamically)
        self.table.setHorizontalHeaderLabels(["ID", "Imię", "Nazwisko", "Punkty", "Kolejność", "Oblicz","Szczegóły","Usuń", "Edytuj"])

        # Populate table with data and buttons
        for row_index, row_data in enumerate(data):
            # Data columns
            for col_index in range(5): # First 5 columns are data (ID, Imię, Nazwisko, Punkty, Kolejność)
                item = QTableWidgetItem(str(row_data[col_index]))
                self.table.setItem(row_index, col_index, item)

            zawodnik_id = row_data[0] # Assuming ID is the first column

            # Button "Oblicz"
            oblicz_button = QPushButton()
            oblicz_button.setIcon(QIcon("icons/calculator.png"))
            oblicz_button.setToolTip("Oblicz punkty")
            oblicz_button.clicked.connect(lambda _, zid=zawodnik_id: self.oblicz_punkty(zid, self.turniej_id))
            self.table.setCellWidget(row_index, 5, oblicz_button)

            # Button "Szczegóły"
            szczegoly_button = QPushButton()
            szczegoly_button.setIcon(QIcon("icons/eye.png"))
            szczegoly_button.setToolTip("Pokaż szczegóły")
            szczegoly_button.clicked.connect(lambda _, zid=zawodnik_id: self.pokaz_szczegoly_zawodnika(zid))
            self.table.setCellWidget(row_index, 6, szczegoly_button)

            # Button "Usuń"
            usun_button = QPushButton()
            usun_button.setIcon(QIcon("icons/trash.png"))
            usun_button.setToolTip("Usuń zawodnika")
            usun_button.clicked.connect(lambda _, zid=zawodnik_id: self.usun_zawodnika(zid))
            self.table.setCellWidget(row_index, 7, usun_button)

            # Button "Edytuj"
            edytuj_button = QPushButton()
            edytuj_button.setIcon(QIcon("icons/pencil.png"))
            edytuj_button.setToolTip("Edytuj zawodnika")
            edytuj_button.clicked.connect(lambda _, zid=zawodnik_id: self.edytuj_zawodnika(zid))
            self.table.setCellWidget(row_index, 8, edytuj_button)

            # Apply button styling (optional, but good for consistency)
            for button in [oblicz_button, szczegoly_button, usun_button, edytuj_button]:
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

        # self.table.resizeColumnsToContents()
        # self.table.horizontalHeader().setStretchLastSection(True) # Make last section stretch to fill space


    def oblicz_punkty(self, zawodnik_id, turniej_id):
        try:
            cursor = self.conn.cursor()

            # Pobranie wyników gier danego zawodnika (zakładając, że wyniki są w tabeli `gra`)
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN zawodnik_1 = ? THEN wynik_1 ELSE 0 END) +
                    SUM(CASE WHEN zawodnik_2 = ? THEN wynik_2 ELSE 0 END) +
                    SUM(CASE WHEN zawodnik_3 = ? THEN wynik_3 ELSE 0 END) +
                    SUM(CASE WHEN zawodnik_4 = ? THEN wynik_4 ELSE 0 END)
                FROM gra
                WHERE turniej_id = ?
            """, (zawodnik_id, zawodnik_id, zawodnik_id, zawodnik_id, turniej_id))
            punkty = cursor.fetchone()[0]
            if punkty is None: # Handle case where no games are found for the player
                punkty = 0

            # Aktualizacja punktów w tabeli `zawodnicy`
            cursor.execute("UPDATE zawodnicy SET points = ? WHERE id = ?", (punkty, zawodnik_id))
            self.conn.commit()

            # Odświeżenie tabeli
            self.load_data()

            # QMessageBox.information(self, "Sukces", f"Punkty zawodnika {zawodnik_id} zostały zaktualizowane.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów: {e}")

    def sort_zawodnicy(self):
        """No longer needed as load_data() handles sorting on combo box change."""
        # This method is now implicitly called by load_data via connect
        self.load_data()

    def losuj_kolejnosc(self):
        """Losuje kolejność zawodników i aktualizuje tabelę."""
        try:
            cursor = self.conn.cursor()

            # Pobranie ID wszystkich zawodników
            cursor.execute("SELECT id FROM zawodnicy")
            zawodnicy_id = [row[0] for row in cursor.fetchall()]

            # Losowanie kolejności
            random.shuffle(zawodnicy_id)

            # Aktualizacja kolejności w bazie danych
            for i, zawodnik_id in enumerate(zawodnicy_id):
                cursor.execute("UPDATE zawodnicy SET kolejnosc = ? WHERE id = ?", (i + 1, zawodnik_id))

            self.conn.commit()
            self.load_data()  # Odświeżenie tabeli

            QMessageBox.information(self, "Sukces", "Kolejność zawodników została wylosowana.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wylosować kolejności: {e}")

    def ustaw_kolejnosc_wg_punktow(self):
        """Ustawia kolejność zawodników na podstawie punktów."""
        try:
            cursor = self.conn.cursor()

            # Pobranie ID i punktów wszystkich zawodników, posortowanych malejąco wg punktów
            cursor.execute("SELECT id, points FROM zawodnicy ORDER BY points DESC")
            zawodnicy = cursor.fetchall()

            # Aktualizacja kolejności w bazie danych
            for i, (zawodnik_id, _) in enumerate(zawodnicy):
                cursor.execute("UPDATE zawodnicy SET kolejnosc = ? WHERE id = ?", (i + 1, zawodnik_id))

            self.conn.commit()
            self.load_data()  # Odświeżenie tabeli

            QMessageBox.information(self, "Sukces", "Kolejność zawodników została ustawiona wg punktów.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się ustawić kolejności: {e}")

    def oblicz_punkty_wszystkich(self):
        """Oblicza punkty dla wszystkich zawodników na liście."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM zawodnicy")  # Pobranie ID wszystkich zawodników
            zawodnicy_id = [row[0] for row in cursor.fetchall()]

            for zawodnik_id in zawodnicy_id:
                self.oblicz_punkty(zawodnik_id, self.turniej_id)  # Wywołanie oblicz_punkty dla każdego zawodnika
            QMessageBox.information(self, "Sukces", "Punkty dla wszystkich zawodników zostały przeliczone.") # Add a success message after all points are calculated

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów: {e}")

    def usun_zawodnika(self, zawodnik_id):
        """Usuwa zawodnika z bazy danych."""
        # Potwierdzenie usunięcia
        odpowiedz = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć zawodnika o ID {zawodnik_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if odpowiedz == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM zawodnicy WHERE id = ?", (zawodnik_id,))
                self.conn.commit()
                self.load_data()  # Odświeżenie tabeli po usunięciu
                QMessageBox.information(self, "Sukces", "Zawodnik został usunięty.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć zawodnika: {e}")

    def edytuj_zawodnika(self, zawodnik_id):
        """Otwiera formularz edycji zawodnika."""
        self.formularz_edycji = FormularzEdycjiZawodnika(self.conn, zawodnik_id, self)  # Przekazanie referencji do self
        self.stacked_widget.addWidget(self.formularz_edycji)
        self.stacked_widget.setCurrentWidget(self.formularz_edycji)


    def pokaz_szczegoly_zawodnika(self, zawodnik_id):
        """Otwiera widok wszystkich gier, w których uczestniczył zawodnik."""
        # Create a new instance each time to ensure fresh data
        self.szczegoly_zawodnika_window = TabelaGierZawodnika(self.conn, zawodnik_id)
        self.stacked_widget.addWidget(self.szczegoly_zawodnika_window)
        self.stacked_widget.setCurrentWidget(self.szczegoly_zawodnika_window)