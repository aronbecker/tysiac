from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFormLayout, QLineEdit, QMessageBox, QHeaderView)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from formularz_aktualizacji_gry import FormularzAktualizacjiGry

class TabelaGierZawodnika(QWidget):
    """Widok wszystkich gier, w których uczestniczył zawodnik."""
    def __init__(self, conn, zawodnik_id):
        super().__init__()
        self.conn = conn
        self.zawodnik_id = zawodnik_id

        self.player_info_label = QLabel("")
        self.total_points_label = QLabel("")
        self.table = QTableWidget()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.player_info_label)
        self.layout.addWidget(self.total_points_label)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.setWindowTitle("Gry zawodnika")

        self.load_player_data()
        self.load_data()

        # --- Zmiany w ustawieniu trybów resize dla kolumn ---
        # Domyślnie wszystkie kolumny mają elastyczną szerokość
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Ustaw kolumny zawodników na ResizeToContents
        # Indeksy kolumn dla zawodników: 2, 3, 4, 5
        for col_idx in range(2, 6): # Od "Zawodnik 1" (indeks 2) do "Zawodnik 4" (indeks 5)
            self.table.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeToContents)
            
        # Opcjonalnie: Ustaw kolumny Stół i Runda ID na Interactive, aby użytkownik mógł je zmieniać,
        # a jednocześnie miały auto-dopasowanie (ale tylko raz, przy pierwszym wyświetleniu)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive) # Stół
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive) # Runda ID

        # Ustawienie czcionki dla tabeli
        font = QFont()
        font.setPointSize(12)
        self.table.setFont(font)

        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)


    def load_player_data(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT firstname, lastname FROM zawodnicy WHERE id = ?", (self.zawodnik_id,))
        player_data = cursor.fetchone()

        if player_data:
            self.player_firstname = player_data[0]
            self.player_lastname = player_data[1]
            full_name = f"{self.player_lastname} {self.player_firstname}"
            self.setWindowTitle(f"Gry zawodnika: {full_name}")

            self.player_info_label.setText(f" Zawodnik:  {full_name}")
            self.player_info_label.setAlignment(Qt.AlignCenter)

            font = self.player_info_label.font()
            font.setPointSize(font.pointSize() + 2)
            self.player_info_label.setFont(font)

            cursor.execute("""
                SELECT
                    SUM(CASE WHEN g.zawodnik_1 = ? THEN g.wynik_1 ELSE 0 END) +
                    SUM(CASE WHEN g.zawodnik_2 = ? THEN g.wynik_2 ELSE 0 END) +
                    SUM(CASE WHEN g.zawodnik_3 = ? THEN g.wynik_3 ELSE 0 END) +
                    SUM(CASE WHEN g.zawodnik_4 = ? THEN g.wynik_4 ELSE 0 END)
                FROM gra AS g
                WHERE g.zawodnik_1 = ? OR g.zawodnik_2 = ? OR g.zawodnik_3 = ? OR g.zawodnik_4 = ?
            """, (self.zawodnik_id, self.zawodnik_id, self.zawodnik_id, self.zawodnik_id,
                  self.zawodnik_id, self.zawodnik_id, self.zawodnik_id, self.zawodnik_id))

            total_points = cursor.fetchone()[0] or 0
            self.total_points_label.setText(f"Suma punktów:  {total_points}")
            self.total_points_label.setAlignment(Qt.AlignCenter)

        else:
            self.player_info_label.setText("Błąd: Nie znaleziono zawodnika.")
            self.total_points_label.setText("Błąd: Nie można obliczyć punktów.")

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                g.id, -- Nadal pobieramy ID gry (index 0)
                g.stol, -- index 1
                g.runda_id, -- index 2
                z1.lastname || ' ' || z1.firstname AS zawodnik_1, -- index 3
                z2.lastname || ' ' || z2.firstname AS zawodnik_2, -- index 4
                z3.lastname || ' ' || z3.firstname AS zawodnik_3, -- index 5
                z4.lastname || ' ' || z4.firstname AS zawodnik_4, -- index 6
                g.wynik_1, -- index 7
                g.wynik_2, -- index 8
                g.wynik_3, -- index 9
                g.wynik_4 -- index 10
            FROM gra AS g
            LEFT JOIN zawodnicy AS z1 ON g.zawodnik_1 = z1.id
            LEFT JOIN zawodnicy AS z2 ON g.zawodnik_2 = z2.id
            LEFT JOIN zawodnicy AS z3 ON g.zawodnik_3 = z3.id
            LEFT JOIN zawodnicy AS z4 ON g.zawodnik_4 = z4.id
            WHERE zawodnik_1 = ? OR zawodnik_2 = ? OR zawodnik_3 = ? OR zawodnik_4 = ?
        """, (self.zawodnik_id, self.zawodnik_id, self.zawodnik_id, self.zawodnik_id))
        gry = cursor.fetchall()

        column_headers = [
            "Stół", "Runda ID",
            "Zawodnik 1", "Zawodnik 2", "Zawodnik 3", "Zawodnik 4",
            "Wynik 1", "Wynik 2", "Wynik 3", "Wynik 4", "Akcje"
        ]
        
        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.setRowCount(len(gry))

        if gry:
            for i, gra in enumerate(gry):
                game_id = gra[0] # ID gry jest zawsze pierwszym elementem z fetchall()
                
                # Wstawianie danych do tabeli, zaczynając od indeksu 1 z 'gra',
                # ponieważ 'gra[0]' (ID gry) nie jest wyświetlane
                # Data pobrana z SQL: [g.id, g.stol, g.runda_id, z1.name, ..., g.wynik_4]
                # Indexy w QTableWidget: [0,    1,       2,        3,        4,        5,       6,        7,        8,        9,        10]
                # Nagłówki w QTableWidget: ["Stół", "Runda ID", "Zawodnik 1", "Zawodnik 2", "Zawodnik 3", "Zawodnik 4", "Wynik 1", "Wynik 2", "Wynik 3", "Wynik 4", "Akcje"]

                # Kolumna "Stół" w QTableWidget (idx 0) <- gra[1] z SQL
                self.table.setItem(i, 0, QTableWidgetItem(str(gra[1])))
                # Kolumna "Runda ID" w QTableWidget (idx 1) <- gra[2] z SQL
                self.table.setItem(i, 1, QTableWidgetItem(str(gra[2])))
                
                # Kolumny Zawodnik 1 do Zawodnik 4 w QTableWidget (idx 2 do 5) <- gra[3] do gra[6] z SQL
                for j in range(3, 7): # Od indexu 3 (Zawodnik 1) do 6 (Zawodnik 4) z wyników SQL
                    item = QTableWidgetItem(str(gra[j]))
                    self.table.setItem(i, j - 1, item) # j-1, bo przesunięcie o 1 kolumnę (usunięte ID Gry)
                
                # Kolumny Wynik 1 do Wynik 4 w QTableWidget (idx 6 do 9) <- gra[7] do gra[10] z SQL
                for j in range(7, 11): # Od indexu 7 (Wynik 1) do 10 (Wynik 4) z wyników SQL
                    item = QTableWidgetItem(str(gra[j]))
                    self.table.setItem(i, j - 1, item) # j-1, bo przesunięcie o 1 kolumnę


                # Dodawanie przycisku "Aktualizuj" do ostatniej kolumny (indeks 10)
                button = QPushButton()
                button.setIcon(QIcon("icons/calculator.png")) # Upewnij się, że ikona jest dostępna
                button.setToolTip("Aktualizuj")
                button.clicked.connect(lambda _, current_game_id=game_id, current_game_data=gra: self.aktualizuj_gre(current_game_id, current_game_data))
                self.table.setCellWidget(i, len(column_headers) - 1, button)


        # self.table.resizeColumnsToContents() # Ta linia może nadpisywać ResizeToContents, usunięta lub przesunięta
                                            # Indywidualne ustawienia setSectionResizeMode są bardziej precyzyjne
                                            # Jeśli chcesz, aby wszystkie kolumny, które mają ResizeToContents, 
                                            # były dopasowywane po załadowaniu danych, to ta linia może zostać.
                                            # W przeciwnym razie usuń ją, jeśli stretch ma być od razu dominujący.
                                            # W przypadku ResizeToContents, to jest często potrzebne, aby faktycznie zmierzyło zawartość.
        # Sprawdzamy, czy tabela ma dane przed próbą resizeColumnsToContents
        if gry: # Tylko jeśli są jakieś wiersze
            self.table.resizeColumnsToContents()

    def aktualizuj_gre(self, gra_id, data_gry):
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry, self)
        self.formularz_aktualizacji.show()