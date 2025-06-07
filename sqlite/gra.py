import sqlite3

class Gra:
    def __init__(self, data, turniej_id, stol, runda_id, 
                 zawodnik_1=None, zawodnik_2=None, zawodnik_3=None, zawodnik_4=None,
                 wynik_1=None, wynik_2=None, wynik_3=None, wynik_4=None):

        self.data = data
        self.turniej_id = turniej_id
        self.stol = stol
        self.runda_id = runda_id
        self.zawodnik_1 = zawodnik_1
        self.zawodnik_2 = zawodnik_2
        self.zawodnik_3 = zawodnik_3
        self.zawodnik_4 = zawodnik_4
        self.wynik_1 = wynik_1
        self.wynik_2 = wynik_2
        self.wynik_3 = wynik_3
        self.wynik_4 = wynik_4


    def zapisz(self):
        conn = sqlite3.connect('./sqlite/my.db')  # Zmień nazwę bazy danych
        cursor = conn.cursor()

        # Tworzenie tabeli, jeśli nie istnieje (już to masz w kodzie)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gra (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                data DATE NOT NULL, 
                turniej_id INT NOT NULL,
                stol INT NOT NULL,
                runda_id INT NOT NULL,
                zawodnik_1 INT,
                zawodnik_2 INT,
                zawodnik_3 INT,
                zawodnik_4 INT,
                wynik_1 INT,
                wynik_2 INT,
                wynik_3 INT,
                wynik_4 INT
            );
        ''')

        cursor.execute('''
            INSERT INTO gra (data, turniej_id, stol, runda_id, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.data, self.turniej_id, self.stol, self.runda_id, self.zawodnik_1, self.zawodnik_2, self.zawodnik_3, self.zawodnik_4, self.wynik_1, self.wynik_2, self.wynik_3, self.wynik_4))

        conn.commit()
        conn.close()

    @classmethod
    def aktualizuj(cls, id, **kwargs):
        conn = sqlite3.connect('./sqlite/my.db')  # Zmień nazwę bazy danych
        cursor = conn.cursor()

        update_fields = []
        update_values = []

        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)

        if update_fields:
            update_query = f"UPDATE gra SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit()
        else:
            print("Brak danych do aktualizacji.")

        conn.close()

# Przykład użycia
gra1 = Gra(data="2024-01-20", turniej_id=1, stol=1, runda_id=1, zawodnik_1=1, zawodnik_2=2, wynik_1=10, wynik_2=5)
gra1.zapisz()

Gra.aktualizuj(1, wynik_1=12, wynik_2=3)