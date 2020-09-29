# Data from https://gist.github.com/jaidevd/23aef12e9bf56c618c41
import sqlite3
import pandas as pd
import os

lib_name = "inHouse.db"
withdrawn_name = "withdrawals.db"


def initialize_lib_db():
    lib_db = sqlite3.connect(lib_name)
    curs = lib_db.cursor()
    # Init
    # curs.execute(
    #     """
    # CREATE TABLE inHouse (
    #     Title text,
    #     Author text,
    #     Genre text,
    #     SubGenre text,
    #     Pages integer,
    #     Publisher text)
    # """
    # )
    lib_db.commit()
    s = curs.fetchall()
    if len(s) != 0:
        curs.execute("DELETE * FROM inHouse")
    df = pd.read_csv("books.csv")
    df = df.rename(columns={"Height": "Pages"})
    for i in df.index:
        curs.execute(
            """INSERT INTO inHouse VALUES (
        :Title,
        :Author,
        :Genre,
        :SubGenre,
        :Pages,
        :Publisher)""",
            df.iloc[i].to_dict(),
        )
    lib_db.commit()
    # lib_db.close()
    return lib_db, curs


def initialize_withdrawals():
    with_db = sqlite3.connect(withdrawn_name)
    wcurs = with_db.cursor()
    wcurs.execute("""SELECT * FROM withdrawals""")
    s = wcurs.fetchall()
    if len(s) != 0:
        wcurs.execute("""DELETE FROM withdrawals""")
    with_db.commit()
    return with_db, wcurs


lib_db, curs = initialize_lib_db()
with_db, wcurs = initialize_withdrawals()


def add_book(title, author, genre, subgenre, pages, publisher):
    info = {
        "Title": title,
        "Author": author,
        "Genre": genre,
        "SubGenre": subgenre,
        "Pages": pages,
        "Publisher": publisher,
    }
    with lib_db:
        curs.execute(
            """INSERT INTO inHouse VALUES (
            :Title,
            :Author,
            :Genre,
            :SubGenre,
            :Pages,
            :Publisher)""",
            info,
        )


def withdraw_book(title, return_date):
    # global with_db, wcurs
    with lib_db:
        curs.execute(
            """
            SELECT * FROM inHouse WHERE Title = :title
            """,
            {"title": title},
        )
        book_info = curs.fetchone()
    with with_db:
        # if len(wcurs.fetchone()) != 1:
        try:
            wcurs.execute(
            """
            CREATE TABLE withdrawals (
                Title text,
                Author text,
                Genre text,
                SubGenre text,
                Pages integer,
                Publisher text,
                ReturnDate text
                )
            """
            )
        except:
            pass
        wcurs.execute(
            """INSERT INTO withdrawals VALUES (?, ?, ?, ?, ?, ?, ?)""",(*book_info, return_date))
        with_db.commit()
        wcurs.execute(
            """SELECT * FROM withdrawals"""
        )
        s = wcurs.fetchall()
        print(s)
        # with_db.commit()
        return wcurs, with_db


# wcurs, with_db = withdraw_book('Fundamentals of Wavelets', '12/12/12')

# print(curs.fetchall())
# print('\n', wcurs.fetchall())


# add_book('yaba', 'dC', 'Fictiona', 'diction', 223, 'wainscott')



# print(curs.fetchall())

def main_menu():
    print(
        "1) Browse Books\n",
        "2) Add a Book\n",
        "3) Withdraw a Book\n",
        "4) Return all Withdrawn\n",
        "5) Exit\n",
        )
    pick = input('Enter the number of the action you would like to take: ')
    if pick not in [1,2,3,4,5]:
        print("Selection Not Valid, please pick again!")
        main_menu()
    actions = {
        "1": display_books,
        "2": add_book,
        "3": withdraw_book,
        "4": reset_withdrawn_db,
        "5": lambda: print("\nGoodbye!"),
    }
    pick = str(pick).strip()
    actions[pick]()


main_menu()


def lib_program():
    print(
            "Welcome to the Library Management System!\nPlease choose from the following:\n",
    )
    main_menu()



