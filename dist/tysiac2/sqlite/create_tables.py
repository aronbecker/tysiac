import sqlite3


sql_statements = [ 
    """CREATE TABLE IF NOT EXISTS turniej (
            id INTEGER PRIMARY KEY, 
            name text NOT NULL, 
            begin_date DATE, 
            tables_number INT,
            rounds_number INT
        );""",

    """CREATE TABLE IF NOT EXISTS zawodnik (
            id INTEGER PRIMARY KEY, 
            firstname text NOT NULL, 
            lastname text NOT NULL,
            points INT
        );""",

    """CREATE TABLE IF NOT EXISTS zawodnik_turnieju (
            id INTEGER PRIMARY KEY, 
            turniej_id INT NOT NULL, 
            zawodnik_id INT NOT NULL,
            FOREIGN KEY (turniej_id) REFERENCES turniej (id),
            FOREIGN KEY (zawodnik_id) REFERENCES zawodnik (id)
        );""",

    """CREATE TABLE IF NOT EXISTS runda (
            id INTEGER PRIMARY KEY, 
            name text,
            priority INT,
            turniej_id INT NOT NULL,
            FOREIGN KEY (turniej_id) REFERENCES turniej (id)
        );""",

    """CREATE TABLE IF NOT EXISTS gra (
            id INTEGER PRIMARY KEY, 
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
        );"""
]

# create a database connection
try:
    with sqlite3.connect('my.db') as conn:
        # create a cursor
        cursor = conn.cursor()

        # execute statements
        for statement in sql_statements:
            cursor.execute(statement)

        # commit the changes
        conn.commit()

        print("Tables created successfully.")
except sqlite3.OperationalError as e:
    print("Failed to create tables:", e)