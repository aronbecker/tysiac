import os
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QComboBox, QHBoxLayout,
                             QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QIcon, QFont # Import QFont
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
        
        # --- Ustawienie czcionki dla tabeli (podobnie jak w innych widokach) ---
        font = QFont()
        font.setPointSize(12) 
        self.table.setFont(font)
        
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)

        # Ustawiamy domyślne zachowanie na elastyczne, a potem nadpiszemy dla konkretnych kolumn
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                g.id,         -- [0] ID gry (do użytku wewnętrznego)
                g.data,       -- [1] Data gry (do użytku wewnętrznego, np. aktualizacji)
                g.stol,       -- [2] Stół (wyświetlana)
                g.runda_id,   -- [3] Runda ID (do użytku wewnętrznego, nie wyświetlana)
                z1.lastname || ' ' || z1.firstname AS zawodnik_1, -- [4]
                z2.lastname || ' ' || z2.firstname AS zawodnik_2, -- [5]
                z3.lastname || ' ' || z3.firstname AS zawodnik_3, -- [6]
                z4.lastname || ' ' || z4.firstname AS zawodnik_4, -- [7]
                g.wynik_1,    -- [8]
                g.wynik_2,    -- [9]
                g.wynik_3,    -- [10]
                g.wynik_4     -- [11]
            FROM gra AS g
            LEFT JOIN zawodnicy AS z1 ON g.zawodnik_1 = z1.id
            LEFT JOIN zawodnicy AS z2 ON g.zawodnik_2 = z2.id
            LEFT JOIN zawodnicy AS z3 ON g.zawodnik_3 = z3.id
            LEFT JOIN zawodnicy AS z4 ON g.zawodnik_4 = z4.id
            WHERE g.runda_id = ?
            ORDER BY g.stol ASC
        ''', (self.runda_id,))
        gry = cursor.fetchall()

        # Definiujemy kolumny, które chcemy WYŚWIETLAĆ (nazwy nagłówków)
        column_headers_to_display = [
            "Stół",
            "Zawodnik 1", "Zawodnik 2", "Zawodnik 3", "Zawodnik 4",
            "Wynik 1", "Wynik 2", "Wynik 3", "Wynik 4",
            "Akcje" # Kolumna na przycisk
        ]
        
        # Ustawienie liczby kolumn i nagłówków w QTableWidget
        self.table.setColumnCount(len(column_headers_to_display))
        self.table.setHorizontalHeaderLabels(column_headers_to_display)
        self.table.setRowCount(len(gry))

        # Indeksy kolumn z wyniku SQL, które odpowiadają DANYM do wyświetlenia (bez ID, daty, runda_id)
        # Zaczynamy od 'g.stol' (indeks 2 w oryginalnym SQL SELECT)
        # Indeksy w tupli 'gra_record' po SELECT to:
        # [0]=g.id, [1]=g.data, [2]=g.stol, [3]=g.runda_id, [4]=zawodnik_1, ..., [11]=wynik_4
        
        # Kolumny, które będą wyświetlane w tabeli i ich odpowiadające indeksy w krotce 'gra_record'
        #   Wyświetlany indeks -> Indeks w gra_record -> Nazwa kolumny w SQL
        #   0 (Stół)           -> 2                   -> g.stol
        #   1 (Zawodnik 1)     -> 4                   -> zawodnik_1
        #   2 (Zawodnik 2)     -> 5                   -> zawodnik_2
        #   3 (Zawodnik 3)     -> 6                   -> zawodnik_3
        #   4 (Zawodnik 4)     -> 7                   -> zawodnik_4
        #   5 (Wynik 1)        -> 8                   -> g.wynik_1
        #   6 (Wynik 2)        -> 9                   -> g.wynik_2
        #   7 (Wynik 3)        -> 10                  -> g.wynik_3
        #   8 (Wynik 4)        -> 11                  -> g.wynik_4
        
        data_col_indices_in_record = [2, 4, 5, 6, 7, 8, 9, 10, 11] 


        for i, gra_record in enumerate(gry):
            # gra_record to cały rekord z bazy danych (tuple)
            game_id = gra_record[0] # ID gry
            game_data_full_record = gra_record # Cały rekord przekazywany do aktualizacji

            # Wstawiamy dane do tabeli, używając przygotowanych indeksów
            for j_display, original_record_idx in enumerate(data_col_indices_in_record):
                value = gra_record[original_record_idx]
                item = QTableWidgetItem(str(value if value is not None else ''))
                self.table.setItem(i, j_display, item)

            # Dodawanie przycisku "Aktualizuj" w ostatniej kolumnie
            button = QPushButton()
            button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "edit_score.png"))) # Upewnij się, że ikona jest dostępna
            button.setToolTip("Aktualizuj grę")
            button.clicked.connect(lambda _, current_gra_id=game_id, current_data_gry=game_data_full_record: self.aktualizuj_gre(current_gra_id, current_data_gry))
            self.table.setCellWidget(i, len(column_headers_to_display) - 1, button)


        # --- Zastosuj tryby zmiany rozmiaru kolumn ---
        # "Stół" (index 0) - Interactive
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        
        # Kolumny zawodników (indexy 1, 2, 3, 4 w wyświetlanej tabeli) - ResizeToContents
        for col_idx in range(1, 5): # Od "Zawodnik 1" (indeks 1) do "Zawodnik 4" (indeks 4)
            self.table.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeToContents)
        
        # Pozostałe kolumny (Wyniki 1-4, Akcje) - Stretch
        # Indeksy: 5, 6, 7, 8, 9
        for col_idx in range(5, len(column_headers_to_display)):
             self.table.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.Stretch)


        # To jest potrzebne, aby QHeaderView.ResizeToContents zadziałało prawidłowo po załadowaniu danych.
        self.table.resizeColumnsToContents()


    def aktualizuj_gre(self, gra_id, data_gry):
        # Tutaj data_gry to cały rekord z bazy danych, w tym ID gry, data, runda_id itp.
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry,
                                                               parent_table_widget=self,
                                                               bundle_dir=self.bundle_dir)

        # Pokaż formularz w stacked_widget, jeśli jest dostępny, w przeciwnym razie jako oddzielne okno
        if self.stacked_widget:
            # Aby uniknąć dodawania tego samego widżetu wiele razy, sprawdź, czy już go nie ma
            if self.stacked_widget.indexOf(self.formularz_aktualizacji) == -1:
                self.stacked_widget.addWidget(self.formularz_aktualizacji)
            self.stacked_widget.setCurrentWidget(self.formularz_aktualizacji)
        else:
            self.formularz_aktualizacji.show()