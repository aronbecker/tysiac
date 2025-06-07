from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QIcon
from formularz_aktualizacji_gry import FormularzAktualizacjiGry

class TabelaGier(QWidget):
    def __init__(self, conn, runda_id):
        super().__init__()
        self.setWindowTitle(f"Lista Gier dla Rundy {runda_id}")
        # self.setFixedSize(1200, 1200) 
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
                button = QPushButton()
                button.setIcon(QIcon("icons/calculator.png"))
                button.setToolTip("Aktualizuj")
                button.clicked.connect(lambda _, gra_id=gra[0], data_gry=gra: self.aktualizuj_gre(gra_id, data_gry))
                self.table.setCellWidget(i, len(gra), button)  # Dodanie przycisku do ostatniej kolumny 
        self.table.resizeColumnsToContents() 

    def aktualizuj_gre(self, gra_id, data_gry):  # Dodana metoda
        self.formularz_aktualizacji = FormularzAktualizacjiGry(self.conn, gra_id, data_gry, self)
        self.formularz_aktualizacji.show()