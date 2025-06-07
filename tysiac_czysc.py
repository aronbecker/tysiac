import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox

class CzyszczenieDanych(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.setWindowTitle("Czyszczenie Danych")
        self.conn = conn

        layout = QVBoxLayout()

        usun_zawodnikow_button = QPushButton("Usuń zawodników")
        usun_zawodnikow_button.clicked.connect(self.usun_zawodnikow)
        layout.addWidget(usun_zawodnikow_button)

        usun_rundy_button = QPushButton("Usuń rundy")
        usun_rundy_button.clicked.connect(self.usun_rundy)
        layout.addWidget(usun_rundy_button)

        usun_gry_button = QPushButton("Usuń gry")
        usun_gry_button.clicked.connect(self.usun_gry)
        layout.addWidget(usun_gry_button)

        usun_turniej_button = QPushButton("Usuń turniej")
        usun_turniej_button.clicked.connect(self.usun_turniej)
        layout.addWidget(usun_turniej_button)

        self.setLayout(layout)

    def usun_zawodnikow(self):
        self.usun_dane_z_tabeli("zawodnicy")

    def usun_rundy(self):
        self.usun_dane_z_tabeli("runda")

    def usun_gry(self):
        self.usun_dane_z_tabeli("gra")

    def usun_turniej(self):
        self.usun_dane_z_tabeli("turniej")

    def usun_dane_z_tabeli(self, nazwa_tabeli):
        odpowiedz = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć wszystkie dane z tabeli '{nazwa_tabeli}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if odpowiedz == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DELETE FROM {nazwa_tabeli}")
                self.conn.commit()
                QMessageBox.information(self, "Sukces", f"Dane z tabeli '{nazwa_tabeli}' zostały usunięte.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć danych: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    conn = sqlite3.connect('twoja_baza.db')  # Zmień nazwę bazy danych
    window = CzyszczenieDanych(conn)
    window.show()
    sys.exit(app.exec_())