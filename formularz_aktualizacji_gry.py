from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)

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