# Data from https://gist.github.com/jaidevd/23aef12e9bf56c618c41
import sqlite3
from sqlite3.dbapi2 import ProgrammingError
import pandas as pd


lib_name = "inHouse.db"
withdrawn_name = "withdrawals.db"


def tab_df(df):
    from tabulate import tabulate
    import json
    if type(df) == dict:
        df = json.dumps(df, indent=2)
        print(df)
        return
    tablefmt = 'fancy_grid'
    print(tabulate(df, headers=df.columns, tablefmt=tablefmt))


def clear_output(num_of_lines):
    # region Docstring
    '''
    # Clear Output
    Clears Print Output of the number of lines passed

    #### Returns nothing.   

    ## Parameters:{
    ####    `num_of_lines`: number of lines to clear
    ## }
    '''
    # endregion Docstring
    # if configure.cut_prints == False:
    #     return
    # elif isnotebook:
    #     return
    import sys
    cursor_up = '\x1b[1A'
    erase_line = '\x1b[2K'
    for _ in range(num_of_lines):
        sys.stdout.write(erase_line)
        sys.stdout.write(cursor_up)
        sys.stdout.write(erase_line)

    sys.stdout.write(cursor_up)
    sys.stdout.write('\r')


def initialize_lib_db():
    lib_db = sqlite3.connect(lib_name)
    curs = lib_db.cursor()
    try:
        curs.execute(
            """
        CREATE TABLE inHouse (
            Title text,
            Author text,
            Genre text,
            SubGenre text,
            Pages text,
            Publisher text)
        """
        )
        lib_db.commit()
    except:
        pass
    curs.execute("DELETE FROM inHouse")
    df = pd.read_csv("books.csv").head(15)
    df = df.rename(columns={"Height": "Pages"})
    df['Pages'] = df.Pages.apply(str)
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


def display_books():
    with lib_db:
        curs.execute("""SELECT * FROM inHouse""")
        books = curs.fetchall()
    books = pd.DataFrame(
        data=books,
        columns=["Title", "Author", "Genre", "SubGenre", "Pages", "Publisher"],
    )
    books['Pages'] = books.Pages.apply(lambda x: str(x).encode('utf-8'))
    tab_df(books)
    main_menu(clear=False)


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


def withdraw_book():
    while True:
        title = input("Please Select the title of the book to withdraw")
        with lib_db:
            curs.execute(
                """
                SELECT * FROM inHouse WHERE Title = :title
                """,
                {"title": title},
            )
            book_info = curs.fetchone()
            if len(book_info) == 0:
                print("Book title did not match, please select again")
            else:
                break

    with with_db:
        wcurs.execute(
            "SELECT * FROM withdrawals WHERE Title = :title", {'title': title})

        if len(wcurs.fetchall()) != 0:
            date = list(wcurs.fetchone())[-1]
            print(
                f"It appears that this book is currently checked out and is due back at {date}",
                "\nWould you like to select another book or return to main menu?\n",
                "1) Select another book\n",
                "2) Return to Main Menu\n",
            )
            action = input(
                "Please select the number corresponding to the action")
            if action == 1:
                withdraw_book()
            main_menu()
        else:
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
                """INSERT INTO withdrawals VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (*book_info, return_date),
            )
            with_db.commit()
            wcurs.execute("""SELECT * FROM withdrawals""")
            s = wcurs.fetchall()
            print(s)
            # with_db.commit()
            return wcurs, with_db


def reset_withdrawn_db():
    with with_db:
        wcurs.execute("DELETE FROM withdrawals")
        wcurs.execute("SELECT * FROM withdrawals")
        proof = wcurs.fetchall()
    print(proof)
    main_menu()


def search_for_book():
    clear_output(999)
    print(
        "\nWhat would you like to search by? :\n",
        "1) Title\n",
        "2) Author\n",
        "3) Genre\n",
        "4) SubGenre\n",
        "5) Publisher\n",
    )
    response = input("Please select an option by it's corresponding number")
    search_cats = {
        "1": "Title",
        "2": "Author",
        "3": "Genre",
        "4": "SubGenre",
        "5": "Publisher"
    }
    cat = search_cats[response]
    term = input(f'Please input the {cat} name to search: ')
    curs.execute("SELECT * FROM inHouse WHERE Title = ?", (term, ))
    responses = curs.fetchall()
    if len(responses) == 0:
        print(
            "No results were found. Would you like to search again?\n"
        )
        ans = input('Y/n?')
        if ans.upper() == 'Y':
            search_for_book()
        return main_menu()
    else:
        columns = ["Title", "Author", "Genre",
                   "SubGenre", "Pages", "Publisher"]
        df = pd.DataFrame(responses, columns=columns)
        df = df.drop(columns=["Pages"], axis=1)
        # df.Pages.apply(lambda x: str(x))
        tab_df(df)
        print(
            "\n1) Check to see if book is available\n",
            "2) Search another book\n",
            "3) Return to Main Menu\n",
        )
        response = input("Please select an option by it's corresponding number")
        actions = {
            "1": lambda: is_withdrawn(title),
            "2": search_for_book,
            "3": main_menu,
        }


def main_menu(clear=True):
    if clear:
        clear_output(999)
    print(
        "1) Browse Books\n",
        "2) Search Books\n",
        "3) Add a Book\n",
        "4) Withdraw a Book\n",
        "5) Return all Withdrawn\n",
        "6) Exit\n",
    )
    pick = input("Enter the number of the action you would like to take: ")
    actions = {
        "1": display_books,
        "2": search_for_book,
        "3": add_book,
        "4": withdraw_book,
        "5": reset_withdrawn_db,
        "6": lambda: print("\nGoodbye!"),
    }
    if pick not in actions.keys():
        print("Selection Not Valid, please pick again!")
        main_menu()
    pick = str(pick).strip()
    actions[pick]()


def lib_program():
    print(
        "Welcome to the Library Management System!\nPlease choose from the following:\n",
    )
    main_menu(clear=False)


if __name__ == "__main__":
    lib_db, curs = initialize_lib_db()
    with_db, wcurs = initialize_withdrawals()
    lib_program()
