# Data from https://gist.github.com/jaidevd/23aef12e9bf56c618c41
import sqlite3
import pandas as pd
import os

lib_name = "inHouse.db"
withdrawn_name = "withdrawals.db"


def initalize_database():
    lib_db = sqlite3.connect(lib_name)
    curs = lib_db.cursor()
    if not os.path.exists(lib_name):
        curs.execute(
            """
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
    lib_db.close()
    return lib_db, curs


def initialize_withdrawals():
    with_db = sqlite3.connect(withdrawn_name)
    wcurs = with_db.cursor()
    if not os.path.exists(withdrawn_name):
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
    s = wcurs.fetchall()
    if len(s) != 0:
        wcurs.execute("""DELETE * FROM withdrawals""")
    with_db.commit()
    return with_db, wcurs


lib_db, curs = initalize_database()
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
    curs.execute(
        """
        SELECT * FROM inHouse WHERE Title = :title
        """,
        {"title": title},
    )
    book_info = curs.fetchone()
    wcurs.execute(
        """INSERT INTO withdrawals VALUES (
                    :Title,
                    :Author,
                    :Genre,
                    :SubGenre,
                    :Pages,
                    :Publisher,
                    :ReturnDate,
                    )""",
        (*book_info, return_date),
    )
    with_db.commit()
    with_db.close()
    print(book_info)
