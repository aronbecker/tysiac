# formularz_dodawania_rund.py
import os # <--- ADD THIS IMPORT
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
# No need for pyqtSignal here if you're directly calling tabela_rund.load_data()

# You don't import Runda class here, you're directly using cursor.execute, which is fine.
# If you were using:
# from sqlite.runda import Runda
# Then you would need to pass self.conn when creating Runda objects here.

class FormularzDodawaniaRundy(QWidget):
    # If you emit a signal for round_added, define it here (currently directly refreshing tabela_rund)
    # round_added = pyqtSignal() # Uncomment if you switch to signal-based refresh

    # ADD bundle_dir to __init__ signature
    def __init__(self, conn, tabela_rund, turniej_id, bundle_dir): # <--- ADDED bundle_dir here!
        super().__init__()
        self.setWindowTitle("Dodaj Rundę")
        self.conn = conn
        self.turniej_id = turniej_id
        self.tabela_rund = tabela_rund
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir here (for future use if needed)

        self.layout = QVBoxLayout()

        # Pola formularza
        self.form_layout = QFormLayout()
        self.name_label = QLabel("Nazwa:")
        self.name_input = QLineEdit()
        self.priority_label = QLabel("Priorytet:")
        self.priority_input = QLineEdit()
        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.priority_label, self.priority_input)

        # Przycisk "Dodaj"
        self.dodaj_button = QPushButton("Dodaj")
        self.dodaj_button.clicked.connect(self.dodaj_runde)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.dodaj_button)

        self.setLayout(self.layout)

    def dodaj_runde(self):
        try:
            name = self.name_input.text()
            priority_text = self.priority_input.text() # Get as text first

            if not all([name, priority_text]): # Check if fields are filled
                raise ValueError("Nazwa i priorytet muszą być wypełnione.")

            try:
                priority = int(priority_text)
            except ValueError:
                raise ValueError("Priorytet musi być liczbą całkowitą.")

            turniej_id = int(self.turniej_id) # Ensure turniej_id is int

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO runda (name, priority, turniej_id) VALUES (?, ?, ?)", (name, priority, turniej_id))
            self.conn.commit() # This looks correct

            # Odświeżenie tabeli rund
            self.tabela_rund.load_data() # This relies on tabela_rund existing and having load_data()

            QMessageBox.information(self, "Sukces", "Runda została dodana.")
            # If you want to use a signal, emit it here instead of direct load_data()
            # self.round_added.emit()
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))
        except Exception as e: # Catch other potential database errors
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas dodawania rundy do bazy danych: {e}")
            self.conn.rollback() # Rollback on database error