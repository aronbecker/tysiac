# formularz_aktualizacji_gry.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)

class FormularzAktualizacjiGry(QWidget):
    def __init__(self, conn, gra_id, data_gry, parent_table_widget=None, bundle_dir=None):
        super().__init__()
        self.setWindowTitle(f"Aktualizacja Gry {gra_id}")
        self.conn = conn
        self.gra_id = gra_id
        self.data_gry = data_gry
        self.parent_table_widget = parent_table_widget
        self.bundle_dir = bundle_dir

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        # Indeksy w tupli data_gry:
        # [4] = zawodnik_1, [8] = wynik_1
        # [5] = zawodnik_2, [9] = wynik_2
        # [6] = zawodnik_3, [10] = wynik_3
        # [7] = zawodnik_4, [11] = wynik_4

        # Zawodnik 1
        nazwa_zawodnika_1 = self.data_gry[4]
        self.wynik_1_label = QLabel(f"{nazwa_zawodnika_1}:")
        self.wynik_1_input = QLineEdit(str(self.data_gry[8] if self.data_gry[8] is not None else 0))
        self.form_layout.addRow(self.wynik_1_label, self.wynik_1_input)

        # Zawodnik 2
        nazwa_zawodnika_2 = self.data_gry[5]
        self.wynik_2_label = QLabel(f"{nazwa_zawodnika_2}:")
        self.wynik_2_input = QLineEdit(str(self.data_gry[9] if self.data_gry[9] is not None else 0))
        self.form_layout.addRow(self.wynik_2_label, self.wynik_2_input)

        # Zawodnik 3
        nazwa_zawodnika_3 = self.data_gry[6]
        self.wynik_3_label = QLabel(f"{nazwa_zawodnika_3}:")
        self.wynik_3_input = QLineEdit(str(self.data_gry[10] if self.data_gry[10] is not None else 0))
        self.form_layout.addRow(self.wynik_3_label, self.wynik_3_input)

        # Zawodnik 4 (Warunkowo)
        self.nazwa_zawodnika_4 = self.data_gry[7] 
        
        if self.nazwa_zawodnika_4 is not None:
            self.wynik_4_label = QLabel(f"{self.nazwa_zawodnika_4}:")
            self.wynik_4_input = QLineEdit(str(self.data_gry[11] if self.data_gry[11] is not None else 0))
            self.form_layout.addRow(self.wynik_4_label, self.wynik_4_input)

        self.aktualizuj_button = QPushButton("Aktualizuj")
        self.aktualizuj_button.clicked.connect(self.aktualizuj_gre)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.aktualizuj_button)

        self.setLayout(self.layout)

    def aktualizuj_gre(self):
        try:
            # Pobranie danych z formularza
            wynik_1 = int(self.wynik_1_input.text() or 0)
            wynik_2 = int(self.wynik_2_input.text() or 0)
            wynik_3 = int(self.wynik_3_input.text() or 0)

            wynik_4 = 0
            if self.nazwa_zawodnika_4 is not None:
                wynik_4_text = self.wynik_4_input.text()
                wynik_4 = int(wynik_4_text or 0)

            # Aktualizacja danych w bazie
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE gra
                SET wynik_1 = ?, wynik_2 = ?, wynik_3 = ?, wynik_4 = ?
                WHERE id = ?
            ''', (wynik_1, wynik_2, wynik_3, wynik_4, self.gra_id))
            self.conn.commit()

            print(f"Gra ID {self.gra_id} zaktualizowana.")
            QMessageBox.information(self, "Sukces", "Dane gry zostały zaktualizowane.")

            # --- KLUCZOWA ZMIANA ---
            # Zamiast 'self.close()', zarządzamy powrotem w QStackedWidget
            
            if self.parent_table_widget:
                # 1. Odśwież dane w widoku gier (w tle)
                self.parent_table_widget.load_data()
                
                # 2. Sprawdź, czy rodzic (WidokZarzadzaniaGrami) ma dostęp do głównego stacka
                # (Zmieniliśmy nazwę atrybutu na 'main_app_stacked_widget' w WidokZarzadzaniaGrami)
                if hasattr(self.parent_table_widget, 'main_app_stacked_widget') and self.parent_table_widget.main_app_stacked_widget is not None:
                    
                    # 3. Pobierz ten stack
                    main_stack = self.parent_table_widget.main_app_stacked_widget
                    
                    # 4. Ustaw widok gier (rodzica) jako aktywny
                    main_stack.setCurrentWidget(self.parent_table_widget)
                    
                    # 5. Usuń ten formularz (self) ze stacka
                    main_stack.removeWidget(self)
                    
                else:
                    # Plan awaryjny, jeśli był otwarty jako osobne okno
                    self.close()
            else:
                # Jeśli nie ma rodzica, też zamknij
                self.close()
            
            # Usunęliśmy 'self.close()' stąd, ponieważ logika jest teraz powyżej

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", f"Nieprawidłowe dane w formularzu: {e}. Wyniki muszą być liczbami całkowitymi.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas aktualizacji gry w bazie danych: {e}")
            self.conn.rollback()