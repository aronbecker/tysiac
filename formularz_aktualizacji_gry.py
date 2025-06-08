# formularz_aktualizacji_gry.py
import os # <--- ADD THIS IMPORT
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)

# No direct database import needed, as it uses self.conn.

class FormularzAktualizacjiGry(QWidget):
    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, gra_id, data_gry, parent_table_widget=None, bundle_dir=None): # <--- ADDED bundle_dir, renamed parent for clarity
        super().__init__()
        self.setWindowTitle(f"Aktualizacja Gry {gra_id}")
        self.conn = conn
        self.gra_id = gra_id
        self.data_gry = data_gry
        self.parent_table_widget = parent_table_widget # Renamed for clarity, it refers to the table widget (e.g. TabelaGier)
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here (for future use if needed)

        self.layout = QVBoxLayout()

        # Tworzenie pól formularza - tylko dla wyników
        self.form_layout = QFormLayout()
        # Ensure default values are converted to string
        self.wynik_1_label = QLabel("Wynik 1:")
        self.wynik_1_input = QLineEdit(str(self.data_gry[8] if self.data_gry[8] is not None else 0)) # Default 0 if None
        self.form_layout.addRow(self.wynik_1_label, self.wynik_1_input)

        self.wynik_2_label = QLabel("Wynik 2:")
        self.wynik_2_input = QLineEdit(str(self.data_gry[9] if self.data_gry[9] is not None else 0)) # Default 0 if None
        self.form_layout.addRow(self.wynik_2_label, self.wynik_2_input)

        self.wynik_3_label = QLabel("Wynik 3:")
        self.wynik_3_input = QLineEdit(str(self.data_gry[10] if self.data_gry[10] is not None else 0)) # Default 0 if None
        self.form_layout.addRow(self.wynik_3_label, self.wynik_3_input)

        self.wynik_4_label = QLabel("Wynik 4:")
        # Handle case where wynik_4 might be None in DB (for 3-player games)
        self.wynik_4_input = QLineEdit(str(self.data_gry[11] if self.data_gry[11] is not None else 0)) # Default 0 if None
        self.form_layout.addRow(self.wynik_4_label, self.wynik_4_input)

        self.aktualizuj_button = QPushButton("Aktualizuj")
        self.aktualizuj_button.clicked.connect(self.aktualizuj_gre)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.aktualizuj_button)

        self.setLayout(self.layout)

    def aktualizuj_gre(self):
        try:
            # Pobranie danych z formularza - tylko wyniki
            wynik_1 = int(self.wynik_1_input.text() or 0) # Use 'or 0' to handle empty string as 0
            wynik_2 = int(self.wynik_2_input.text() or 0)
            wynik_3 = int(self.wynik_3_input.text() or 0)

            # Improved handling for wynik_4, treating empty/None as 0 or None if needed
            wynik_4_text = self.wynik_4_input.text()
            wynik_4 = None # Default to None for 3-player games
            if wynik_4_text and wynik_4_text.lower() != 'none': # If not empty and not 'None' string
                wynik_4 = int(wynik_4_text)
            else:
                wynik_4 = 0 # If it was a 4-player game, but now blank/None, default to 0

            # Aktualizacja danych w bazie - tylko wyniki
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE gra
                SET wynik_1 = ?, wynik_2 = ?, wynik_3 = ?, wynik_4 = ?
                WHERE id = ?
            ''', (wynik_1, wynik_2, wynik_3, wynik_4, self.gra_id)) # Pass None if you want actual NULL in DB for 4th player
            self.conn.commit()

            print(f"Gra ID {self.gra_id} zaktualizowana.")
            QMessageBox.information(self, "Sukces", "Dane gry zostały zaktualizowane.")

            if self.parent_table_widget: # Use the new name
                self.parent_table_widget.load_data() # Wywołanie load_data w rodzicu (TabelaGier)
                # If TabelaGier is part of a QStackedWidget, you don't call .show() on it.
                # The parent (e.g., TabelaGier) is already displayed via stacked_widget.
                # You might want to switch back to the parent in stacked_widget if this form was opened as a separate stacked page.
                # Example (if this form is in stacked_widget and parent is also there):
                # self.parent_table_widget.stacked_widget.setCurrentWidget(self.parent_table_widget)
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", f"Nieprawidłowe dane w formularzu: {e}. Wyniki muszą być liczbami całkowitymi.")
        except Exception as e: # Catch other potential database errors
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas aktualizacji gry w bazie danych: {e}")
            self.conn.rollback() # Rollback on database error