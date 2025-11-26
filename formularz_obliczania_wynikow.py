import sqlite3
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QComboBox, QLabel)
from PyQt5.QtCore import pyqtSignal
from datetime import date

class FormularzObliczaniaWynikow(QWidget):
    # Sygnał informujący, że wyniki zostały obliczone (używany do odświeżenia tabeli wyników)
    results_calculated = pyqtSignal()

    def __init__(self, conn, bundle_dir):
        super().__init__()
        self.setWindowTitle("Obliczanie Wyników Turnieju")
        self.conn = conn
        self.bundle_dir = bundle_dir
        self.turniej_map = {} # Słownik przechowujący nazwę -> ID turnieju

        self.main_layout = QVBoxLayout(self)

        # --- Formularz ---
        form_layout = QHBoxLayout()
        
        self.turniej_label = QLabel("Wybierz Turniej:")
        self.turniej_combo = QComboBox()
        

        self.oblicz_button = QPushButton("Oblicz i Zapisz Wyniki")
        self.oblicz_button.clicked.connect(self.oblicz_i_zapisz_wyniki)
        self.load_turnaments()
        form_layout.addWidget(self.turniej_label)
        form_layout.addWidget(self.turniej_combo)
        form_layout.addWidget(self.oblicz_button)
        form_layout.addStretch()

        self.main_layout.addLayout(form_layout)
        self.main_layout.addStretch()

    def load_turnaments(self):
        """Pobiera listę turniejów z bazy danych i wypełnia QComboBox."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM turniej ORDER BY begin_date DESC")
        turnieje = cursor.fetchall()
        
        self.turniej_map = {}
        self.turniej_combo.clear()
        
        if not turnieje:
            self.turniej_combo.addItem("Brak dostępnych turniejów")
            self.oblicz_button.setEnabled(False)
            return

        for id, name in turnieje:
            self.turniej_map[name] = id
            self.turniej_combo.addItem(name)
        
        self.oblicz_button.setEnabled(True)

    def oblicz_i_zapisz_wyniki(self):
        """Pobiera ID turnieju, oblicza punkty i zapisuje je do tabeli 'wyniki'."""
        selected_name = self.turniej_combo.currentText()
        turniej_id = self.turniej_map.get(selected_name)

        if turniej_id is None:
            QMessageBox.warning(self, "Błąd", "Wybierz poprawny turniej.")
            return

        try:
            cursor = self.conn.cursor()
            
            # 1. Pobierz dane o turnieju (data, którą wstawimy do tabeli wyniki)
            cursor.execute("SELECT begin_date FROM turniej WHERE id = ?", (turniej_id,))
            turniej_date = cursor.fetchone()[0]
            
            # 2. Pobierz WSZYSTKIE gry dla tego turnieju
            # Potrzebujemy ID zawodników, żeby wiedzieć, komu przypisać punkty
            cursor.execute("""
                SELECT
                    zawodnik_1, wynik_1,
                    zawodnik_2, wynik_2,
                    zawodnik_3, wynik_3,
                    zawodnik_4, wynik_4
                FROM gra
                WHERE turniej_id = ?
            """, (turniej_id,))
            wszystkie_gry_w_turnieju = cursor.fetchall()

            # 3. Zbuduj mapę ID zawodników do obliczenia punktów
            # Najpierw zbierz wszystkie unikalne ID zawodników z tych gier
            zawodnicy_ids = set()
            for gra in wszystkie_gry_w_turnieju:
                for i in range(0, 8, 2):
                    if gra[i] is not None:
                        zawodnicy_ids.add(gra[i])
            
            # 4. Pobierz szczegóły zawodników (ID, Imię, Nazwisko)
            # W ten sposób unikamy wielokrotnego zapytania do DB
            zawodnik_details = {} # {id: (firstname, lastname)}
            if zawodnicy_ids:
                # Zamiana set na krotkę, aby użyć w zapytaniu SQL
                placeholders = ','.join(['?'] * len(zawodnicy_ids))
                cursor.execute(f"SELECT id, firstname, lastname FROM zawodnicy WHERE id IN ({placeholders})", tuple(zawodnicy_ids))
                for zid, fname, lname in cursor.fetchall():
                    zawodnik_details[zid] = (fname, lname)
            
            # 5. Oblicz punkty (logika podobna do oryginalnej)
            calculated_points = {zid: 0 for zid in zawodnicy_ids}
            
            for gra in wszystkie_gry_w_turnieju:
                # gra: (z1, w1, z2, w2, z3, w3, z4, w4)
                players_in_game = {
                    gra[0]: (gra[1] if gra[1] is not None else 0),
                    gra[2]: (gra[3] if gra[3] is not None else 0),
                    gra[4]: (gra[5] if gra[5] is not None else 0),
                    gra[6]: (gra[7] if gra[7] is not None else 0)
                }
                
                for p_id, p_score in players_in_game.items():
                    if p_id in calculated_points:
                        calculated_points[p_id] += p_score

            # 6. Usuń stare wyniki dla tego turnieju z tabeli wyniki
            cursor.execute("DELETE FROM wyniki WHERE turnament = ?", (turniej_id,))
            
            # 7. Przygotuj dane do wstawienia do tabeli 'wyniki'
            results_to_insert = []
            for zid, points_sum in calculated_points.items():
                if zid in zawodnik_details:
                    fname, lname = zawodnik_details[zid]
                    # Format: (firstname, lastname, punkty, turnament, tdate)
                    results_to_insert.append((fname, lname, int(points_sum), turniej_id, turniej_date)) 

            # 8. Wstaw nowe wyniki w operacji wsadowej
            cursor.executemany("""
                INSERT INTO wyniki (firstname, lastname, punkty, turnament, tdate) 
                VALUES (?, ?, ?, ?, ?)
            """, results_to_insert)
            
            self.conn.commit()
            
            QMessageBox.information(self, "Sukces", 
                                    f"Wyniki dla turnieju '{selected_name}' zostały obliczone i zapisane w tabeli 'wyniki'.")
            
            # Emituj sygnał, aby poinformować główne okno o konieczności odświeżenia
            self.results_calculated.emit()

        except Exception as e:
            self.conn.rollback() 
            QMessageBox.critical(self, "Błąd", f"Nie udało się obliczyć i zapisać wyników: {e}")