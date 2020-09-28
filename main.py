# %%
# Data from https://gist.github.com/jaidevd/23aef12e9bf56c618c41
import sqlite3
import pandas as pd

conn = sqlite3.connect("inHouse.db")
curs = conn.cursor()

def initalize_database():
    s = curs.fetchall()
    if len(s) != 0:
        curs.execute("DELETE * FROM inHouse")
    df = pd.read_csv('books.csv')
    df = df.rename(columns={'Height':'Pages'})
    for i in df.index:
        curs.execute('INSERT INTO employees VALUES (:Title, :Author, :Genre, :Pages, )')
        df.iloc[i].to_dict()
 


# %%



c = conn.cursor()

c.execute(
"""
CREATE TABLE employees(
    Title text,  
    Author text,  
    Genre text,  
    Sub_Genre text,  
    Pages integer,  
    Publisher text,  
)
"""
)
conn.commit()
conn.close()



# entries

# %%




def inherit_database():
    pass

def add_book():
    pass

def withdraw_book(title):
    pass




c.execute('INSERT INTO employees VALUES ("Dan", "Corson", 58000)')

# conn.commit()

c.execute("SELECT * FROM employees WHERE last = 'Corson'")

one = c.fetchall()
print(one)

conn.commit()
# Saves Changes to DB

conn.close()