import sqlite3

class Runda:
    def __init__(self, name, priority, turniej_id):
        self.name = name
        self.priority = priority
        self.turniej_id = turniej_id

    def zapisz(self):
        conn = sqlite3.connect('my.db')  # Zmień nazwę bazy danych
        cursor = conn.cursor()

        # Tworzenie tabeli, jeśli nie istnieje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runda (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name text,
                priority INT,
                turniej_id INT NOT NULL,
                FOREIGN KEY (turniej_id) REFERENCES turniej (id)
            );
        ''')

        cursor.execute('''
            INSERT INTO runda (name, priority, turniej_id)
            VALUES (?, ?, ?)
        ''', (self.name, self.priority, self.turniej_id))

        conn.commit()
        conn.close()

    @classmethod
    def aktualizuj(cls, id, **kwargs):
        conn = sqlite3.connect('my.db')  # Zmień nazwę bazy danych
        cursor = conn.cursor()

        update_fields = []
        update_values = []

        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)

        if update_fields:
            update_query = f"UPDATE runda SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit()
        else:
            print("Brak danych do aktualizacji.")

        conn.close()

    @classmethod
    def znajdz_runde(cls, id):
        conn = sqlite3.connect('my.db')  # Zmień nazwę bazy danych
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM runda WHERE id = ?", (id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            # Domyślnie zwracamy tuplę z danymi, ale można też stworzyć słownik lub obiekt Runda
            # return cls(*data[1:]) # Jeśli chcesz zwrócić obiekt Runda (pomijając id)
            return data  # Zwraca tuplę
        else:
            return None  # Zwraca None, jeśli runda nie istnieje

# Przykład użycia
runda1 = Runda(name="Runda 1", priority=1, turniej_id=1)
runda1.zapisz()
znajdz_runde = Runda.znajdz_runde(1)
print(znajdz_runde[1])

Runda.aktualizuj(1, name="Runda pierwsza")