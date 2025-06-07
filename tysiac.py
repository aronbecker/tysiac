import sys
import sqlite3
from sqlite.zawodnik import Zawodnik
from sqlite.gra import Gra
import random
from datetime import date


from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
                             QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Turniej w tysiąca 1.0")

        # Połączenie z bazą danych
        self.conn = sqlite3.connect('sqlite/my.db')  # Zmień nazwę bazy danych
        self.cursor = self.conn.cursor()

        # Pobierz dane turnieju (załóżmy, że jest tylko jeden aktywny turniej)
        self.cursor.execute("SELECT name, begin_date FROM turniej LIMIT 1")  # Dostosuj zapytanie
        turniej_data = self.cursor.fetchone()

        if turniej_data:
            turniej_name, begin_date = turniej_data
        else:
            turniej_name = "Brak danych turnieju"
            begin_date = ""

        # Nagłówek
        header_layout = QHBoxLayout()
        name_label = QLabel(f"Turniej: {turniej_name}")
        date_label = QLabel(f"Data: {begin_date}")

        name_label.setStyleSheet("font-size: 18px; font-weight: bold;") # Dodano style
        date_label.setStyleSheet("font-size: 16px;") # Dodano style

        header_layout.addWidget(name_label)
        header_layout.addWidget(date_label)

        # Przyciski
        lista_zawodnikow_button = QPushButton("Lista zawodników")
        dodaj_zawodnika_button = QPushButton("Dodaj zawodnika")
        rundy_button = QPushButton("Rundy")
        dodaj_turniej_button = QPushButton("Dodaj turniej")

        # Layout główny
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(lista_zawodnikow_button)
        main_layout.addWidget(dodaj_zawodnika_button)
        main_layout.addWidget(rundy_button)
        main_layout.addWidget(dodaj_turniej_button) 

        self.setLayout(main_layout)

        # Podłączenie akcji do przycisków
        lista_zawodnikow_button.clicked.connect(self.pokaz_liste_zawodnikow)
        dodaj_zawodnika_button.clicked.connect(self.otworz_formularz_dodawania_zawodnika)
        rundy_button.clicked.connect(self.pokaz_liste_rund)
        dodaj_turniej_button.clicked.connect(self.otworz_formularz_dodawania_turnieju)  # Podłączenie sygnału

    def pokaz_liste_zawodnikow(self):
        self.okno_lista_zawodnikow = TabelaZawodnikow(self.conn)
        self.okno_lista_zawodnikow.show()

    def otworz_formularz_dodawania_zawodnika(self):
        self.formularz_dodawania = FormularzDodawaniaZawodnika(self.conn)
        self.formularz_dodawania.show()

    def pokaz_liste_rund(self):
        self.okno_lista_rund = TabelaRund(self.conn)
        self.okno_lista_rund.show()

    def otworz_formularz_dodawania_turnieju(self):
        self.formularz_dodawania_turnieju = FormularzDodawaniaTurnieju(self.conn)
        self.formularz_dodawania_turnieju.show()

