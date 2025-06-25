import os
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QComboBox, QHBoxLayout,
                             QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt

from formularz_aktualizacji_gry import FormularzAktualizacjiGry

class TabelaGier(QWidget):
    def __init__(self, conn, runda_id, bundle_dir, stacked_widget=None):
        super().__init__()
        self.setWindowTitle(f"Lista Gier dla Rundy {runda_id}")
        self.conn = conn
        self.runda_id = runda_id
        self.bundle_dir = bundle_dir
        self.stacked_widget = stacked_widget

        self.table = QTableWidget()
        self.layout = QVBoxLayout(self)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        font = QFont()
        font.setPointSize(12) 
        self.table.setFont(font)
        
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)

        # Ustawiamy domyślne zachowanie na elastyczne, a potem nadpiszemy dla konkretnych kolumn
        # To jest teraz mniej krytyczne, bo będziemy ręcznie sterować rozmiarem po wstawieniu danych.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 

        self.layout.addWidget(self.table)
        self.load_data()

        self.setLayout(self.layout)


    def load_data(self):
        cursor = self.conn.cursor()
        # SQL zapytanie jest OK, pobiera wszystkie potrzebne dane w jednym wierszu na grę.
        # Będziemy grupować te dane w Pythonie.
        cursor.execute('''
            SELECT
                g.id,           -- [0] ID gry (do użytku wewnętrznego)
                g.data,         -- [1] Data gry (do użytku wewnętrznego, np. aktualizacji)
                g.stol,         -- [2] Stół (wyświetlana)
                g.runda_id,     -- [3] Runda ID (do użytku wewnętrznego, nie wyświetlana)
                z1.lastname || ' ' || z1.firstname AS zawodnik_1, -- [4]
                z2.lastname || ' ' || z2.firstname AS zawodnik_2, -- [5]
                z3.lastname || ' ' || z3.firstname AS zawodnik_3, -- [6]
                z4.lastname || ' ' || z4.firstname AS zawodnik_4, -- [7]
                g.wynik_1,      -- [8]
                g.wynik_2,      -- [9]
                g.wynik_3,      -- [10]
                g.wynik_4       -- [11]
            FROM gra AS g
            LEFT JOIN zawodnicy AS z1 ON g.zawodnik_1 = z1.id
            LEFT JOIN zawodnicy AS z2 ON g.zawodnik_2 = z2.id
            LEFT JOIN zawodnicy AS z3 ON g.zawodnik_3 = z3.id
            LEFT JOIN zawodnicy AS z4 ON g.zawodnik_4 = z4.id
            WHERE g.runda_id = ?
            ORDER BY g.stol ASC
        ''', (self.runda_id,))
        gry_raw_data = cursor.fetchall() # Pobierz wszystkie wiersze

        # --- KROK 1: Przetwarzanie danych do pożądanego formatu grupującego po stolikach ---
        # Będziemy budować słownik, gdzie kluczem jest ID stolika,
        # a wartością jest lista słowników, każdy reprezentujący zawodnika i jego wynik.
        # Dodatkowo, zapiszemy game_id dla każdego stolika, aby można było przekazać je do aktualizacji.
        
        # Format danych wyjściowych:
        # {
        #   stol_id: {
        #       'game_id': int,
        #       'full_game_record': tuple, # Cały rekord z bazy danych
        #       'players': [
        #           {'name': 'Zawodnik 1', 'score': 'Wynik 1'},
        #           {'name': 'Zawodnik 2', 'score': 'Wynik 2'},
        #           # ... do 4 zawodników
        #       ]
        #   },
        #   ...
        # }
        
        grouped_games_data = {}
        for record in gry_raw_data:
            game_id = record[0]
            stol_id = record[2]
            
            if stol_id not in grouped_games_data:
                grouped_games_data[stol_id] = {
                    'game_id': game_id,
                    'full_game_record': record, # Zachowaj cały rekord dla aktualizacji
                    'players': []
                }
            
            # Dodaj zawodników i ich wyniki do listy dla danego stolika
            # Iterujemy od zawodnik_1 (indeks 4) do wynik_4 (indeks 11)
            for i in range(4): # 4 zawodników
                player_name = record[4 + i] # Zawodnik 1-4
                player_score = record[8 + i] # Wynik 1-4

                # Dodajemy tylko jeśli zawodnik istnieje (nie jest None)
                if player_name:
                    grouped_games_data[stol_id]['players'].append({
                        'name': player_name,
                        'score': str(player_score if player_score is not None else '')
                    })
        
        # Posortuj stoliki po ich ID, aby zachować porządek
        sorted_stols_data = sorted(grouped_games_data.items(), key=lambda item: item[0])

        # --- KROK 2: Ustawienie struktury QTableWidget ---
        # Definiujemy kolumny, które chcemy WYŚWIETLAĆ (nazwy nagłówków)
        column_headers_to_display = [
            "Stół",
            "Zawodnicy",
            "Wyniki",
            "Akcje"
        ]
        
        self.table.setColumnCount(len(column_headers_to_display))
        self.table.setHorizontalHeaderLabels(column_headers_to_display)
        
        # Oblicz całkowitą liczbę wierszy, uwzględniając wszystkich zawodników dla wszystkich stolików
        total_rows = 0
        for stol_id, stol_info in sorted_stols_data:
            total_rows += len(stol_info['players']) # Liczba wierszy dla zawodników
            # Opcjonalnie: total_rows += 1 # Dodaj 1 wiersz na separator, jeśli chcesz widoczne odstępy

        self.table.setRowCount(total_rows)
        stol_count = 0 

        # --- KROK 3: Wypełnianie tabeli danymi i stosowanie setSpan ---
        current_display_row = 0
        for stol_id, stol_info in sorted_stols_data:
            game_id = stol_info['game_id']
            full_game_record = stol_info['full_game_record']
            players_data = stol_info['players']
            num_players = len(players_data)

            if num_players == 0:
                continue # Pomiń stoliki bez zawodników (chociaż nasza logika powinna zapobiec temu)

            # Ustaw kolor tła dla bieżącego stolika
            # Możesz wybrać kolory, które pasują do Twojej aplikacji
            if stol_count % 2 == 0: # Co drugi stolik (parzysty index)
                # Jasny szary, żeby nie odciągać uwagi od danych
                background_color = QColor(192, 192, 192) 
            else: # Co drugi stolik (nieparzysty index)
                background_color = QColor(255, 255, 255) # Biały

            # --- Kolumna 'Stół' (indeks 0) ---
            self.table.setSpan(current_display_row, 0, num_players, 1) # Scal komórki pionowo
            item_stol = QTableWidgetItem(str(stol_id))
            item_stol.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter) # Wyśrodkuj tekst
            self.table.setItem(current_display_row, 0, item_stol)
            item_stol.setBackground(background_color) # Ustaw tło
            # --- Kolumna 'Akcje' (indeks 3) ---
            self.table.setSpan(current_display_row, 3, num_players, 1) # Scal komórki pionowo
            
            button = QPushButton()
            button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "edit_score.png")))
            button.setToolTip(f"Aktualizuj grę dla stołu {stol_id}")
            # Przekaż game_id i cały rekord gry do funkcji aktualizuj_gre
            button.clicked.connect(lambda _, gid=game_id, data_rec=full_game_record: self.aktualizuj_gre(gid, data_rec))
            
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.addWidget(button)
            button_layout.setAlignment(Qt.AlignCenter)
            button_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(current_display_row, 3, button_widget)

            # --- Kolumny 'Zawodnicy' (indeks 1) i 'Wyniki' (indeks 2) ---
            for i, player in enumerate(players_data):
                row_idx = current_display_row + i
                item_zawodnik = QTableWidgetItem(player['name'])
                item_wynik = QTableWidgetItem(player['score'])
                
                # Ustaw wyrównanie dla nazwisk i wyników (opcjonalnie)
                item_zawodnik.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item_wynik.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item_zawodnik.setBackground(background_color) # Ustaw tło
                item_wynik.setBackground(background_color) # Ustaw tło

                self.table.setItem(row_idx, 1, item_zawodnik)
                self.table.setItem(row_idx, 2, item_wynik)

            current_display_row += num_players
            stol_count += 1 
            

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        # Dostosuj szerokość kolumn do zawartości
        self.table.resizeColumnsToContents()

        self.table.horizontalHeader().setStretchLastSection(False) # Ważne, aby nie rozciągać tylko ostatniej
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Rozciągnij kolumnę Zawodnicy



    def aktualizuj_gre(self, gra_id, data_gry):
        # Tutaj data_gry to cały rekord z bazy danych, w tym ID gry, data, runda_id itp.
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry,
                                                             parent_table_widget=self,
                                                             bundle_dir=self.bundle_dir)

        if self.stacked_widget:
            # Aby uniknąć dodawania tego samego widżetu wiele razy, sprawdź, czy już go nie ma
            if self.stacked_widget.indexOf(self.formularz_aktualizacji) == -1:
                self.stacked_widget.addWidget(self.formularz_aktualizacji)
            self.stacked_widget.setCurrentWidget(self.formularz_aktualizacji)
        else:
            self.formularz_aktualizacji.show()