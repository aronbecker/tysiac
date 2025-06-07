from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, QComboBox)

from tabela_gier import TabelaGier
from formularz_dodawania_rund import FormularzDodawaniaRundy
import random
from datetime import date
from PyQt5.QtGui import QIcon

class TabelaRund(QWidget):
    def __init__(self, conn, stacked_widget, turniej_id):
        super().__init__()
        self.turniej_id = turniej_id
        self.setWindowTitle("Lista Rund")
        self.setFixedSize(1200, 900) 
        self.conn = conn
        self.table = QTableWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        # Dodanie przycisku "Dodaj rundę"
        dodaj_runde_button = QPushButton("Dodaj rundę")
        dodaj_runde_button.clicked.connect(self.otworz_formularz_dodawania_rundy)
        
        self.layout.addWidget(dodaj_runde_button)  # Dodanie przycisku do layoutu
        self.load_data()
        self.stacked_widget = stacked_widget 





    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM runda")
        rundy = cursor.fetchall()

        self.table.setRowCount(len(rundy))
        self.table.setColumnCount(8)  # 4 kolumny danych + 2 na przycisk
        self.table.setHorizontalHeaderLabels(["ID", "Nazwa", "Priorytet", "Turniej ID", "Szczegóły", "Losuj", "Wyczyść", "Usuń"])

        for i, runda in enumerate(rundy):
            for j, value in enumerate(runda):
                item = QTableWidgetItem(str(value))
                self.table.setItem(i, j, item)

            # Dodawanie przycisku "Pokaż szczegóły"
            button = QPushButton()
            button.setIcon(QIcon("icons/eye.png"))
            button.setToolTip("Pokaż szczegóły")
            button.clicked.connect(lambda _, runda_id=runda[0]: self.pokaz_szczegoly_rundy(runda_id))
            self.table.setCellWidget(i, 4, button)  # Dodanie przycisku do 5. kolumny



            # Dodawanie przycisku "Losuj"
            losuj_button = QPushButton()
            losuj_button.setIcon(QIcon("icons/draw.png"))
            losuj_button.setToolTip("Losuj gry w rundzie")
            losuj_button.clicked.connect(lambda _, runda_id=runda[0]: self.losuj_gry(runda_id,  self.turniej_id))
            self.table.setCellWidget(i, 5, losuj_button)

            # Dodawanie przycisku "Wyczyść"
            wyczysc_button = QPushButton()
            wyczysc_button.setIcon(QIcon("icons/clean.png"))
            wyczysc_button.setToolTip("Wyczyść gry w rundzie")
            wyczysc_button.clicked.connect(lambda _, runda_id=runda[0]: self.wyczysc_gry(runda_id))
            self.table.setCellWidget(i, 6, wyczysc_button)  # Dodanie przycisku "Wyczyść" do 8. kolumny

            # Dodawanie przycisku "Usuń" do osobnej kolumny
            usun_button = QPushButton()
            usun_button.setIcon(QIcon("icons/trash.png"))
            usun_button.setToolTip("Usuń rundę")
            usun_button.clicked.connect(lambda _, runda_id=runda[0]: self.usun_runde(runda_id))
            self.table.setCellWidget(i, 7, usun_button)  

        self.table.resizeColumnsToContents() # Dopasowanie szerokości kolumn



    def pokaz_szczegoly_rundy(self, runda_id):
        self.szczegoly_rundy_window = TabelaGier(self.conn, runda_id)
        self.stacked_widget.addWidget(self.szczegoly_rundy_window)  # Dodanie do QStackedWidget
        self.stacked_widget.setCurrentWidget(self.szczegoly_rundy_window)  # Przełączenie widoku

    def otworz_formularz_dodawania_rundy(self):
        self.formularz_dodawania_rundy = FormularzDodawaniaRundy(self.conn, self, self.turniej_id)  # Przekazanie self (referencji do TabelaRund)
        self.stacked_widget.addWidget(self.formularz_dodawania_rundy)
        self.stacked_widget.setCurrentWidget(self.formularz_dodawania_rundy)

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
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM gra WHERE runda_id = ?", (runda_id,))
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
            cursor.execute("SELECT id FROM zawodnicy ORDER BY kolejnosc DESC")
            zawodnicy = [row[0] for row in cursor.fetchall()]

            # Jeśli jest mniej niż 3 zawodników, nie można utworzyć gry
            if len(zawodnicy) < 3:
                QMessageBox.warning(self, "Błąd", "Za mało zawodników, aby utworzyć grę.")
                return

            #random.shuffle(zawodnicy)  # Losowe tasowanie listy zawodników
            dzisiejsza_data = date.today().strftime("%Y-%m-%d")
            numer_stolika = 1
            lista_gier = []
            # Tworzenie gier (po 3 zawodników)
            while len(zawodnicy) >= 3:


                if len(zawodnicy) == 8 or len(zawodnicy) == 4:
                    zawodnik_1 = zawodnicy.pop()
                    zawodnik_2 = zawodnicy.pop()
                    zawodnik_3 = zawodnicy.pop()
                    zawodnik_4 = zawodnicy.pop()
                    # Dodawanie gry z 4 zawodnikami do bazy danych
                    cursor.execute('''
                        INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
                    ''', (dzisiejsza_data, runda_id, turniej_id, numer_stolika, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4))
                else:
                    zawodnik_1 = zawodnicy.pop()
                    zawodnik_2 = zawodnicy.pop()
                    zawodnik_3 = zawodnicy.pop()
                    # Dodawanie gry z 3 zawodnikami do bazy danych
                    cursor.execute('''
                        INSERT INTO gra (data, runda_id, turniej_id, stol, zawodnik_1, zawodnik_2, zawodnik_3, wynik_1, wynik_2, wynik_3) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
                    ''', (dzisiejsza_data, runda_id, turniej_id, numer_stolika, zawodnik_1, zawodnik_2, zawodnik_3))
                numer_stolika+=1
                lista_gier.append(cursor.lastrowid)


            self.conn.commit()
            QMessageBox.information(self, "Sukces", "Gry zostały wylosowane.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wylosować gier: {e}")

    def wyczysc_gry(self, runda_id):
        """Usuwa wszystkie gry przypisane do danej rundy."""
        # Potwierdzenie usunięcia
        odpowiedz = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć wszystkie gry dla rundy o ID {runda_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if odpowiedz == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM gra WHERE runda_id = ?", (runda_id,))
                self.conn.commit()
                QMessageBox.information(self, "Sukces", "Gry zostały usunięte.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć gier: {e}")
