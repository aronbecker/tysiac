import os
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QComboBox, QHBoxLayout,
                             QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt

from formularz_aktualizacji_gry import FormularzAktualizacjiGry

class TabelaGier2(QWidget):
    def __init__(self, conn, runda_id, bundle_dir, stacked_widget=None, parent_manager=None):
        super().__init__()
        self.setWindowTitle(f"Lista Gier (Widok 2) dla Rundy {runda_id}")
        self.conn = conn
        self.runda_id = runda_id
        self.bundle_dir = bundle_dir
        self.stacked_widget = stacked_widget
        self.parent_manager = parent_manager

        # Główny layout pionowy
        self.layout = QVBoxLayout(self)

        # <-- ZMIANA: Układ poziomy na dwie tabele
        self.content_layout = QHBoxLayout()

        # <-- ZMIANA: Stworzenie dwóch obiektów tabel
        self.table_left = QTableWidget()
        self.table_right = QTableWidget()

        # <-- ZMIANA: Konfiguracja obu tabel za pomocą funkcji pomocniczej
        self.setup_table(self.table_left)
        self.setup_table(self.table_right)

        # <-- ZMIANA: Dodanie obu tabel do układu poziomego
        self.content_layout.addWidget(self.table_left)
        self.content_layout.addWidget(self.table_right)

        # <-- ZMIANA: Dodanie układu poziomego do głównego layoutu
        self.layout.addLayout(self.content_layout)

        self.load_data()

    def setup_table(self, table_widget):
        """Funkcja pomocnicza do konfiguracji obu tabel."""
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        font = QFont()
        font.setPointSize(12) 
        table_widget.setFont(font)
        
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        table_widget.horizontalHeader().setFont(header_font)

        table_widget.verticalHeader().setVisible(False)

        # Ustaw nagłówki i liczbę kolumn
        column_headers = ["Stół", "Zawodnik", "Wynik", "Akcje"]
        table_widget.setColumnCount(len(column_headers)) 
        table_widget.setHorizontalHeaderLabels(column_headers)

        # Ustaw tryb 'Interactive' i domyślne szerokości
        table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive) # Stół
        table_widget.setColumnWidth(0, 80)
        
        table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive) # Zawodnik
        table_widget.setColumnWidth(1, 250)
        
        table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive) # Wynik
        table_widget.setColumnWidth(2, 100)
        
        table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive) # Akcje
        table_widget.setColumnWidth(3, 120)

    def load_data(self):
        """Pobiera dane i dzieli je na dwie tabele."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                g.id, g.data, g.stol, g.runda_id,
                z1.lastname || ' ' || z1.firstname AS zawodnik_1,
                z2.lastname || ' ' || z2.firstname AS zawodnik_2,
                z3.lastname || ' ' || z3.firstname AS zawodnik_3,
                z4.lastname || ' ' || z4.firstname AS zawodnik_4,
                g.wynik_1, g.wynik_2, g.wynik_3, g.wynik_4
            FROM gra AS g
            LEFT JOIN zawodnicy AS z1 ON g.zawodnik_1 = z1.id
            LEFT JOIN zawodnicy AS z2 ON g.zawodnik_2 = z2.id
            LEFT JOIN zawodnicy AS z3 ON g.zawodnik_3 = z3.id
            LEFT JOIN zawodnicy AS z4 ON g.zawodnik_4 = z4.id
            WHERE g.runda_id = ?
            ORDER BY g.stol ASC
        ''', (self.runda_id,))
        gry = cursor.fetchall()

        # Wyczyść obie tabele
        self.table_left.setRowCount(0)
        self.table_right.setRowCount(0)

        # <-- ZMIANA: Podział danych na dwie listy
        total_games = len(gry)
        midpoint = (total_games + 1) // 2  # Zaokrągla w górę dla lewej tabeli
        
        gry_left = gry[:midpoint]
        gry_right = gry[midpoint:]

        # <-- ZMIANA: Wypełnienie obu tabel osobno
        self.populate_table(self.table_left, gry_left)
        self.populate_table(self.table_right, gry_right)

    def populate_table(self, table_widget, gry_data):
        """Wypełnia podaną tabelę podanymi danymi, stosując przeplatanie kolorów tła dla poszczególnych stołów."""
        current_row_index = 0

        # Definicja kolorów (możesz je przenieść do __init__ lub stałych klasy)
        ROW_COLOR_LIGHT = "white"
        ROW_COLOR_DARK = "#F0F0F0" # Lekka szarość
        
        for gra_record in gry_data:
            game_id = gra_record[0]
            stol_number = gra_record[2]
            
            # --- ZMIANA: Wybór koloru tła na podstawie numeru stołu ---
            # Użycie modulo 2 do przeplatania kolorów dla kolejnych stołów
            background_color = ROW_COLOR_DARK if stol_number % 2 == 0 else ROW_COLOR_LIGHT
            color_style = f"background-color: {background_color};" 
            
            # ... (pobieranie zawodników i wyników) ...
            players_scores = []
            player_indices = [4, 5, 6, 7] 
            score_indices = [8, 9, 10, 11]

            for p_idx, s_idx in zip(player_indices, score_indices):
                player_name = gra_record[p_idx]
                if player_name is not None:
                    players_scores.append((player_name, gra_record[s_idx]))

            num_players = len(players_scores)
            if num_players == 0:
                continue

            table_widget.setRowCount(current_row_index + num_players)
            
            # --- 1. Komórki scalone (Stół, Akcje) ---
            
            # Stół (Indeks 0)
            stol_item = QTableWidgetItem(str(stol_number))
            stol_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) 
            # ... (ustawienie czcionki, która została już zdefiniowana) ...
            
            # Ustaw tło dla scalonej komórki STÓŁ
            stol_item.setData(Qt.BackgroundRole, QColor(background_color))
            
            table_widget.setItem(current_row_index, 0, stol_item)
            table_widget.setSpan(current_row_index, 0, num_players, 1)

            # Akcje (Indeks 3)
            # ... (kod przycisku Akcje - bez zmian, używamy button_widget, który nie dziedziczy QTableWidgetItem) ...
            # Musimy zmienić kolor tła QWidget zawierającego przycisk:
            button_widget = QWidget()
            # Ustawienie stylu dla button_widget (nie samego przycisku)
            # button_widget.setStyleSheet(f"QWidget {{ {color_style} }}") 
            button_widget.setStyleSheet(f"QWidget {{ background-color: {background_color}; }}")
            
            # ... (reszta kodu button_widget i button_layout) ...
            
            button = QPushButton()
            button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "pencil.png")))
            button.setToolTip("Aktualizuj grę")
            
            parent_do_odswiezenia = self.parent_manager if self.parent_manager else self
            button.clicked.connect(lambda _, current_gid=game_id, current_data=gra_record, pdp=parent_do_odswiezenia: self.aktualizuj_gre(current_gid, current_data, pdp))

            button_layout = QVBoxLayout(button_widget)
            button_layout.addStretch()
            button_layout.addWidget(button)
            button_layout.addStretch()
            button_layout.setContentsMargins(0, 0, 0, 0)
            
            table_widget.setCellWidget(current_row_index, 3, button_widget)
            table_widget.setSpan(current_row_index, 3, num_players, 1)

            # --- 2. Wypełnianie danych (Zawodnik, Wynik) ---
            
            for i, (player_name, score) in enumerate(players_scores):
                row_to_insert = current_row_index + i
                
                # Ustaw tło dla całego wiersza
                
                # Zawodnik (Indeks 1)
                player_item = QTableWidgetItem(str(player_name))
                player_item.setData(Qt.BackgroundRole, QColor(background_color))
                table_widget.setItem(row_to_insert, 1, player_item)
                
                # Wynik (Indeks 2)
                score_item = QTableWidgetItem(str(score if score is not None else ''))
                score_item.setTextAlignment(Qt.AlignCenter) 
                score_item.setData(Qt.BackgroundRole, QColor(background_color))
                table_widget.setItem(row_to_insert, 2, score_item)

            current_row_index += num_players

        # Ustaw wysokość wierszy dla całej tabeli
        for i in range(table_widget.rowCount()):
            table_widget.setRowHeight(i, 35)

    def aktualizuj_gre(self, gra_id, data_gry, parent_do_odswiezenia=None):
        """Ta funkcja pozostaje bez zmian."""
        if parent_do_odswiezenia is None:
            parent_do_odswiezenia = self.parent_manager if self.parent_manager else self
        
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry,
                                                             parent_table_widget=parent_do_odswiezenia,
                                                             bundle_dir=self.bundle_dir)

        if self.stacked_widget:
            if self.stacked_widget.indexOf(self.formularz_aktualizacji) == -1:
                self.stacked_widget.addWidget(self.formularz_aktualizacji)
            self.stacked_widget.setCurrentWidget(self.formularz_aktualizacji)
        else:
            self.formularz_aktualizacji.show()