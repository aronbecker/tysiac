import sqlite3

class Runda:
    # Dodajemy 'conn' do konstruktora
    def __init__(self, name, priority, turniej_id, conn=None): # <--- DODANO conn
        self.name = name
        self.priority = priority
        self.turniej_id = turniej_id
        self.conn = conn # <--- PRZECHOWUJEMY OBIEKT POŁĄCZENIA

    def zapisz(self):
        if not self.conn: # <--- Sprawdzamy, czy połączenie zostało przekazane
            raise ValueError("Database connection (conn) must be provided to Runda instance for saving.")

        cursor = self.conn.cursor() # <--- UŻYWAMY PRZEKAZANEGO POŁĄCZENIA

        # Tworzenie tabeli, jeśli nie istnieje - ta logika powinna być GŁÓWNIE w MainWindow.stworz_baze_danych()
        # Pozostawienie jej tutaj jako "awaryjne" jest ok, ale lepiej ją tam usunąć.
        # Tak czy inaczej, używa self.conn.cursor(), więc jest ok.
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

        self.conn.commit() # <--- UŻYWAMY PRZEKAZANEGO POŁĄCZENIA
        # conn.close() # <--- WAŻNE: USUŃ TĘ LINIĘ! Połączenie zarządza MainWindow.

    @classmethod
    # Dodajemy 'conn' jako parametr dla metod klasowych
    def aktualizuj(cls, id, conn, **kwargs): # <--- DODANO conn
        if not conn:
            raise ValueError("Database connection (conn) must be provided for aktualizuj method.")
        cursor = conn.cursor() # <--- UŻYWAMY PRZEKAZANEGO POŁĄCZENIA

        update_fields = []
        update_values = []

        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)

        if update_fields:
            update_query = f"UPDATE runda SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit() # <--- UŻYWAMY PRZEKAZANEGO POŁĄCZENIA
        else:
            print("Brak danych do aktualizacji.")

        # conn.close() # <--- WAŻNE: USUŃ TĘ LINIĘ!

    @classmethod
    # Dodajemy 'conn' jako parametr dla metod klasowych
    def znajdz_runde(cls, id, conn): # <--- DODANO conn
        if not conn:
            raise ValueError("Database connection (conn) must be provided for znajdz_runde method.")
        cursor = conn.cursor() # <--- UŻYWAMY PRZEKAZANEGO POŁĄCZENIA

        cursor.execute("SELECT * FROM runda WHERE id = ?", (id,))
        data = cursor.fetchone()
        # conn.close() # <--- WAŻNE: USUŃ TĘ LINIĘ!

        if data:
            return data
        else:
            return None

# Przykład użycia
# --- WAŻNE: USUŃ LUB ZAKOMENTUJ CAŁY PONIŻSZY BLOK KODU PRZYKŁADOWEGO ---
# runda1 = Runda(name="Runda 1", priority=1, turniej_id=1)
# runda1.zapisz()
# znajdz_runde = Runda.znajdz_runde(1)
# print(znajdz_runde[1])
# Runda.aktualizuj(1, name="Runda pierwsza")