class FormularzDodawaniaTurnieju(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Dodaj Turniej")
        self.conn = conn

        self.layout = QVBoxLayout()

        # Pola formularza
        self.form_layout = QFormLayout()
        self.name_label = QLabel("Nazwa:")
        self.name_input = QLineEdit()
        self.begin_date_label = QLabel("Data rozpoczęcia (YYYY-MM-DD):")
        self.begin_date_input = QLineEdit(date.today().strftime("%Y-%m-%d"))  # Ustawienie domyślnej daty
        self.tables_number_label = QLabel("Liczba stołów:")
        self.tables_number_input = QLineEdit()
        self.rounds_number_label = QLabel("Liczba rund:")
        self.rounds_number_input = QLineEdit()

        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.begin_date_label, self.begin_date_input)
        self.form_layout.addRow(self.tables_number_label, self.tables_number_input)
        self.form_layout.addRow(self.rounds_number_label, self.rounds_number_input)

        # Przycisk "Dodaj"
        self.dodaj_button = QPushButton("Dodaj")
        self.dodaj_button.clicked.connect(self.dodaj_turniej)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.dodaj_button)

        self.setLayout(self.layout)

    def dodaj_turniej(self):
        try:
            name = self.name_input.text()
            begin_date = self.begin_date_input.text()
            tables_number = int(self.tables_number_input.text())
            rounds_number = int(self.rounds_number_input.text())

            if not all([name, begin_date, tables_number, rounds_number]):
                raise ValueError("Wszystkie pola muszą być wypełnione.")

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO turniej (name, begin_date, tables_number, rounds_number) 
                VALUES (?, ?, ?, ?)
            ''', (name, begin_date, tables_number, rounds_number))
            self.conn.commit()
            QMessageBox.information(self, "Sukces", "Turniej został dodany.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))


class TabelaZawodnikow(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Lista Zawodników")
        self.setFixedSize(1200, 900) 

        self.table = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.conn = conn
        self.load_data()

    def load_data(self):
         self.cursor = self.conn.cursor()
         self.cursor.execute("SELECT * FROM zawodnicy")
         data = self.cursor.fetchall()

         # Ustaw liczbę wierszy i kolumn
         self.table.setRowCount(len(data))
         self.table.setColumnCount(len(data[0]) if data else 0)  # Obsługa pustej tabeli

         # Ustaw nagłówki kolumn (opcjonalne)
         if data:
             headers = [description[0] for description in self.cursor.description]
             self.table.setHorizontalHeaderLabels(headers)
             
             # Wstaw dane do tabeli
             for row_index, row_data in enumerate(data):
                 for col_index, cell_data in enumerate(row_data):
                     item = QTableWidgetItem(str(cell_data))
                     self.table.setItem(row_index, col_index, item)

# class TabelaRund(QWidget):

#     def __init__(self, conn):
#         super().__init__()
#         self.setWindowTitle("List rund")
#         self.table = QTableWidget()
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.table)
#         self.setLayout(self.layout)

#         self.conn = conn
#         self.load_data()

#     def load_data(self):
#          self.cursor = self.conn.cursor()
#          self.cursor.execute("SELECT * FROM runda")
#          data = self.cursor.fetchall()

#          # Ustaw liczbę wierszy i kolumn
#          self.table.setRowCount(len(data))
#          self.table.setColumnCount(len(data[0]) if data else 0)  # Obsługa pustej tabeli

#          # Ustaw nagłówki kolumn (opcjonalne)
#          if data:
#              headers = [description[0] for description in self.cursor.description]
#              self.table.setHorizontalHeaderLabels(headers)
             
#              # Wstaw dane do tabeli
#              for row_index, row_data in enumerate(data):
#                  for col_index, cell_data in enumerate(row_data):
#                      item = QTableWidgetItem(str(cell_data))
#                      self.table.setItem(row_index, col_index, item)

class TabelaRund(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Lista Rund")
        self.setFixedSize(1200, 900) 
        self.conn = conn
        self.table = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM runda")
        rundy = cursor.fetchall()

        self.table.setRowCount(len(rundy))
        self.table.setColumnCount(7)  # 4 kolumny danych + 2 na przycisk
        self.table.setHorizontalHeaderLabels(["ID", "Nazwa", "Priorytet", "Turniej ID", "Akcje"])

        for i, runda in enumerate(rundy):
            for j, value in enumerate(runda):
                item = QTableWidgetItem(str(value))
                self.table.setItem(i, j, item)

            # Dodawanie przycisku "Pokaż szczegóły"
            button = QPushButton("Pokaż szczegóły")
            button.clicked.connect(lambda _, runda_id=runda[0]: self.pokaz_szczegoly_rundy(runda_id))
            self.table.setCellWidget(i, 4, button)  # Dodanie przycisku do 5. kolumny

            # Dodawanie przycisku "Usuń" do osobnej kolumny
            usun_button = QPushButton("Usuń")
            usun_button.clicked.connect(lambda _, runda_id=runda[0]: self.usun_runde(runda_id))
            self.table.setCellWidget(i, 5, usun_button)  

            # Dodawanie przycisku "Losuj"
            losuj_button = QPushButton("Losuj")
            losuj_button.clicked.connect(lambda _, runda_id=runda[0]: self.losuj_gry(runda_id, runda[3]))
            self.table.setCellWidget(i, 6, losuj_button) 



    def pokaz_szczegoly_rundy(self, runda_id):
        self.szczegoly_rundy_window = TabelaGier(self.conn, runda_id)
        self.szczegoly_rundy_window.show()

    def usun_runde(self, runda_id):
        # Potwierdzenie usunięcia
        odpowiedz = QMessageBox.question(
            self, 
            "Potwierdzenie usunięcia", 
            f"Czy na pewno chcesz usunąć rundę o ID {runda_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if odpowiedz == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM runda WHERE id = ?", (runda_id,))
                self.conn.commit()
                self.load_data()  # Odświeżenie tabeli po usunięciu
                QMessageBox.information(self, "Sukces", "Runda została usunięta.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć rundy: {e}")

    def losuj_gry(self, runda_id, turniej_id):
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT tables_number FROM turniej WHERE id = ?", (turniej_id,))
            turniej_data = cursor.fetchone()
            liczba_stolow = turniej_data[0]

            #Pobranie listy dostępnych zawodników
            cursor.execute("SELECT id FROM zawodnicy")
            zawodnicy = [row[0] for row in cursor.fetchall()]

            # Jeśli jest mniej niż 3 zawodników, nie można utworzyć gry
            if len(zawodnicy) < 3:
                QMessageBox.warning(self, "Błąd", "Za mało zawodników, aby utworzyć grę.")
                return

            random.shuffle(zawodnicy)  # Losowe tasowanie listy zawodników
            dzisiejsza_data = date.today().strftime("%Y-%m-%d")
            numer_stolika = 1
            lista_gier = []
            # Tworzenie gier (po 3 zawodników)
            while len(zawodnicy) >= 3:
                zawodnik_1 = zawodnicy.pop()
                zawodnik_2 = zawodnicy.pop()
                zawodnik_3 = zawodnicy.pop()

                if len(zawodnicy) == 8 or len(zawodnicy) == 4:
                    zawodnik_4 = zawodnicy.pop()
                    # Dodawanie gry z 4 zawodnikami do bazy danych
                    cursor.execute('''
                        INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
                    ''', (dzisiejsza_data, runda_id, turniej_id, dzisiejsza_data, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4))
                else:
                    # Dodawanie gry z 3 zawodnikami do bazy danych
                    cursor.execute('''
                        INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, wynik_1, wynik_2, wynik_3) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
                    ''', (dzisiejsza_data, runda_id, turniej_id, dzisiejsza_data, zawodnik_1, zawodnik_2, zawodnik_3))
                numer_stolika+=1
                lista_gier.append(cursor.lastrowid)


            self.conn.commit()
            QMessageBox.information(self, "Sukces", "Gry zostały wylosowane.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wylosować gier: {e}")


class TabelaGier(QWidget):
    def __init__(self, conn, runda_id):
        super().__init__()
        self.setWindowTitle(f"Lista Gier dla Rundy {runda_id}")
        self.setFixedSize(1200, 900) 
        self.conn = conn
        self.runda_id = runda_id
        self.table = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        # cursor.execute("SELECT * FROM gra WHERE runda_id = ?", (self.runda_id,))
        cursor.execute('''
            SELECT
                g.id,
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
            WHERE g.runda_id = ?
        ''', (self.runda_id,))
        gry = cursor.fetchall()

        self.table.setRowCount(len(gry))
        self.table.setColumnCount(len(gry[0])+1 if gry else 0)
        if gry:
            self.table.setHorizontalHeaderLabels([description[0] for description in cursor.description])
            for i, gra in enumerate(gry):
                for j, value in enumerate(gra):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(i, j, item)
                # Dodawanie przycisku "Aktualizuj"
                button = QPushButton("Aktualizuj")
                button.clicked.connect(lambda _, gra_id=gra[0], data_gry=gra: self.aktualizuj_gre(gra_id, data_gry))
                self.table.setCellWidget(i, len(gra), button)  # Dodanie przycisku do ostatniej kolumny 
        self.table.resizeColumnsToContents() 

    def aktualizuj_gre(self, gra_id, data_gry):  # Dodana metoda
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry, self)
        self.formularz_aktualizacji.show()

class FormularzAktualizacjiGry(QWidget):
    def __init__(self, conn, gra_id, data_gry, parent=None):
        super().__init__()
        self.setWindowTitle(f"Aktualizacja Gry {gra_id}")
        self.conn = conn
        self.gra_id = gra_id
        self.data_gry = data_gry  # Przechowujemy dane gry
        self.parent = parent

        self.layout = QVBoxLayout()

        # Tworzenie pól formularza - tylko dla wyników
        self.form_layout = QFormLayout()
        self.wynik_1_label = QLabel("Wynik 1:")
        self.wynik_1_input = QLineEdit(str(self.data_gry[8]))  # Ustawienie początkowej wartości dla wynik_1
        self.form_layout.addRow(self.wynik_1_label, self.wynik_1_input)
        self.wynik_2_label = QLabel("Wynik 2:")
        self.wynik_2_input = QLineEdit(str(self.data_gry[9]))  # Ustawienie początkowej wartości dla wynik_2
        self.form_layout.addRow(self.wynik_2_label, self.wynik_2_input)
        self.wynik_3_label = QLabel("Wynik 3:")
        self.wynik_3_input = QLineEdit(str(self.data_gry[10]))  # Ustawienie początkowej wartości dla wynik_3
        self.form_layout.addRow(self.wynik_3_label, self.wynik_3_input)
        self.wynik_4_label = QLabel("Wynik 4:")
        self.wynik_4_input = QLineEdit(str(self.data_gry[11]))  # Ustawienie początkowej wartości dla wynik_4
        self.form_layout.addRow(self.wynik_4_label, self.wynik_4_input)

        self.aktualizuj_button = QPushButton("Aktualizuj")
        self.aktualizuj_button.clicked.connect(self.aktualizuj_gre)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.aktualizuj_button)

        self.setLayout(self.layout)

    def aktualizuj_gre(self):
        try:
            # Pobranie danych z formularza - tylko wyniki
            wynik_1 = int(self.wynik_1_input.text())
            wynik_2 = int(self.wynik_2_input.text())
            wynik_3 = int(self.wynik_3_input.text())
            
            if self.wynik_4_input.text() == 'None':
                wynik_4 = 0
            else:
                wynik_4 = int(self.wynik_4_input.text())

            # Aktualizacja danych w bazie - tylko wyniki
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE gra 
                SET wynik_1 = ?, wynik_2 = ?, wynik_3 = ?, wynik_4 = ?
                WHERE id = ?
            ''', (wynik_1, wynik_2, wynik_3, wynik_4, self.gra_id))
            self.conn.commit()
            print(self.gra_id)
            QMessageBox.information(self, "Sukces", "Dane gry zostały zaktualizowane.")
            if self.parent:  # Sprawdzenie, czy rodzic istnieje
                self.parent.load_data()  # Wywołanie load_data w rodzicu (TabelaGier)
                self.parent.show()  # Ponowne otwarcie okna TabelaGier
            self.close()
            # TabelaGier.load_data(self)  # Odświeżenie danych w tabeli gier

        except ValueError:
            QMessageBox.warning(self, "Błąd", "Nieprawidłowe dane w formularzu.")


