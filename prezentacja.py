import os # <--- IMPORT OS to join paths
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer # Not used, but keep if you plan to use it later
from PyQt5.QtGui import QFont

class Prezentacja(QWidget):
    # Add bundle_dir to constructor
    def __init__(self, conn, bundle_dir): # <--- ADD bundle_dir parameter here
        super().__init__()
        self.setWindowTitle("Prezentacja")

        self.conn = conn
        self.bundle_dir = bundle_dir # <--- STORE bundle_dir for later use

        # Load the CSS stylesheet using the determined path
        # Construct the full path to style.css using bundle_dir
        style_sheet_path = os.path.join(self.bundle_dir, "style.css") # <--- CORRECT PATH HERE
        try:
            with open(style_sheet_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Error in Prezentacja: style.css not found at {style_sheet_path}. Prezentacja will run without specific stylesheet.")
        except Exception as e:
            print(f"Error loading stylesheet in Prezentacja: {e}")

        self.layout = QVBoxLayout()
        self.label = QLabel()
        font = QFont()
        font.setPointSize(48)
        self.label.setFont(font)

        # Buttons (poprzedni, nastepny)
        button_layout = QHBoxLayout() # Create a separate layout for buttons
        self.poprzedni_button = QPushButton("Poprzedni")
        self.poprzedni_button.clicked.connect(self.pokaz_poprzedniego_zawodnika)
        button_layout.addWidget(self.poprzedni_button)

        self.nastepny_button = QPushButton("Następny")
        self.nastepny_button.clicked.connect(self.pokaz_nastepnego_zawodnika)
        button_layout.addWidget(self.nastepny_button)

        self.layout.addLayout(button_layout) # Add button layout first

        # Central label with stretches for centering
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.label)
        h_layout.addStretch(1)
        self.layout.addLayout(h_layout)

        # Add vertical stretches to center content
        self.layout.addStretch(1)
        # self.layout.addStretch(1) # Duplicate, remove one if you only want 1 stretch at bottom

        self.setLayout(self.layout)

        self.aktualny_indeks = 0

    def pokaz_prezentacje(self):
        self.aktualny_indeks = 0
        self.pokaz_nastepnego_zawodnika()
        # self.timer.start(3000)

    def pokaz_nastepnego_zawodnika(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT firstname, lastname, points FROM zawodnicy ORDER BY points ASC")
        zawodnicy = cursor.fetchall()

        if self.aktualny_indeks < len(zawodnicy):
            zawodnik = zawodnicy[self.aktualny_indeks]
            miejsce = self.aktualny_indeks + 1

            if miejsce > len(zawodnicy) - 5:
                self.label.setText(f"{len(zawodnicy) - miejsce + 1}. {zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")
            else:
                self.label.setText(f"{zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")

            self.aktualny_indeks += 1
        else:
            self.label.setText("Dziękujemy !!!")

    def pokaz_poprzedniego_zawodnika(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT firstname, lastname, points FROM zawodnicy ORDER BY points ASC")
        zawodnicy = cursor.fetchall()

        self.aktualny_indeks -= 1

        if self.aktualny_indeks < 0:
            self.aktualny_indeks = 0

        if 0 <= self.aktualny_indeks < len(zawodnicy):
            zawodnik = zawodnicy[self.aktualny_indeks]
            miejsce = self.aktualny_indeks + 1

            if miejsce > len(zawodnicy) - 5:
                self.label.setText(f"{len(zawodnicy) - miejsce + 1}. {zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")
            else:
                self.label.setText(f"{zawodnik[0]} {zawodnik[1]} - {zawodnik[2]} punktów")
        else:
            self.label.setText("Dziękujemy !!!")