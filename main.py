# Data from https://gist.github.com/jaidevd/23aef12e9bf56c618c41
import sqlite3
import pandas as pd


lib_name = "inHouse.db"
withdrawn_name = "withdrawals.db"


def tab_df(df):
    """Prints out a df or dict in a pretty way"""
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
    Clears Console Output of the number of lines passed

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
    """Makes sure lib_db exists and is populated with data"""
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
    """Ensures with_db exists"""
    with_db = sqlite3.connect(withdrawn_name)
    wcurs = with_db.cursor()
    wcurs.execute("""SELECT * FROM withdrawals""")
    s = wcurs.fetchall()
    if len(s) != 0:
        wcurs.execute("""DELETE FROM withdrawals""")
    with_db.commit()
    return with_db, wcurs


def display_books():
    """Gathers all entries for db and prints them out to console"""
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


def add_book():
    """Adds a book entry to the lib_db through the main menu ui of the program"""
    clear_output(999)
    print("Adding a book")
    title = input("Please type Title of Book: ")
    author = input("Please type Author's Name: ")
    genre = input("Please type Genre: ")
    subgenre = input("Please type Subgenre: ")
    pages = input("Please type number of pages: ")
    publisher = input("Please type publisher name: ")
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
    print('\nBook Added!\n')
    main_menu(clear=False)


def withdraw_book():
    """Allows user to withdraw a book and set a date for return """
    while True:
        title = input("Please Select the title of the book to withdraw: ")
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
        data = wcurs.fetchall()

        if len(data) != 0:
            date = data[-1][-1]
            # print()
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
            return_date = input("Please enter the date of return in mm/dd/yy format: ")
            wcurs.execute(
                """INSERT INTO withdrawals VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (*book_info, return_date),
            )
            with_db.commit()
            wcurs.execute("""SELECT * FROM withdrawals""")
            s = wcurs.fetchall()

            print(
                "The following book has been withdrawn:\n",
                s,
                '\n'
                )
            # with_db.commit()
            main_menu(clear=False)
            return


def is_withdrawn(title):
    "Endpoint for App that will declare whether passed title is inside the with_db"
    with with_db:
        wcurs.execute("SELECT * FROM withdrawals WHERE Title = ?", (title,))
        data = wcurs.fetchall()
        if (len(data)) != 0:
            date = data[0][-1]
            print(
                f"{title} is currently checked out and is due back on {date}\n"
            )
        else:
            print(
                f"{title} is available for withdrawal\n"
            )
        main_menu(clear=False)


def reset_withdrawn_db():
    """DELETE all entries of with_db"""
    with with_db:
        wcurs.execute("DELETE FROM withdrawals")
        wcurs.execute("SELECT * FROM withdrawals")
        proof = wcurs.fetchall()
    print(
        "\nAll withdrawals have been reset.\n"
    )
    main_menu(clear=False)


def search_for_book():
    '''Allows user to search through book collection'''
    clear_output(999)
    print(
        "\nWhat would you like to search by? :\n",
        "1) Title\n",
        "2) Author\n",
        "3) Genre\n",
        "4) SubGenre\n",
        "5) Publisher\n",
    )
    response = input("Please select an option by it's corresponding number: ")
    search_cats = {
        "1": "Title",
        "2": "Author",
        "3": "Genre",
        "4": "SubGenre",
        "5": "Publisher"
    }
    cat = search_cats[response]
    term = input(f'Please input the {cat} name to search: ')
    curs.execute(f"SELECT * FROM inHouse WHERE {cat} = ?", (term,))
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
        # df = df.drop(columns=["Pages"], axis=1)
        tab_df(df)
        if len(df) != 1:
            print(
                "\nLooks like several entries came back. Please enter the number of the book you were searching for:\n",
            )
            ans = input("You can also enter -1 to go back to Main Menu: ")
            if int(ans) == -1 or int(ans) not in df.index:
                main_menu()
                return
            df = df[df.index == int(ans)]
            tab_df(df)
        print(
            "\n1) Check to see if book is available\n",
            "2) Search another book\n",
            "3) Return to Main Menu\n",
        )
        title = df.Title.tolist()[0]
        response = input(
            "Please select an option by it's corresponding number: ")
        actions = {
            "1": lambda: is_withdrawn(title),
            "2": search_for_book,
            "3": main_menu,
        }
        actions[response]()


def main_menu(clear=True):
    """User hub of options to choose from with directories to said options"""
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
    """Main Program"""
    print(
        "Welcome to the Library Management System!\nPlease choose from the following:\n",
    )
    main_menu(clear=False)


if __name__ == "__main__":
    lib_db, curs = initialize_lib_db()
    with_db, wcurs = initialize_withdrawals()
    lib_program()
