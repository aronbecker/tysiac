import os
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QComboBox, QHBoxLayout,
                             QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QIcon
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                g.id,         -- <--- ZOSTAWIAJEMY G.ID DO WEWNĘTRZNEGO UŻYTKU
                g.data,       -- <--- ZOSTAWIAJEMY G.DATA DO WEWNĘTRZNEGO UŻYTKU (np. dla formularza aktualizacji)
                g.stol,
                g.runda_id,
                z1.lastname || ' ' || z1.firstname AS zawodnik_1,
                z2.lastname || ' ' || z2.firstname AS zawodnik_2,
                z3.lastname || ' ' || z3.firstname AS zawodnik_3,
                z4.lastname || ' ' || z4.firstname AS zawodnik_4,
                g.wynik_1,
                g.wynik_2,
                g.wynik_3,
                g.wynik_4
            FROM gra AS g
            LEFT JOIN zawodnicy AS z1 ON g.zawodnik_1 = z1.id
            LEFT JOIN zawodnicy AS z2 ON g.zawodnik_2 = z2.id
            LEFT JOIN zawodnicy AS z3 ON g.zawodnik_3 = z3.id
            LEFT JOIN zawodnicy AS z4 ON g.zawodnik_4 = z4.id
            WHERE g.runda_id = ?
            ORDER BY g.stol ASC
        ''', (self.runda_id,))
        gry = cursor.fetchall()

        # Pobieramy nagłówki z zapytania SQL
        column_headers_raw = [description[0] for description in cursor.description]

        # Definiujemy kolumny, które chcemy WYŚWIETLAĆ
        # Pamiętaj, że g.id (0) i g.data (1) są w oryginalnym rekordzie, ale nie w wyświetlanych.
        # W widoku będą od 'stol' (czyli oryginalnie index 2)
        columns_to_display_names = [
            'stol', 'runda_id',
            'zawodnik_1', 'zawodnik_2', 'zawodnik_3', 'zawodnik_4',
            'wynik_1', 'wynik_2', 'wynik_3', 'wynik_4'
        ]
        
        # Filtrujemy oryginalne nagłówki, aby uzyskać tylko te, które chcemy wyświetlić,
        # zachowując ich oryginalną kolejność, aby indeksy pasowały
        display_headers = [
            header for header in column_headers_raw if header in columns_to_display_names
        ]


        # Liczba kolumn do wyświetlenia to (liczba wybranych kolumn) + 1 dla przycisku
        num_display_columns = len(display_headers) + 1 # +1 dla przycisku "Aktualizuj"

        self.table.setRowCount(len(gry))
        self.table.setColumnCount(num_display_columns)
        self.table.setHorizontalHeaderLabels(display_headers + ["Aktualizuj"])

        # Indeksy kolumn w oryginalnym zapytaniu SQL, które odpowiadają wyświetlanym danym
        # (czyli te, które nie są g.id ani g.data)
        original_indices_to_display = [
            column_headers_raw.index(name) for name in columns_to_display_names
        ]


        for i, gra_record in enumerate(gry): # Zmieniłem 'gra' na 'gra_record' dla jasności
            # 'gra_record' to cały rekord z bazy danych (ID, data, stol, runda_id, zawodnik_1...wynik_4)
            # Wstawiamy dane do tabeli, używając oryginalnych indeksów, ale pomijając ID i datę
            for j_display, original_idx in enumerate(original_indices_to_display):
                value = gra_record[original_idx] # Pobieramy wartość z oryginalnego rekordu
                item = QTableWidgetItem(str(value if value is not None else ''))
                self.table.setItem(i, j_display, item) # 'j_display' to indeks w widocznej tabeli

            # Dodawanie przycisku "Aktualizuj"
            button = QPushButton()
            button.setIcon(QIcon(os.path.join(self.bundle_dir, "icons", "edit_score.png")))
            button.setToolTip("Aktualizuj")
            # Przekazujemy gra_record[0] (ID gry) i cały rekord gra_record (data_gry)
            button.clicked.connect(lambda _, current_gra_id=gra_record[0], current_data_gry=gra_record: self.aktualizuj_gre(current_gra_id, current_data_gry))
            self.table.setCellWidget(i, num_display_columns - 1, button) # Przycisk w ostatniej kolumnie

        # Zastosuj tryby zmiany rozmiaru kolumn
        zawodnik_display_col_indices = []
        for idx, header_name in enumerate(display_headers):
            if 'zawodnik' in header_name:
                zawodnik_display_col_indices.append(idx)

        for col_idx in zawodnik_display_col_indices:
            self.table.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeToContents)

        self.table.resizeColumnsToContents()


    def aktualizuj_gre(self, gra_id, data_gry):
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry,
                                                               parent_table_widget=self,
                                                               bundle_dir=self.bundle_dir)

        if self.stacked_widget:
            self.stacked_widget.addWidget(self.formularz_aktualizacji)
            self.stacked_widget.setCurrentWidget(self.formularz_aktualizacji)
        else:
            self.formularz_aktualizacji.show()