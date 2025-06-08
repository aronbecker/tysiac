import sqlite3

class Gra:
    # Add 'conn' parameter to the constructor
    def __init__(self, data, turniej_id, stol, runda_id,
                 zawodnik_1=None, zawodnik_2=None, zawodnik_3=None, zawodnik_4=None,
                 wynik_1=None, wynik_2=None, wynik_3=None, wynik_4=None, conn=None): # <--- ADDED conn
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
        self.conn = conn # <--- STORE THE CONNECTION

    def zapisz(self):
        if not self.conn: # <--- ENSURE CONNECTION IS PROVIDED
            raise ValueError("Database connection (conn) must be provided to Gra instance for saving.")

        cursor = self.conn.cursor() # <--- USE THE PASSED CONNECTION

        # You already have CREATE TABLE in MainWindow.stworz_baze_danych()
        # It's generally not good practice to create tables every time you save.
        # This block below should be removed or commented out.
        # It won't cause the 'unable to open database file' error but is inefficient.
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS gra (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         data DATE NOT NULL,
        #         turniej_id INT NOT NULL,
        #         stol INT NOT NULL,
        #         runda_id INT NOT NULL,
        #         zawodnik_1 INT,
        #         zawodnik_2 INT,
        #         zawodnik_3 INT,
        #         zawodnik_4 INT,
        #         wynik_1 INT,
        #         wynik_2 INT,
        #         wynik_3 INT,
        #         wynik_4 INT
        #     );
        # ''')

        cursor.execute('''
            INSERT INTO gra (data, turniej_id, stol, runda_id, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.data, self.turniej_id, self.stol, self.runda_id, self.zawodnik_1, self.zawodnik_2, self.zawodnik_3, self.zawodnik_4, self.wynik_1, self.wynik_2, self.wynik_3, self.wynik_4))

        self.conn.commit() # <--- USE THE PASSED CONNECTION
        # Do NOT close the connection here. The main application closes it.
        # conn.close() # <--- REMOVE THIS LINE


    @classmethod
    def aktualizuj(cls, id, conn, **kwargs): # <--- ADD conn parameter
        if not conn:
            raise ValueError("Database connection (conn) must be provided for aktualizuj method.")
        cursor = conn.cursor() # <--- USE THE PASSED CONNECTION

        update_fields = []
        update_values = []

        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)

        if update_fields:
            update_query = f"UPDATE gra SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit() # <--- USE THE PASSED CONNECTION
        else:
            print("Brak danych do aktualizacji.")