class FormularzDodawaniaZawodnika(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Dodaj Zawodnika")

        self.conn = conn
        self.layout = QVBoxLayout()

        self.firstname_label = QLabel("Imię:")
        self.firstname_input = QLineEdit()
        self.lastname_label = QLabel("Nazwisko:")
        self.lastname_input = QLineEdit()
        self.points_label = QLabel("Punkty:")
        self.points_input = QLineEdit()

        self.dodaj_button = QPushButton("Dodaj")
        self.dodaj_button.clicked.connect(self.dodaj_zawodnika)

        form_layout = QFormLayout()
        form_layout.addRow(self.firstname_label, self.firstname_input)
        form_layout.addRow(self.lastname_label, self.lastname_input)
        form_layout.addRow(self.points_label, self.points_input)
        

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.dodaj_button)
        self.setLayout(self.layout)

    def dodaj_zawodnika(self):
        firstname = self.firstname_input.text()
        lastname = self.lastname_input.text()
        points = self.points_input.text()

        if not firstname or not lastname or not points:
            QMessageBox.warning(self, "Błąd", "Wszystkie pola muszą być wypełnione.")
            return

        try:
            points = int(points)  # Konwersja na int
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Punkty muszą być liczbą całkowitą.")
            return

        Zawodnik1 = Zawodnik(firstname, lastname, points)
        print(Zawodnik1.firstname, Zawodnik1.lastname, Zawodnik1.points)
        Zawodnik1.zapisz()
        # self.cursor = self.conn.cursor()
        # self.cursor.execute("INSERT INTO zawodnicy (firstname, lastname, points) VALUES (?, ?, ?)",
        #                     (firstname, lastname, points))
        # self.conn.commit()

        # self.close() # Zamknij formularz po dodaniu zawodnika

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())