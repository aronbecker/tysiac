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

        # Utwórz główne elementy UI
        self.player_info_label = QLabel("") # Etykieta na imię i nazwisko zawodnika
        self.total_points_label = QLabel("") # Etykieta na sumę punktów
        self.table = QTableWidget()

        # Ustawienie layoutu
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.player_info_label)  # Dodaj etykietę z imieniem/nazwiskiem
        self.layout.addWidget(self.total_points_label) # Dodaj etykietę z punktami
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        # Ustawienie nagłówka okna
        self.setWindowTitle("Gry zawodnika") # Tytuł będzie ustawiony po pobraniu danych zawodnika

        # Wczytaj dane i zaktualizuj UI
        self.load_player_data() # Nowa funkcja do ładowania danych zawodnika i jego sumy punktów
        self.load_data()  # Zmieniona nazwa, aby była bardziej specyficzna dla gier

        # Opcjonalnie: Ustawienie szerokości kolumn
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)


    def load_player_data(self):
        """Pobiera imię, nazwisko i sumę punktów zawodnika."""
        cursor = self.conn.cursor()

        # Pobranie imienia i nazwiska zawodnika
        cursor.execute("SELECT firstname, lastname FROM zawodnicy WHERE id = ?", (self.zawodnik_id,))
        player_data = cursor.fetchone()

        if player_data:
            self.player_firstname = player_data[0]
            self.player_lastname = player_data[1]
            full_name = f"{self.player_lastname} {self.player_firstname}"
            self.setWindowTitle(f"Gry zawodnika: {full_name}")

            # Ustawienie tekstu etykiety z imieniem i nazwiskiem
            self.player_info_label.setText(f" Zawodnik:  {full_name}")
            self.player_info_label.setAlignment(Qt.AlignCenter) # Wyśrodkuj tekst

            # Pogrub czcionkę etykiety z imieniem i nazwiskiem
            font = self.player_info_label.font()
            font.setPointSize(font.pointSize() + 2) # Zwiększ rozmiar czcionki
            self.player_info_label.setFont(font)

            # Obliczanie sumy punktów dla zawodnika ze wszystkich gier
            # Musimy sumować punkty z odpowiedniej kolumny w zależności od pozycji zawodnika
            # To jest bardziej złożone i wymaga sumowania warunkowego
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

            total_points = cursor.fetchone()[0] or 0 # Użyj 0, jeśli suma jest NULL (brak gier)
            self.total_points_label.setText(f"Suma punktów:  {total_points}")
            self.total_points_label.setAlignment(Qt.AlignCenter) # Wyśrodkuj tekst

        else:
            self.player_info_label.setText("Błąd: Nie znaleziono zawodnika.")
            self.total_points_label.setText("Błąd: Nie można obliczyć punktów.")

    def load_data(self):
        cursor = self.conn.cursor()
        # cursor.execute("DELETE FROM gra WHERE runda_id = ?", (1,))
        # self.conn.commit()
        cursor.execute("""
            SELECT DISTINCT
                g.data, 
                g.stol, 
                g.runda_id, 
                z1.lastname || ' ' || z1.firstname AS zawodnik_1,  -- Złączenie nazwiska i imienia
                z2.lastname || ' ' || z2.firstname AS zawodnik_2,
                z3.lastname || ' ' || z3.firstname AS zawodnik_3,
                z4.lastname || ' ' || z4.firstname AS zawodnik_4,
                g.wynik_1, 
                g.wynik_2, 
                g.wynik_3, 
                g.wynik_4
            FROM gra AS g
            LEFT JOIN zawodnicy AS z1 ON g.zawodnik_1 = z1.id  -- LEFT JOIN, aby pokazać wszystkie gry, nawet jeśli nie ma zawodnika
            LEFT JOIN zawodnicy AS z2 ON g.zawodnik_2 = z2.id
            LEFT JOIN zawodnicy AS z3 ON g.zawodnik_3 = z3.id
            LEFT JOIN zawodnicy AS z4 ON g.zawodnik_4 = z4.id
            WHERE zawodnik_1 = ? OR zawodnik_2 = ? OR zawodnik_3 = ? OR zawodnik_4 = ?
        """, (self.zawodnik_id, self.zawodnik_id, self.zawodnik_id, self.zawodnik_id))
        gry = cursor.fetchall()

        self.table.setRowCount(len(gry))
        self.table.setColumnCount(len(gry[0])+1 if gry else 0)
        num_display_columns = 11 #
        bold_font = QFont()
        bold_font.setBold(True)
        if gry:
            self.table.setHorizontalHeaderLabels([description[0] for description in cursor.description])
            for i, gra in enumerate(gry):
                for j, value in enumerate(gra):
                    item = QTableWidgetItem(str(value))

                    self.table.setItem(i, j, item)
                    # Dodawanie przycisku "Aktualizuj"
                button = QPushButton()
                button.setIcon(QIcon("icons/calculator.png"))
                button.setToolTip("Aktualizuj")
                button.clicked.connect(lambda _, gra_id=gra[0], data_gry=gra: self.aktualizuj_gre(gra_id, data_gry))
                self.table.setCellWidget(i, len(gra), button)  # Dodanie przycisku do ostatniej kolumny 

        self.table.resizeColumnsToContents() # Dopasowanie szerokości kolumn

    def aktualizuj_gre(self, gra_id, data_gry):  # Dodana metoda
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry, self)
        self.formularz_aktualizacji.show()