import os
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QMessageBox, QComboBox,
                             QHBoxLayout, QHeaderView, QAbstractItemView, QLabel, QLineEdit, QFileDialog)
from PyQt5.QtGui import QIcon, QFont # Import QFont for font size
from PyQt5.QtCore import Qt

from formularz_edycji_zawodnika import FormularzEdycjiZawodnika
from tabela_gier_zawodnika import TabelaGierZawodnika

import openpyxl
import random

class TabelaZawodnikow(QWidget):
    def __init__(self, conn, turniej_id, stacked_widget, bundle_dir):
        super().__init__()
        self.setWindowTitle("Lista Zawodników")
        self.stacked_widget = stacked_widget
        self.conn = conn
        self.turniej_id = turniej_id
        self.bundle_dir = bundle_dir

        self.main_layout = QVBoxLayout(self)

        # --- Filtering/Sorting Controls (Top Row) ---
        self.filter_sort_layout = QHBoxLayout()

        # Zmieniono filtr z ID na Imię/Nazwisko, skoro ID nie jest wyświetlane
        self.filter_name_label = QLabel("Filtruj po imieniu/nazwisku:")
        self.filter_name_input = QLineEdit()
        self.filter_name_input.setPlaceholderText("Wpisz imię lub nazwisko")
        self.filter_name_input.textChanged.connect(self.load_data) # Live filter

        self.sort_column_combo = QComboBox()
        # Usunięto 'id' z opcji sortowania, jeśli nie jest wyświetlane
        self.sort_column_combo.addItems(["firstname", "lastname", "points", "kolejnosc"])
        self.sort_column_combo.currentIndexChanged.connect(self.load_data)

        self.sort_direction_combo = QComboBox()
        self.sort_direction_combo.addItems(["ASC", "DESC"])
        self.sort_direction_combo.currentIndexChanged.connect(self.load_data)

        self.filter_sort_layout.addWidget(self.filter_name_label)
        self.filter_sort_layout.addWidget(self.filter_name_input)
        self.filter_sort_layout.addStretch(1)
        self.filter_sort_layout.addWidget(QLabel("Sortuj po:"))
        self.filter_sort_layout.addWidget(self.sort_column_combo)
        self.filter_sort_layout.addWidget(self.sort_direction_combo)

        # --- Przycisk Eksportu ---
        self.export_button = QPushButton("Eksportuj do XLSX")
        self.export_button.clicked.connect(self.export_to_xlsx)
        self.filter_sort_layout.addWidget(self.export_button)
        self.main_layout.addLayout(self.filter_sort_layout)

        # --- Action Buttons (Losuj, Ustaw, Oblicz) ---
        self.action_buttons_layout = QHBoxLayout()

        self.losuj_kolejnosc_button = QPushButton("Losuj kolejność")
        self.losuj_kolejnosc_button.clicked.connect(self.losuj_kolejnosc)
        self.action_buttons_layout.addWidget(self.losuj_kolejnosc_button)

        self.ustaw_kolejnosc_button = QPushButton("Ustaw kolejność wg punktów")
        self.ustaw_kolejnosc_button.clicked.connect(self.ustaw_kolejnosc_wg_punktow)
        self.action_buttons_layout.addWidget(self.ustaw_kolejnosc_button)

        self.oblicz_wszystkich_button = QPushButton("Oblicz punkty dla wszystkich")
        self.oblicz_wszystkich_button.clicked.connect(self.oblicz_punkty_wszystkich)
        self.action_buttons_layout.addWidget(self.oblicz_wszystkich_button)

        self.main_layout.addLayout(self.action_buttons_layout)

        # --- Table Widget ---
        self.table = QTableWidget()
        # Zmieniono liczbę kolumn z 9 na 8 (usunięto kolumnę ID)
        self.table.setColumnCount(8) 
        # Zmieniono nagłówki - usunięto "ID"
        self.table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "Punkty", "Kolejność", "Oblicz", "Szczegóły", "Usuń", "Edytuj"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Zwiększenie czcionki wewnątrz tabeli
        font = QFont()
        font.setPointSize(12) # Ustaw rozmiar czcionki na np. 12 (możesz dostosować)
        self.table.setFont(font)
        
        # Opcjonalnie: Zwiększenie czcionki dla nagłówków kolumn
        header_font = QFont()
        header_font.setPointSize(12) # Rozmiar czcionki nagłówków
        header_font.setBold(True) # Pogrubienie
        self.table.horizontalHeader().setFont(header_font)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

        self.setLayout(self.main_layout)

        self.load_data() # Initial data load

    def load_data(self):
        self.cursor = self.conn.cursor()

        sort_column = self.sort_column_combo.currentText()
        sort_direction = self.sort_direction_combo.currentText()
        filter_text = self.filter_name_input.text().strip() # Tekst do filtrowania po imieniu/nazwisku

        # Zmieniono zapytanie SQL - nie wybieramy ID
        query = "SELECT id, firstname, lastname, points, kolejnosc FROM zawodnicy" # Nadal potrzebujemy ID do operacji (usuń, edytuj, oblicz)
        params = []

        if filter_text:
            query += " WHERE firstname LIKE ? OR lastname LIKE ?"
            params.append(f"%{filter_text}%")
            params.append(f"%{filter_text}%")

        query += f" ORDER BY {sort_column} {sort_direction}"

        self.cursor.execute(query, tuple(params))
        data = self.cursor.fetchall()

        self.table.setRowCount(len(data))
        # self.table.setColumnCount(8) # Usunięto ID, więc 8 kolumn (bez przycisków)

        # Nagłówki kolumn w interfejsie użytkownika
        # self.table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "Punkty", "Kolejność", "Oblicz", "Szczegóły", "Usuń", "Edytuj"])

        # Populate table with data and buttons
        for row_index, row_data in enumerate(data):
            zawodnik_id = row_data[0] # ID zawodnika jest nadal pobierane, ale nie wyświetlane

            # Data columns (pamiętaj, że row_data[0] to ID, więc zaczynamy od row_data[1])
            # Indeksy kolumn w tabeli (Qt) przesuwają się o 1 w lewo
            # row_data: [id, firstname, lastname, points, kolejnosc]
            # Qt Table: [firstname, lastname, points, kolejnosc, Oblicz, Szczegóły, Usuń, Edytuj]
            self.table.setItem(row_index, 0, QTableWidgetItem(str(row_data[1]))) # Imię
            self.table.setItem(row_index, 1, QTableWidgetItem(str(row_data[2]))) # Nazwisko
            self.table.setItem(row_index, 2, QTableWidgetItem(str(row_data[3]))) # Punkty
            self.table.setItem(row_index, 3, QTableWidgetItem(str(row_data[4]))) # Kolejność

            # Button "Oblicz" (kolumna 4 w QTableWidget)
            oblicz_button = QPushButton()
            oblicz_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "calculator.png")))
            oblicz_button.setToolTip("Oblicz punkty")
            oblicz_button.clicked.connect(lambda _, zid=zawodnik_id: self.oblicz_punkty(zid, self.turniej_id))
            self.table.setCellWidget(row_index, 4, oblicz_button)

            # Button "Szczegóły" (kolumna 5 w QTableWidget)
            szczegoly_button = QPushButton()
            szczegoly_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "eye.png")))
            szczegoly_button.setToolTip("Pokaż szczegóły")
            szczegoly_button.clicked.connect(lambda _, zid=zawodnik_id: self.pokaz_szczegoly_zawodnika(zid))
            self.table.setCellWidget(row_index, 5, szczegoly_button)

            # Button "Usuń" (kolumna 6 w QTableWidget)
            usun_button = QPushButton()
            usun_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "trash.png")))
            usun_button.setToolTip("Usuń zawodnika")
            usun_button.clicked.connect(lambda _, zid=zawodnik_id: self.usun_zawodnika(zid))
            self.table.setCellWidget(row_index, 6, usun_button)

            # Button "Edytuj" (kolumna 7 w QTableWidget)
            edytuj_button = QPushButton()
            edytuj_button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "pencil.png")))
            edytuj_button.setToolTip("Edytuj zawodnika")
            edytuj_button.clicked.connect(lambda _, zid=zawodnik_id: self.edytuj_zawodnika(zid))
            self.table.setCellWidget(row_index, 7, edytuj_button)

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
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Eksportuj listę zawodników", "lista_zawodnikow.xlsx",
                                                   "Pliki Excel (*.xlsx);;Wszystkie pliki (*)", options=options)

        if file_name:
            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Lista Zawodników"

                headers = []
                for col in range(self.table.columnCount()):
                    header_item = self.table.horizontalHeaderItem(col)
                    if header_item is not None:
                        headers.append(header_item.text())
                    else:
                        headers.append(f"Kolumna {col+1}")
                sheet.append(headers)

                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        if self.table.cellWidget(row, col) is None:
                            item = self.table.item(row, col)
                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append("")
                        else:
                            row_data.append("")
                    sheet.append(row_data)

                workbook.save(file_name)
                QMessageBox.information(self, "Eksport zakończony", f"Dane zostały pomyślnie wyeksportowane do: {file_name}")

            except Exception as e:
                QMessageBox.critical(self, "Błąd eksportu", f"Wystąpił błąd podczas eksportowania danych: {e}")
        else:
            QMessageBox.information(self, "Eksport anulowany", "Eksport danych został anulowany.")

    def oblicz_punktyOld(self, zawodnik_id, turniej_id):
        try:
            # self.dodaj_indexy()
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

    def oblicz_punkty(self, zawodnik_id, turniej_id):
        try:
            cursor = self.conn.cursor()

            # 1. Pobierz wszystkie gry, w których uczestniczył dany zawodnik w tym turnieju
            # Wybieramy wszystkie kolumny zawodników i wyników
            cursor.execute("""
                SELECT
                    zawodnik_1, wynik_1,
                    zawodnik_2, wynik_2,
                    zawodnik_3, wynik_3,
                    zawodnik_4, wynik_4
                FROM gra
                WHERE
                    turniej_id = ? AND
                    (zawodnik_1 = ? OR zawodnik_2 = ? OR zawodnik_3 = ? OR zawodnik_4 = ?)
            """, (turniej_id, zawodnik_id, zawodnik_id, zawodnik_id, zawodnik_id))
            
            gry_zawodnika = cursor.fetchall()

            punkty = 0
            if gry_zawodnika: # Jeśli zawodnik ma jakieś gry
                # 2. Oblicz punkty w Pythonie
                for gra in gry_zawodnika:
                    # gra to krotka: (zawodnik_1, wynik_1, zawodnik_2, wynik_2, zawodnik_3, wynik_3, zawodnik_4, wynik_4)
                    
                    # Sprawdzamy, na której pozycji zawodnik grał w danej grze i dodajemy odpowiedni wynik
                    if gra[0] == zawodnik_id: # Zawodnik 1
                        punkty += (gra[1] if gra[1] is not None else 0)
                    if gra[2] == zawodnik_id: # Zawodnik 2
                        punkty += (gra[3] if gra[3] is not None else 0)
                    if gra[4] == zawodnik_id: # Zawodnik 3
                        punkty += (gra[5] if gra[5] is not None else 0)
                    if gra[6] == zawodnik_id: # Zawodnik 4
                        punkty += (gra[7] if gra[7] is not None else 0)
            
            # Wartości None są traktowane jako 0 punktów
            punkty = int(punkty) # Upewnij się, że punkty są liczbą całkowitą

            # 3. Zaktualizuj punkty w bazie danych
            cursor.execute("UPDATE zawodnicy SET points = ? WHERE id = ?", (punkty, zawodnik_id))
            self.conn.commit()
            
            # 4. Odśwież widok tabeli
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów: {e}")

