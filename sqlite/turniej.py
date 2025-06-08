import sqlite3

class Turniej:
    # Add 'conn' parameter to the constructor
    def __init__(self, name=None, begin_date=None, tables_number=None, rounds_number=None, conn=None): # <--- ADDED conn
        self.name = name
        self.begin_date = begin_date
        self.tables_number = tables_number
        self.rounds_number = rounds_number
        self.conn = conn # <--- STORE THE CONNECTION

    def zapisz(self):
        if not self.conn: # <--- Ensure connection is provided
            raise ValueError("Database connection (conn) must be provided to Turniej instance for saving.")

        cursor = self.conn.cursor() # <--- USE THE PASSED CONNECTION

        # You already have CREATE TABLE in MainWindow.stworz_baze_danych().
        # It's generally not good practice to create tables every time you save.
        # You can keep it as a fallback, but the primary table creation happens centrally.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turniej (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text NOT NULL,
                begin_date DATE,
                tables_number INT,
                rounds_number INT
            )
        ''')

        if self.name and self.begin_date and self.tables_number is not None and self.rounds_number is not None: # Check for None for numbers
            cursor.execute('''
                INSERT INTO turniej (name, begin_date, tables_number, rounds_number)
                VALUES (?, ?, ?, ?) # <--- CORRECTED: 4 placeholders for 4 columns
            ''', (self.name, self.begin_date, self.tables_number, self.rounds_number)) # <--- CORRECTED: 4 values
            print("Turniej zapisany.")
        else:
            print("Brak wszystkich danych turnieju do zapisania.")

        self.conn.commit() # <--- USE THE PASSED CONNECTION
        # conn.close() # <--- IMPORTANT: REMOVE THIS LINE! Connection is managed by MainWindow.

    @classmethod
    # Add 'conn' as a parameter for class methods that perform DB operations
    def aktualizuj(cls, id, conn, name=None, begin_date=None, tables_number=None, rounds_number=None): # <--- ADDED conn
        if not conn:
            raise ValueError("Database connection (conn) must be provided for aktualizuj method.")
        cursor = conn.cursor() # <--- USE THE PASSED CONNECTION

        update_fields = []
        update_values = []

        if name:
            update_fields.append("name = ?")
            update_values.append(name)
        if begin_date:
            update_fields.append("begin_date = ?")
            update_values.append(begin_date)
        if tables_number is not None: # Use 'is not None' as 0 is a valid number
            update_fields.append("tables_number = ?")
            update_values.append(tables_number)
        if rounds_number is not None:
            update_fields.append("rounds_number = ?")
            update_values.append(rounds_number)

        if update_fields:
            update_query = f"UPDATE turniej SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit() # <--- USE THE PASSED CONNECTION
        else:
            print("Brak danych do aktualizacji.")

        # conn.close() # <--- IMPORTANT: REMOVE THIS LINE!

    @classmethod
    # This method also needs to receive the connection
    def dodaj(cls, name, begin_date, tables_number, rounds_number, conn=None): # <--- ADDED conn
        if not conn:
            raise ValueError("Database connection (conn) must be provided for dodaj method.")
        turniej = cls(name, begin_date, tables_number, rounds_number, conn=conn) # <--- PASS THE CONNECTION
        turniej.zapisz()

# Przykład użycia (Example usage)
# --- IMPORTANT: REMOVE OR COMMENT OUT ALL EXAMPLE USAGE CODE AT THE END OF THE FILE ---
# turniej1 = Turniej(name="Turniej Testowy", begin_date="2025-01-01", tables_number=5, rounds_number=3)
# turniej1.zapisz()
# Turniej.aktualizuj(1, name="Turniej Nowy", rounds_number=4)
# Turniej.dodaj("Kolejny Turniej", "2025-02-01", 3, 2)