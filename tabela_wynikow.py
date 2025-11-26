import os
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QHeaderView, QAbstractItemView,
                             QLabel, QComboBox, QPushButton)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

class TabelaWynikow(QWidget):
    open_calculate_form = pyqtSignal()

    def __init__(self, conn, stacked_widget, bundle_dir):
        super().__init__()
        self.setWindowTitle("Historia Wyników Turniejowych")
        self.conn = conn
        self.stacked_widget = stacked_widget
        self.bundle_dir = bundle_dir
        
        self.main_layout = QVBoxLayout(self)

        # Mapowanie kolumn z DB na nagłówki tabeli (i ewentualne sortowanie)
        self.column_map = {
            "Imię": "firstname",
            "Nazwisko": "lastname",
            "Punkty": "punkty",
            "Turniej ID": "turnament",
            "Data": "tdate"
        }
        
        # Słownik do mapowania nazwy turnieju na ID (Turniej_name -> Turniej_ID)
        self.turniej_map = {}
        # Zmienna do przechowywania aktualnie wybranego ID turnieju (0 oznacza wszystkie)
        self.current_turniej_id = 0 

        # --- Tabela Wyników (Tworzenie i konfiguracja) ---
        self.table = QTableWidget()
        self.setup_table()
        
        # --- Filtering/Sorting/Action Controls (Górny rząd) ---
        self.filter_sort_layout = QHBoxLayout()
        
        # NOWA KONTROLKA: Wybór Turnieju
        self.filter_sort_layout.addWidget(QLabel("Wybierz Turniej:"))
        self.turniej_filter_combo = QComboBox()
        self.load_turnaments_for_filter() # Ładowanie danych do QComboBox
        # Po zmianie wyboru, natychmiast odśwież dane
        self.turniej_filter_combo.currentIndexChanged.connect(self.handle_turniej_selection)

        # Opcje sortowania
        self.filter_sort_layout.addWidget(QLabel("Sortuj po:"))
        self.sort_column_combo = QComboBox()
        self.sort_column_combo.addItems(self.column_map.keys())
        self.sort_column_combo.setCurrentText("Data") # Domyślnie sortuj po dacie
        self.sort_column_combo.currentIndexChanged.connect(self.load_data)

        self.sort_direction_combo = QComboBox()
        self.sort_direction_combo.addItems(["DESC", "ASC"])
        self.sort_direction_combo.currentIndexChanged.connect(self.load_data)
        
        self.filter_sort_layout.addWidget(self.sort_column_combo)
        self.filter_sort_layout.addWidget(self.sort_direction_combo)
        
        self.filter_sort_layout.addStretch(1) # Wyrównuje kontrolki do lewej
        
        self.calculate_button = QPushButton("Oblicz Wyniki Turnieju")
        self.calculate_button.clicked.connect(self.open_calculate_form.emit)
        self.calculate_button.setStyleSheet("font-weight: bold; padding: 5px;")

        self.filter_sort_layout.addWidget(self.calculate_button)
        # ------------------------------------------------------------------

        # Dodanie układów do głównego layoutu
        self.main_layout.insertLayout(0, self.filter_sort_layout) # Kontrolki na górze
        self.main_layout.addWidget(self.table) # Tabela poniżej kontrolek

        self.load_data()

    def load_turnaments_for_filter(self):
        """Pobiera listę turniejów i wypełnia QComboBox."""
        cursor = self.conn.cursor()
        
        # 1. Sprawdź, czy to zapytanie działa i zwraca dane w Twojej bazie
        cursor.execute("SELECT id, name, begin_date FROM turniej ORDER BY begin_date DESC")
        turnieje = cursor.fetchall()

        self.turniej_map = {}
        self.turniej_filter_combo.clear()
        
        # Opcja 1: Wszystkie turnieje (ID 0)
        self.turniej_filter_combo.addItem("Wszystkie Turnieje", 0)
        self.turniej_map["Wszystkie Turnieje"] = 0
        
        if turnieje:
            # 2. Sprawdź, czy ten blok się wykonuje
            for id, name, tdate in turnieje:
                # Tworzymy czytelną nazwę, np. "Turniej Główny (2025-11-20)"
                display_name = f"{name} ({tdate})"
                self.turniej_map[display_name] = id
                # Dodajemy element do QComboBox, przypisując ID jako dane użytkownika
                self.turniej_filter_combo.addItem(display_name, id)

    def handle_turniej_selection(self, index):
        """Aktualizuje ID wybranego turnieju i odświeża dane."""
        # Pobierz ID z danych przypisanych do elementu QComboBox
        self.current_turniej_id = self.turniej_filter_combo.itemData(index)
        self.load_data()

    def setup_table(self):
        """Konfiguracja wizualna tabeli."""
        column_headers = list(self.column_map.keys())
        self.table.setColumnCount(len(column_headers)) 
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Ustawienie czcionki
        font = QFont()
        font.setPointSize(12) 
        self.table.setFont(font)
        
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)
        
        # Rozciąganie kolumn
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_data(self):
        """Pobiera dane z tabeli 'wyniki', stosując filtr turnieju."""
        cursor = self.conn.cursor()

        selected_polish_name = self.sort_column_combo.currentText()
        sort_column = self.column_map.get(selected_polish_name, "tdate") 
        sort_direction = self.sort_direction_combo.currentText()
        
        # Budowanie zapytania SQL z filtrowaniem
        query = "SELECT firstname, lastname, punkty, turnament, tdate FROM wyniki"
        params = []
        
        # Dodanie klauzuli WHERE, jeśli nie wybrano "Wszystkich Turniejów" (ID != 0)
        if self.current_turniej_id != 0:
            query += " WHERE turnament = ?"
            params.append(self.current_turniej_id)
        
        query += f" ORDER BY {sort_column} {sort_direction}"

        cursor.execute(query, tuple(params))
        data = cursor.fetchall()

        self.table.setRowCount(len(data))
        
        # Wypełnianie tabeli
        for row_index, row_data in enumerate(data):
            # row_data: (firstname, lastname, punkty, turnament, tdate)
            for col_index, item_data in enumerate(row_data):
                item = QTableWidgetItem(str(item_data))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, col_index, item)