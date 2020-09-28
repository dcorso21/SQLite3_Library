# %%
# Data from https://gist.github.com/jaidevd/23aef12e9bf56c618c41
import sqlite3
import pandas as pd
import os

db_name = "inHouse.db"

def initalize_database():
    lib_db = sqlite3.connect(db_name)
    curs = lib_db.cursor()
    if not os.path.exists(db_name):
        curs.execute("""
        CREATE TABLE inHouse (
            Title text,  
            Author text,  
            Genre text,
            SubGenre text,
            Pages integer,
            Publisher text)
        """
        )
    lib_db.commit()
    s = curs.fetchall()
    if len(s) != 0:
        curs.execute("DELETE * FROM inHouse")
    df = pd.read_csv('books.csv')
    df = df.rename(columns={'Height':'Pages'})
    for i in df.index:
        curs.execute("""INSERT INTO inHouse VALUES (
        :Title,
        :Author,
        :Genre,
        :SubGenre,
        :Pages,
        :Publisher)""",
        df.iloc[i].to_dict())
    lib_db.commit()
    lib_db.close()
    return lib_db, curs

lib_db, curs =  initalize_database()


# %%

def add_book():
    pass

def withdraw_book(title):
    pass




# c.execute('INSERT INTO employees VALUES ("Dan", "Corson", 58000)')

# # conn.commit()

# c.execute("SELECT * FROM employees WHERE last = 'Corson'")

# one = c.fetchall()
# print(one)

# conn.commit()
# # Saves Changes to DB

# conn.close()