# W klasie TabelaZawodnikow

# ... (definicja oblicz_punkty dla pojedynczego zawodnika, jeśli nadal potrzebna, z nową implementacją pythona) ...

    def oblicz_punkty_wszystkich(self):
        try:
            # self.dodaj_indexy() # Możesz wywołać to raz na starcie aplikacji, a nie tutaj w pętli
            cursor = self.conn.cursor()

            # 1. Pobierz ID wszystkich zawodników dla bieżącego turnieju
            # Zakładam, że zawodnicy mają `turniej_id` lub są powiązani przez `turniej_zawodnicy`
            # Jeśli zawodnicy są przypisani do turniejów przez tabelę `turniej_zawodnicy`:
            # cursor.execute("SELECT z.id FROM zawodnicy AS z JOIN turniej_zawodnicy AS tz ON z.id = tz.zawodnik_id WHERE tz.turniej_id = ?", (self.turniej_id,))
            cursor.execute("SELECT id FROM zawodnicy")
            zawodnicy_ids = [row[0] for row in cursor.fetchall()]

            # 2. Pobierz WSZYSTKIE gry dla tego turnieju, w których brał udział którykolwiek z tych zawodników
            # Znacznie mniej zapytań do bazy danych
            cursor.execute("""
                SELECT
                    zawodnik_1, wynik_1,
                    zawodnik_2, wynik_2,
                    zawodnik_3, wynik_3,
                    zawodnik_4, wynik_4
                FROM gra
                WHERE turniej_id = ?
                -- Nie filtrujemy tutaj po konkretnym zawodniku, bo potrzebujemy wszystkich gier turnieju
            """, (self.turniej_id,))
            
            wszystkie_gry_w_turnieju = cursor.fetchall()

            # Słownik do przechowywania obliczonych punktów dla każdego zawodnika
            calculated_points = {zid: 0 for zid in zawodnicy_ids}

            # 3. Oblicz punkty w Pythonie dla wszystkich zawodników jednocześnie
            for gra in wszystkie_gry_w_turnieju:
                players_in_game = {
                    gra[0]: (gra[1] if gra[1] is not None else 0), # zawodnik_1: wynik_1
                    gra[2]: (gra[3] if gra[3] is not None else 0), # zawodnik_2: wynik_2
                    gra[4]: (gra[5] if gra[5] is not None else 0), # zawodnik_3: wynik_3
                    gra[6]: (gra[7] if gra[7] is not None else 0)  # zawodnik_4: wynik_4
                }
                
                for p_id, p_score in players_in_game.items():
                    if p_id in calculated_points: # Upewnij się, że zawodnik jest z tego turnieju
                        calculated_points[p_id] += p_score
            
            # 4. Przygotuj dane do aktualizacji bazy danych w operacji wsadowej
            updates_to_db = []
            for zid, points_sum in calculated_points.items():
                updates_to_db.append((int(points_sum), zid)) # Upewnij się, że punkty są int

            # 5. Wykonaj aktualizację wszystkich punktów w JEDNEJ operacji (executemany)
            cursor.executemany("UPDATE zawodnicy SET points = ? WHERE id = ?", updates_to_db)
            self.conn.commit() # JEDEN COMMIT

            # 6. Odśwież UI TYLKO RAZ
            self.load_data()
            QMessageBox.information(self, "Sukces", "Punkty dla wszystkich zawodników zostały przeliczone.")

        except Exception as e:
            self.conn.rollback() # Wycofaj zmiany, jeśli coś pójdzie nie tak
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów dla wszystkich zawodników: {e}")


    def dodaj_indexy(self):
        """Dodaje indeksy do tabeli zawodników."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gra_turniej_id ON gra (turniej_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gra_zawodnik_1 ON gra (zawodnik_1)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gra_zawodnik_2 ON gra (zawodnik_2)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gra_zawodnik_3 ON gra (zawodnik_3)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gra_zawodnik_4 ON gra (zawodnik_4)")
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się dodać indeksów: {e}")

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

    def oblicz_punkty_wszystkichOld(self):
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
        # Assume FormularzEdycjiZawodnika does not need bundle_dir passed, or handles it internally
        self.formularz_edycji = FormularzEdycjiZawodnika(self.conn, zawodnik_id, self, self.bundle_dir)
        self.stacked_widget.addWidget(self.formularz_edycji)
        self.stacked_widget.setCurrentWidget(self.formularz_edycji)


    def pokaz_szczegoly_zawodnika(self, zawodnik_id):
        """Otwiera widok wszystkich gier, w których uczestniczył zawodnik."""
        # Assume TabelaGierZawodnika does not need bundle_dir passed, or handles it internally
        self.szczegoly_zawodnika_window = TabelaGierZawodnika(self.conn, zawodnik_id)
        self.stacked_widget.addWidget(self.szczegoly_zawodnika_window)
        self.stacked_widget.setCurrentWidget(self.szczegoly_zawodnika_window)