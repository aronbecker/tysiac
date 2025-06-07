import sqlite3

class Turniej:
    def __init__(self, name=None, begin_date=None, tables_number=None, rounds_number=None):
        self.name = name
        self.begin_date = begin_date
        self.tables_number = tables_number
        self.rounds_number = rounds_number

    def zapisz(self):
        conn = sqlite3.connect('my.db')  # Połączenie z bazą danych (lub tworzenie nowej)
        cursor = conn.cursor()

        # Tworzenie tabeli, jeśli nie istnieje
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turniej (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text NOT NULL, 
                begin_date DATE, 
                tables_number INT,
                rounds_number INT
            )
        ''')

        if self.name and self.begin_date and self.tables_number and self.rounds_number:
            cursor.execute('''
                INSERT INTO turniej (name, begin_date, tables_number, rounds_number)
                VALUES (?, ?, ?)
            ''', (self.name, self.begin_date, self.tables_number, self.rounds_number))
        else:
            print("Brak danych turniej do zapisania.")

        conn.commit()
        conn.close()

    @classmethod
    def aktualizuj(cls, id, name=None, begin_date=None, tables_number=None, rounds_number=None):
        conn = sqlite3.connect('my.db')
        cursor = conn.cursor()

        update_fields = []
        update_values = []

        if name:
            update_fields.append("name = ?")
            update_values.append(name)
        if begin_date:
            update_fields.append("begin_date = ?")
            update_values.append(begin_date)
        if tables_number:
            update_fields.append("tables_number = ?")
            update_values.append(tables_number)

        if rounds_number:
            update_fields.append("rounds_number = ?")
            update_values.append(rounds_number)

        if update_fields:
            update_query = f"UPDATE turniej SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(id)
            cursor.execute(update_query, update_values)
            conn.commit()
        else:
            print("Brak danych do aktualizacji.")

        conn.close()

    @classmethod
    def dodaj(cls, name, begin_date, tables_number, rounds_number):
        turniej = cls(name, begin_date, tables_number, rounds_number)
        turniej.zapisz()