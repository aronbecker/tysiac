import os # <--- IMPORT OS
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QMessageBox, QComboBox,
                             QHBoxLayout, QHeaderView, QAbstractItemView, QLabel, QLineEdit, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt # Import Qt for alignment

from formularz_edycji_zawodnika import FormularzEdycjiZawodnika
from tabela_gier_zawodnika import TabelaGierZawodnika

import openpyxl
import random

class TabelaZawodnikow(QWidget):
    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, turniej_id, stacked_widget, bundle_dir): # <--- ADDED bundle_dir
        super().__init__()
        self.setWindowTitle("Lista Zawodników")
        self.stacked_widget = stacked_widget
        self.conn = conn
        self.turniej_id = turniej_id
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here

        # Main layout for this specific widget (TabelaZawodnikow)
        self.main_layout = QVBoxLayout(self)

        # Removed the commented-out "SKOCKIE ASY" label for clarity since it's in MainWindow now.
        # # --- "SKOCKIE ASY" Label (as seen in screenshot) ---
        # self.skockie_asy_label = QLabel("SKOCKIE ASY")
        # # Apply styling from your CSS if you want, or here directly
        # self.skockie_asy_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700; margin-bottom: 10px;")
        # self.skockie_asy_label.setAlignment(Qt.AlignCenter)
        # self.main_layout.addWidget(self.skockie_asy_label)

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

        # --- Przycisk Eksportu ---
        self.export_button = QPushButton("Eksportuj do XLSX")
        self.export_button.clicked.connect(self.export_to_xlsx)
        self.filter_sort_layout.addWidget(self.export_button)
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
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Make cells non-editable

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table) # Add the table to the main layout of this widget

        self.setLayout(self.main_layout) # Set the main_layout for the QWidget itself

        self.load_data() # Initial data load

    def load_data(self):
        self.cursor = self.conn.cursor()

        # Get sorting and filtering parameters
        sort_column = self.sort_column_combo.currentText()
        sort_direction = self.sort_direction_combo.currentText()
        filter_id = self.filter_id_input.text().strip()

        query = "SELECT id, firstname, lastname, points, kolejnosc FROM zawodnicy"
        params = []

        if filter_id:
            query += " WHERE id = ?"
            params.append(filter_id)

        query += f" ORDER BY {sort_column} {sort_direction}"

        self.cursor.execute(query, tuple(params))
        data = self.cursor.fetchall()

        self.table.setRowCount(len(data))
        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels(["ID", "Imię", "Nazwisko", "Punkty", "Kolejność", "Oblicz","Szczegóły","Usuń", "Edytuj"])

        # Populate table with data and buttons
        for row_index, row_data in enumerate(data):
            # Data columns
            for col_index in range(5):
                item = QTableWidgetItem(str(row_data[col_index]))
                self.table.setItem(row_index, col_index, item)

            zawodnik_id = row_data[0]

            # Button "Oblicz"
            oblicz_button = QPushButton()
            oblicz_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "calculator.png"))) # <--- FIXED PATH
            oblicz_button.setToolTip("Oblicz punkty")
            oblicz_button.clicked.connect(lambda _, zid=zawodnik_id: self.oblicz_punkty(zid, self.turniej_id))
            self.table.setCellWidget(row_index, 5, oblicz_button)

            # Button "Szczegóły"
            szczegoly_button = QPushButton()
            szczegoly_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "eye.png"))) # <--- FIXED PATH
            szczegoly_button.setToolTip("Pokaż szczegóły")
            szczegoly_button.clicked.connect(lambda _, zid=zawodnik_id: self.pokaz_szczegoly_zawodnika(zid))
            self.table.setCellWidget(row_index, 6, szczegoly_button)

            # Button "Usuń"
            usun_button = QPushButton()
            usun_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "trash.png"))) # <--- FIXED PATH
            usun_button.setToolTip("Usuń zawodnika")
            usun_button.clicked.connect(lambda _, zid=zawodnik_id: self.usun_zawodnika(zid))
            self.table.setCellWidget(row_index, 7, usun_button)

            # Button "Edytuj"
            edytuj_button = QPushButton()
            edytuj_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "pencil.png"))) # <--- FIXED PATH
            edytuj_button.setToolTip("Edytuj zawodnika")
            edytuj_button.clicked.connect(lambda _, zid=zawodnik_id: self.edytuj_zawodnika(zid))
            self.table.setCellWidget(row_index, 8, edytuj_button)

            # Apply button styling (optional, but good for consistency)
            for button in [oblicz_button, szczegoly_button, usun_button, edytuj_button]:
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

    def export_to_xlsx(self):
        # Otwórz okno dialogowe zapisu pliku
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Eksportuj listę zawodników", "lista_zawodnikow.xlsx",
                                                   "Pliki Excel (*.xlsx);;Wszystkie pliki (*)", options=options)

        if file_name: # Jeśli użytkownik wybrał plik
            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Lista Zawodników"

                # Dodaj nagłówki kolumn
                headers = []
                for col in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(col)
                    if header_item is not None:
                        headers.append(header_item.text())
                    else:
                        headers.append(f"Kolumna {col+1}") # Fallback
                sheet.append(headers)

                # Dodaj dane z tabeli
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        # Sprawdź, czy komórka zawiera widget (przycisk)
                        if self.table.cellWidget(row, col) is None:
                            item = self.table.item(row, col)
                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append("")
                        else:
                            row_data.append("") # Nie eksportuj danych z komórek z widgetami (przyciskami)
                    sheet.append(row_data)

                workbook.save(file_name)
                QMessageBox.information(self, "Eksport zakończony", f"Dane zostały pomyślnie wyeksportowane do: {file_name}")

            except Exception as e:
                QMessageBox.critical(self, "Błąd eksportu", f"Wystąpił błąd podczas eksportowania danych: {e}")
        else:
            QMessageBox.information(self, "Eksport anulowany", "Eksport danych został anulowany.")



    def oblicz_punkty(self, zawodnik_id, turniej_id):
        try:
            cursor = self.conn.cursor()

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
            if punkty is None:
                punkty = 0

            cursor.execute("UPDATE zawodnicy SET points = ? WHERE id = ?", (punkty, zawodnik_id))
            self.conn.commit()
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów: {e}")

    def sort_zawodnicy(self):
        self.load_data()

    def losuj_kolejnosc(self):
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT id FROM zawodnicy")
            zawodnicy_id = [row[0] for row in cursor.fetchall()]

            random.shuffle(zawodnicy_id)

            for i, zawodnik_id in enumerate(zawodnicy_id):
                cursor.execute("UPDATE zawodnicy SET kolejnosc = ? WHERE id = ?", (i + 1, zawodnik_id))

            self.conn.commit()
            self.load_data()

            QMessageBox.information(self, "Sukces", "Kolejność zawodników została wylosowana.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wylosować kolejności: {e}")

    def ustaw_kolejnosc_wg_punktow(self):
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT id, points FROM zawodnicy ORDER BY points DESC")
            zawodnicy = cursor.fetchall()

            for i, (zawodnik_id, _) in enumerate(zawodnicy):
                cursor.execute("UPDATE zawodnicy SET kolejnosc = ? WHERE id = ?", (i + 1, zawodnik_id))

            self.conn.commit()
            self.load_data()

            QMessageBox.information(self, "Sukces", "Kolejność zawodników została ustawiona wg punktów.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się ustawić kolejności: {e}")

    def oblicz_punkty_wszystkich(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM zawodnicy")
            zawodnicy_id = [row[0] for row in cursor.fetchall()]

            for zawodnik_id in zawodnicy_id:
                self.oblicz_punkty(zawodnik_id, self.turniej_id)
            QMessageBox.information(self, "Sukces", "Punkty dla wszystkich zawodników zostały przeliczone.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów: {e}")

    def usun_zawodnika(self, zawodnik_id):
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
                self.load_data()
                QMessageBox.information(self, "Sukces", "Zawodnik został usunięty.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć zawodnika: {e}")

    def edytuj_zawodnika(self, zawodnik_id):
        """Otwiera formularz edycji zawodnika."""
        # You need to pass bundle_dir to FormularzEdycjiZawodnika if it loads any resources
        self.formularz_edycji = FormularzEdycjiZawodnika(self.conn, zawodnik_id, self)
        self.stacked_widget.addWidget(self.formularz_edycji)
        self.stacked_widget.setCurrentWidget(self.formularz_edycji)


    def pokaz_szczegoly_zawodnika(self, zawodnik_id):
        """Otwiera widok wszystkich gier, w których uczestniczył zawodnik."""
        # You need to pass bundle_dir to TabelaGierZawodnika if it loads any resources
        self.szczegoly_zawodnika_window = TabelaGierZawodnika(self.conn, zawodnik_id)
        self.stacked_widget.addWidget(self.szczegoly_zawodnika_window)
        self.stacked_widget.setCurrentWidget(self.szczegoly_zawodnika_window)