import sqlite3

class Zawodnik:
    # Add 'conn' parameter to the constructor to store the main connection
    def __init__(self, firstname=None, lastname=None, points=0, kolejnosc=0, conn=None): # <--- ADDED conn
        self.firstname = firstname
        self.lastname = lastname
        self.points = points
        self.kolejnosc = kolejnosc
        self.conn = conn # <--- STORE THE CONNECTION

    def zapisz(self):
        if not self.conn: # <--- ENSURE CONNECTION IS PROVIDED
            raise ValueError("Database connection (conn) must be provided to Zawodnik instance for saving.")

        cursor = self.conn.cursor() # <--- USE THE PASSED CONNECTION

        # You already have CREATE TABLE in MainWindow.stworz_baze_danych().
        # It's generally not good practice to create tables every time you save.
        # This block below should be removed or commented out for efficiency.
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS zawodnicy (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         firstname TEXT,
        #         lastname TEXT,
        #         points INTEGER,
        #         kolejnosc INT DEFAULT 0
        #     )
        # ''')

        if self.firstname and self.lastname:
            cursor.execute('''
                INSERT INTO zawodnicy (firstname, lastname, points, kolejnosc)
                VALUES (?, ?, ?, ?)
            ''', (self.firstname, self.lastname, self.points, self.kolejnosc))
            print("Zawodnik zapisany.")
        else:
            print("Brak danych zawodnika do zapisania.")
        self.conn.commit() # <--- USE THE PASSED CONNECTION
        # Do NOT close the connection here. The main application closes it.
        # conn.close() # <--- REMOVE THIS LINE


    @classmethod
    # Add 'conn' parameter to class methods that perform DB operations
    def aktualizuj(cls, id, conn, firstname=None, lastname=None, points=None, kolejnosc=None): # <--- ADDED conn
        if not conn:
            raise ValueError("Database connection (conn) must be provided for aktualizuj method.")
        cursor = conn.cursor() # <--- USE THE PASSED CONNECTION

        update_fields = []
        update_values = []

        if firstname:
            update_fields.append("firstname = ?")
            update_values.append(firstname)
        if lastname:
            update_fields.append("lastname = ?")
            update_values.append(lastname)
        if points is not None: # Use 'is not None' because points can be 0 (falsey)
            update_fields.append("points = ?")
            update_values.append(points)
        if kolejnosc is not None:
            update_fields.append("kolejnosc = ?")
            update_values.append(kolejnosc)

        if update_fields:
            update_query = f"UPDATE zawodnicy SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit() # <--- USE THE PASSED CONNECTION
        else:
            print("Brak danych do aktualizacji.")

        # Do NOT close the connection here. The main application closes it.
        # conn.close() # <--- REMOVE THIS LINE


    @classmethod
    # This method also needs to receive the connection to pass to the Zawodnik instance
    def dodaj(cls, firstname, lastname, points, kolejnosc=0, conn=None): # <--- ADDED conn
        if not conn:
            raise ValueError("Database connection (conn) must be provided for dodaj method.")
        zawodnik = cls(firstname, lastname, points, kolejnosc, conn=conn) # <--- PASS THE CONNECTION
        zawodnik.zapisz()

# Przykład użycia (Example usage)
# --- REMOVE OR COMMENT OUT ALL EXAMPLE USAGE CODE AT THE END OF THE FILE ---
# Zawodnik.dodaj("Jan", "Kowalski", 100)
# Zawodnik.aktualizuj(1, points=120)