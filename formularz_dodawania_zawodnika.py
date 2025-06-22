import os
import pandas as pd # <-- Dodaj ten import!
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFileDialog) # <-- Dodaj QFileDialog!
from PyQt5.QtCore import pyqtSignal

from sqlite.zawodnik import Zawodnik # Assuming Zawodnik class is correctly modified to accept 'conn'

class FormularzDodawaniaZawodnika(QWidget):
    player_added = pyqtSignal()

    def __init__(self, conn, tabela_zawodnikow, bundle_dir):
        super().__init__()
        self.setWindowTitle("Dodaj Zawodnika")
        self.tabela_zawodnikow = tabela_zawodnikow
        self.conn = conn
        self.bundle_dir = bundle_dir
        self.layout = QVBoxLayout()

        # Pola formularza
        self.firstname_label = QLabel("Imię:")
        self.firstname_input = QLineEdit()
        self.lastname_label = QLabel("Nazwisko:")
        self.lastname_input = QLineEdit()
        self.points_label = QLabel("Punkty:")
        self.points_input = QLineEdit("0") # Domyślna wartość 0 dla punktów
        self.kolejnosc_label = QLabel("Kolejność:")
        self.kolejnosc_input = QLineEdit("0") # Domyślna wartość 0 dla kolejności

        self.dodaj_button = QPushButton("Dodaj ręcznie")
        self.dodaj_button.clicked.connect(self.dodaj_zawodnika_recznie) # Zmieniona nazwa metody

        # --- NOWY ELEMENT: Przycisk do wczytywania z pliku XLSX ---
        self.zaladuj_xlsx_button = QPushButton("Wczytaj z pliku XLSX")
        self.zaladuj_xlsx_button.clicked.connect(self.wczytaj_zawodnikow_z_xlsx)
        # -----------------------------------------------------------

        form_layout = QFormLayout()
        form_layout.addRow(self.firstname_label, self.firstname_input)
        form_layout.addRow(self.lastname_label, self.lastname_input)
        form_layout.addRow(self.points_label, self.points_input)
        form_layout.addRow(self.kolejnosc_label, self.kolejnosc_input)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.dodaj_button)
        self.layout.addWidget(self.zaladuj_xlsx_button) # <-- Dodaj nowy przycisk do layoutu
        self.setLayout(self.layout)

    # Zmieniona nazwa dla jasności, że to dodawanie pojedynczego zawodnika
    def dodaj_zawodnika_recznie(self):
        firstname = self.firstname_input.text().strip()
        lastname = self.lastname_input.text().strip()
        points_text = self.points_input.text().strip()
        kolejnosc_text = self.kolejnosc_input.text().strip()

        if not all([firstname, lastname, points_text, kolejnosc_text]):
            QMessageBox.warning(self, "Błąd", "Wszystkie pola muszą być wypełnione.")
            return

        try:
            points = int(points_text)
            kolejnosc = int(kolejnosc_text)
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Punkty i Kolejność muszą być liczbami całkowitymi.")
            return

        # Użyj wspólnej metody do dodawania zawodnika do bazy
        self._add_single_player_to_db(firstname, lastname, points, kolejnosc)


    # --- NOWA METODA: Wczytywanie zawodników z pliku XLSX ---
    def wczytaj_zawodnikow_z_xlsx(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Opcjonalnie, jeśli chcesz używać niestandardowego okna dialogowego Qt
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Wybierz plik XLSX",
                                                   "", # Domyślna ścieżka - pusta oznacza ostatnio używaną
                                                   "Pliki Excela (*.xlsx);;Wszystkie pliki (*)",
                                                   options=options)

        if file_name:
            try:
                # Wczytaj dane z pliku XLSX
                # Nagłówki kolumn są domyślnie brane z pierwszego wiersza
                df = pd.read_excel(file_name)

                # Sprawdź, czy kolumny 'Imię' i 'Nazwisko' istnieją
                # W pandas odwołujemy się do kolumn po ich nazwach.
                # Upewnij się, że nazwy kolumn w pliku XLSX są dokładnie 'Imię' i 'Nazwisko'
                if 'Imię' not in df.columns or 'Nazwisko' not in df.columns:
                    QMessageBox.warning(self, "Błąd",
                                        "Plik XLSX musi zawierać kolumny 'Imię' i 'Nazwisko'. "
                                        "Sprawdź pisownię i wielkość liter.")
                    return

                liczba_dodanych = 0
                for index, row in df.iterrows():
                    # Odczytaj imię i nazwisko z wiersza
                    firstname = str(row['Imię']).strip()
                    lastname = str(row['Nazwisko']).strip()

                    # Użyj domyślnych wartości dla punktów i kolejności (np. 0),
                    # ponieważ plik XLSX ich nie zawiera zgodnie z opisem
                    points = 0
                    kolejnosc = 0

                    # Dodaj zawodnika do bazy danych
                    if firstname and lastname: # Upewnij się, że pola nie są puste
                        self._add_single_player_to_db(firstname, lastname, points, kolejnosc, show_message=False)
                        liczba_dodanych += 1

                if liczba_dodanych > 0:
                    QMessageBox.information(self, "Sukces",
                                            f"Pomyślnie dodano {liczba_dodanych} zawodników z pliku XLSX.")
                    self.player_added.emit() # Wyślij sygnał, aby odświeżyć główną tabelę
                    self.close() # Zamknij formularz po załadowaniu
                else:
                    QMessageBox.warning(self, "Informacja", "W pliku XLSX nie znaleziono żadnych nowych zawodników do dodania.")

            except FileNotFoundError:
                QMessageBox.warning(self, "Błąd", "Nie wybrano pliku.")
            except pd.errors.EmptyDataError:
                QMessageBox.warning(self, "Błąd", "Wybrany plik XLSX jest pusty.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas wczytywania pliku: {e}")

    # --- NOWA METODA: Prywatna pomocnicza metoda do dodawania zawodnika do bazy danych ---
    # Używamy jej zarówno dla ręcznego dodawania, jak i dla importu z pliku,
    # aby uniknąć duplikacji kodu.
    def _add_single_player_to_db(self, firstname, lastname, points, kolejnosc, show_message=True):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("INSERT INTO zawodnicy (firstname, lastname, points, kolejnosc) VALUES (?, ?, ?, ?)",
                                (firstname, lastname, points, kolejnosc))
            self.conn.commit()

            # Odśwież główną tabelę tylko raz po zaimportowaniu wszystkich danych z pliku,
            # lub po dodaniu pojedynczego zawodnika.
            if show_message: # Tylko jeśli to dodawanie ręczne
                self.tabela_zawodnikow.load_data()
                QMessageBox.information(self, "Sukces", "Zawodnik został dodany.")
                self.player_added.emit()
                self.close()
            # Dla importu z pliku, load_data() i player_added.emit() wywoływane są raz na końcu importu

        except Exception as e:
            QMessageBox.critical(self, "Błąd Bazy Danych", f"Wystąpił błąd podczas dodawania zawodnika: {e}")
            self.conn.rollback()