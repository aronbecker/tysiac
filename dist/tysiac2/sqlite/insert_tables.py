import sqlite3
from zawodnik import Zawodnik
from runda import Runda

def add_turniej(conn, turnament):
    # insert table statement
    sql = ''' INSERT INTO turniej(name,begin_date,tables_number,rounds_number)
              VALUES(?,?,?,?) '''
    
    # Create  a cursor
    cur = conn.cursor()

    # execute the INSERT statement
    cur.execute(sql, turnament)

    # commit the changes
    conn.commit()

    # get the id of the last inserted row
    return cur.lastrowid


def add_player(conn, player):
    # insert table statement
    sql = '''INSERT INTO zawodnik(name,firstname,lastname,points)
             VALUES(?,?,?,?,?,?) '''
    
    #     # insert table statement
    # sql2 = '''INSERT INTO zawodnik_turnieju(name,firstname,lastname,points)
    #          VALUES(?,?,?,?,?,?) '''
    # create a cursor
    cur = conn.cursor()

    # execute the INSERT statement
    cur.execute(sql, player)

    # commit the changes
    conn.commit()

    # get the id of the last inserted row
    return cur.lastrowid

def add_round(conn, round):
    # insert table statement
    sql = '''INSERT INTO runda(name,priority,turniej_id)
             VALUES(?,?,?) '''
    # create a cursor
    cur = conn.cursor()

    # execute the INSERT statement
    cur.execute(sql, round)

    # commit the changes
    conn.commit()

    # get the id of the last inserted row
    return cur.lastrowid

def add_game(conn, game):
    # insert table statement
    sql = '''INSERT INTO gra(data,turniej_id,stol, runda_id, zawodnik_1, zawodnik_2, zawodnik_3, zawodnik_4, wynik_1, wynik_2, wynik_3, wynik_4)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
    # create a cursor
    cur = conn.cursor()

    # execute the INSERT statement
    cur.execute(sql, game)

    # commit the changes
    conn.commit()

    # get the id of the last inserted row
    return cur.lastrowid

def main():
    # try:
    #     with sqlite3.connect('my.db') as conn:
    #         # add  a project
    #         project = ('Cool App with SQLite & Python', '2015-01-01', '2015-01-30')
    #         project_id = add_project(conn, project)
    #         print(f'Created a project with the id {project_id}')

    #         # add tasks to the project 
    #         tasks = [
    #             ('Analyze the requirements of the app', 1, 1, project_id, '2015-01-01', '2015-01-02'),
    #             ('Confirm with user about the top requirements', 1, 1, project_id, '2015-01-03', '2015-01-05')
    #         ]

    #         for task in tasks:
    #             task_id = add_task(conn, task)
    #             print(f'Created task with the id {task_id}')


    # except sqlite3.Error as e:
        # print(e)
    Zawodnik1 = Zawodnik("Jan", "Kowalsk2", 100)
    Zawodnik1.zapisz()
    Zawodnik.aktualizuj(2, points=120)

    Runda1 =  Runda(name="Runda 1", priority=1, turniej_id=1)
    Runda1.zapisz()
    print(Runda1.name)
    Runda.aktualizuj(1, name="Runda pierwsza")

if __name__ == '__main__':
    main()