import sqlite3

class Zawodnik:
    def __init__(self, firstname=None, lastname=None, points=0, kolejnosc=0):
        self.firstname = firstname
        self.lastname = lastname
        self.points = points
        self.kolejnosc = kolejnosc

    def zapisz(self):
        conn = sqlite3.connect('my.db')  # Połączenie z bazą danych (lub tworzenie nowej)
        cursor = conn.cursor()

        # Tworzenie tabeli, jeśli nie istnieje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zawodnicy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT,
                lastname TEXT,
                points INTEGER,
                kolejnosc INT DEFAULT 0
            )
        ''')

        if self.firstname and self.lastname:
            cursor.execute('''
                INSERT INTO zawodnicy (firstname, lastname, points, kolejnosc)
                VALUES (?, ?, ?, ?)
            ''', (self.firstname, self.lastname, self.points, self.kolejnosc))
            print("Zawodnik zapisany.")
        else:
            print("Brak danych zawodnika do zapisania.")
        conn.commit()
        conn.close()

    @classmethod
    def aktualizuj(cls, id, firstname=None, lastname=None, points=None, kolejnosc=None):
        conn = sqlite3.connect('./sqlite/my.db')
        cursor = conn.cursor()

        update_fields = []
        update_values = []

        if firstname:
            update_fields.append("firstname = ?")
            update_values.append(firstname)
        if lastname:
            update_fields.append("lastname = ?")
            update_values.append(lastname)
        if points:
            update_fields.append("points = ?")
            update_values.append(points)

        if kolejnosc:
            update_fields.append("kolejnosc = ?")
            update_values.append(kolejnosc)

        if update_fields:
            update_query = f"UPDATE zawodnicy SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit()
        else:
            print("Brak danych do aktualizacji.")

        conn.close()

    @classmethod
    def dodaj(cls, firstname, lastname, points, kolejnosc=0):
        zawodnik = cls(firstname, lastname, points, kolejnosc=0)
        zawodnik.zapisz()

# Przykład użycia
# Zawodnik.dodaj("Jan", "Kowalski", 100)
# Zawodnik.aktualizuj(1, points=120)