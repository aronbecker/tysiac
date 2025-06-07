from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QPushButton, QMessageBox, QComboBox, QHBoxLayout)
from PyQt5.QtGui import QIcon
from formularz_edycji_zawodnika import FormularzEdycjiZawodnika
from tabela_gier_zawodnika import TabelaGierZawodnika

import random

class TabelaZawodnikow(QWidget):
    def __init__(self, conn, turniej_id, stacked_widget):
        super().__init__()
        self.setWindowTitle("Lista Zawodników")
        # self.setFixedSize(1200, 900) 
        self.stacked_widget = stacked_widget 

        # Dodanie listy wyboru kolumn i przycisku "Sortuj"
        self.sort_column_combo = QComboBox()
        self.sort_column_combo.addItems(["id", "firstname", "lastname", "points", "kolejnosc"])  # Dodaj nazwy kolumn

        self.sort_direction = QComboBox()
        self.sort_direction.addItems(["ASC", "DESC"])  # Dodaj rodzaj sortowanie

        sort_button = QPushButton("Sortuj")
        sort_button.clicked.connect(self.sort_zawodnicy)


        # Dodanie widgetów do layoutu
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(self.sort_column_combo)
        sort_layout.addWidget(self.sort_direction)
        sort_layout.addWidget(sort_button)


        self.table = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(sort_layout)  # Dodanie layoutu sortowania nad tabelą
        

        # Dodanie przycisku "Losuj kolejność"
        losuj_kolejnosc_button = QPushButton("Losuj kolejność")
        losuj_kolejnosc_button.clicked.connect(self.losuj_kolejnosc)
        self.layout.addWidget(losuj_kolejnosc_button)  # Dodanie przycisku do layoutu

        # Dodanie przycisku "Ustaw kolejność wg punktów"
        ustaw_kolejnosc_button = QPushButton("Ustaw kolejność wg punktów")
        ustaw_kolejnosc_button.clicked.connect(self.ustaw_kolejnosc_wg_punktow)
        self.layout.addWidget(ustaw_kolejnosc_button)  # Dodanie przycisku do layoutu


        # Dodanie przycisku "Oblicz punkty dla wszystkich"
        oblicz_wszystkich_button = QPushButton("Oblicz punkty dla wszystkich")
        oblicz_wszystkich_button.clicked.connect(self.oblicz_punkty_wszystkich)
        self.layout.addWidget(oblicz_wszystkich_button)  # Dodanie przycisku do layoutu


        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.turniej_id = turniej_id



        self.conn = conn
        self.load_data()

    def load_data(self):
         self.cursor = self.conn.cursor()
         self.cursor.execute("SELECT * FROM zawodnicy")
         data = self.cursor.fetchall()

         # Ustaw liczbę wierszy i kolumn
         self.table.setRowCount(len(data))
         self.table.setColumnCount(9 if data else 0)  # Obsługa pustej tabeli

         # Ustaw nagłówki kolumn (opcjonalne)
         if data:
             headers = [description[0] for description in self.cursor.description]
            #  self.table.setHorizontalHeaderLabels(headers)
             self.table.setHorizontalHeaderLabels(["ID", "Imię", "Nazwisko", "Punkty", "Kolejność", "Oblicz","Szczegóły","Usuń", "Edytuj"])
             
             # Wstaw dane do tabeli
             for row_index, row_data in enumerate(data):
                 for col_index, cell_data in enumerate(row_data):
                     item = QTableWidgetItem(str(cell_data))
                     self.table.setItem(row_index, col_index, item)
                     
                 # Dodawanie przycisku "Oblicz"
                 oblicz_button = QPushButton()
                 oblicz_button.setIcon(QIcon("icons/calculator.png"))
                 oblicz_button.setToolTip("Oblicz punkty")
                 oblicz_button.clicked.connect(lambda _, zawodnik_id=row_data[0]: self.oblicz_punkty(zawodnik_id, self.turniej_id))
                 self.table.setCellWidget(row_index, 5, oblicz_button) 

                # Dodawanie przycisku "Szczegóły"
                 szczegoly_button = QPushButton()
                 szczegoly_button.setIcon(QIcon("icons/eye.png"))
                 szczegoly_button.setToolTip("Pokaż szczegóły")
                 szczegoly_button.clicked.connect(lambda _, zawodnik_id=row_data[0]: self.pokaz_szczegoly_zawodnika(zawodnik_id))
                 self.table.setCellWidget(row_index, 6, szczegoly_button)  # Dodanie przycisku "Szczegóły" do 7. kolumny

                 # Dodawanie przycisku "Usuń"
                 usun_button = QPushButton()
                 usun_button.setIcon(QIcon("icons/trash.png"))
                 usun_button.setToolTip("Usuń zawodnika")
                 usun_button.clicked.connect(lambda _, zawodnik_id=row_data[0]: self.usun_zawodnika(zawodnik_id))
                 self.table.setCellWidget(row_index, 7, usun_button)  # Dodanie do 6. kolumny

                 # Dodawanie przycisku "Edytuj"
                 edytuj_button = QPushButton()
                 edytuj_button.setIcon(QIcon("icons/pencil.png"))
                 edytuj_button.setToolTip("Edytuj zawodnika")
                 edytuj_button.clicked.connect(lambda _, zawodnik_id=row_data[0]: self.edytuj_zawodnika(zawodnik_id))
                 self.table.setCellWidget(row_index, 8, edytuj_button)  # Dodanie do 6. kolumny


        
         self.table.resizeColumnsToContents() # Dopasowanie szerokości kolumn


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

            # Aktualizacja punktów w tabeli `zawodnicy`
            cursor.execute("UPDATE zawodnicy SET points = ? WHERE id = ?", (punkty, zawodnik_id))
            self.conn.commit()

            # Odświeżenie tabeli
            self.load_data()

            # QMessageBox.information(self, "Sukces", f"Punkty zawodnika {zawodnik_id} zostały zaktualizowane.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć punktów: {e}")

    def sort_zawodnicy(self):
        """Sortuje zawodników za pomocą zapytania SQL."""
        column = self.sort_column_combo.currentText()  # Pobranie wybranej kolumny
        direction = self.sort_direction.currentText() # Pobranie rodzaju sortowania
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM zawodnicy ORDER BY {column} {direction}") # Zapytanie SQL z sortowaniem
            zawodnicy = cursor.fetchall()

            # Aktualizacja tabeli
            self.table.setRowCount(len(zawodnicy))
            for i, zawodnik in enumerate(zawodnicy):
                for j, value in enumerate(zawodnik):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(i, j, item)

                # Dodawanie przycisku "Oblicz"
                oblicz_button = QPushButton("Oblicz punkty")
                oblicz_button.clicked.connect(lambda _, zawodnik_id=zawodnik[0]: self.oblicz_punkty(zawodnik_id, self.turniej_id))
                self.table.setCellWidget(i, 5, oblicz_button) 

                # Dodawanie przycisku "Usuń"
                usun_button = QPushButton("Usuń")
                usun_button.clicked.connect(lambda _, zawodnik_id=zawodnik[0]: self.usun_zawodnika(zawodnik_id))
                self.table.setCellWidget(i, 6, usun_button)  # Dodanie do 6. kolumny

                # Dodawanie przycisku "Edytuj"
                edytuj_button = QPushButton("Edytuj")
                edytuj_button.clicked.connect(lambda _, zawodnik_id=zawodnik[0]: self.edytuj_zawodnika(zawodnik_id))
                self.table.setCellWidget(i, 7, edytuj_button)  # Dodanie do 6. kolumny

                # Dodawanie przycisku "Szczegóły"
                szczegoly_button = QPushButton("Szczegóły")
                szczegoly_button.clicked.connect(lambda _, zawodnik_id=zawodnik[0]: self.pokaz_szczegoly_zawodnika(zawodnik_id))
                self.table.setCellWidget(i, 8, szczegoly_button)  # Dodanie przycisku "Szczegóły" do 7. kolumny

            self.table.resizeColumnsToContents() # Dopasowanie szerokości kolumn

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się posortować zawodników: {e}")


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

            # QMessageBox.information(self, "Sukces", "Kolejność zawodników została wylosowana.")

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
        self.szczegoly_zawodnika_window = TabelaGierZawodnika(self.conn, zawodnik_id)  # Nowa klasa - patrz punkt 2
        self.stacked_widget.addWidget(self.szczegoly_zawodnika_window)
        self.stacked_widget.setCurrentWidget(self.szczegoly_zawodnika_window)