import sys
import mysql.connector


def print_menu(menu):
    """
    Displays the menu
    :param menu: dict of form {code: [description, query]}
    """
    for item in menu:
        # print item code and description
        print(item + ". " + menu[item][0])


def validate_int(values, col_name, index):
    """
    Returns if values[index] is a valid int or not. If it is, casts to int. If not, prints message for user.
    :param values: list of values of data to be inserted into the table
    :param col_name: name of the column that we're checking the data for
    :param index: index of the data we're checking
    :return: True if values[index] is a valid int, else False
    """
    try:
        values[index] = int(values[index])
    except ValueError:
        print(col_name + " must be an int. ")
        return False
    else:
        return True


def validate_float(values, col_name, index):
    """
    Returns if values[index] is a valid float or not. If it is, casts to float. If not, prints message for user.
    :param values: list of values of data to be inserted into the table
    :param col_name: name of the column that we're checking the data for
    :param index: index of the data we're checking
    :return: True if values[index] is a valid float, else False
    """
    try:
        values[index] = float(values[index])
    except ValueError:
        print(col_name + " must be a float. ")
        return False
    else:
        return True


def validate_date(values, col_name, index):
    """
    Returns if values[index] is a valid date or not. If it is, casts to int. If not, prints message for user.
    :param values: list of values of data to be inserted into the table
    :param col_name: name of the column that we're checking the data for
    :param index: index of the data we're checking
    :return: True if values[index] is a valid date, else False
    """
    # dates must be of length 8 (YYYYMMDD)
    if len(values[index]) != 8:
        valid = False
    else:
        # if string of length 8, need to make sure it's a string
        try:
            values[index] = int(values[index])
        except ValueError:
            valid = False
        else:
            valid = True
    if not valid:
        print(col_name + " must be a valid date (YYYYMMDD format). ")
        return False
    else:
        return True


def insert():
    """
    Allows user to insert a new row into a table
    :return: insertion query to execute on the database
    """
    # get table name
    print("Which table (Hotel, Room, Booking, or Guest) would you like to insert data into?")
    table = input().title()

    # validate table name
    while table not in {"Hotel", "Room", "Booking", "Guest"}:
        print("Sorry, that is not one of the tables in the Hotel Database. "
              "Please enter a valid table name (Hotel, Room, Booking, or Guest). ")
        table = input().title()

    # determine what pieces of data are needed (columns in chosen table)
    if table == "Hotel":
        cols = ["hotelNo", "hotelName", "city"]
    elif table == "Room":
        cols = ["roomNo", "hotelNo", "type", "price"]
    elif table == "Booking":
        cols = ["hotelNo", "guestNo", "dateFrom", "dateTo", "roomNo"]
    else:
        # Guest
        cols = ["guestNo", "guestName", "guestAddress"]

    # prompt user with column names
    prompt = "Please enter values for "
    for i in range(len(cols) - 1):
        prompt += cols[i] + ", "
    prompt += "and " + cols[-1] + ", in order and separated by commas. "
    print(prompt)
    # get data to insert
    values = input().split(",")
    # strip off whitespace
    for i in range(len(values)):
        values[i] = values[i].strip()

    # validate data
    invalid = True
    while invalid:
        # make sure we have the right number of values
        if len(values) != len(cols):
            print("You have not entered the correct number of values. ")
        elif table == "Hotel":
            # hotelNo, the first parameter, must be an int
            invalid = not validate_int(values, "hotelNo", 0)
        elif table == "Room":
            # roomNo and hotelNo, the first two parameters, must be ints
            # price, the fourth parameter, must be a float
            invalid = False in [validate_int(values, "roomNo", 0), validate_int(values, "hotelNo", 1),
                                validate_float(values, "price", 3)]
        elif table == "Booking":
            # hotelNo and guestNo, the first two parameters, must be ints
            # dateFrom and dateTo, the third and fourth parameters, must be datetimes (can pass as ints with 8 digits)
            # roomNo, the fifth parameter, must be an int
            invalid = False in [validate_int(values, "hotelNo", 0), validate_int(values, "guestNo", 1),
                                validate_date(values, "dateFrom", 2), validate_date(values, "dateTo", 3),
                                validate_int(values, "roomNo", 4)]
        else:
            # Guest
            # guestNo, the first parameter, must be an int
            invalid = not validate_int(values, "guestNo", 0)
        if invalid:
            # if the user entered invalid date, prompt them again
            print(prompt)
            # get data to insert
            values = input().split(",")
            # strip off whitespace
            for i in range(len(values)):
                values[i] = values[i].strip()

    # build insertion query
    return "INSERT INTO " + table + " VALUES " + str(tuple(values))


def get_query(menu):
    """
    Gets query from user's selected option
    :param menu: dict of form {code: [description, query]}
    :return: query corresponding to selected menu option
    """
    # get raw input from user
    print("Please enter the menu code corresponding to your desired query. "
          "Enter 'MENU' to view menu options again. ")
    selection = input().upper()

    # validate input
    while selection not in menu:
        # display menu again if requested
        if selection == 'MENU':
            print_menu(menu)
            print("Please enter the menu code corresponding to your desired query: ")
        else:
            print("Sorry, that is not a valid menu code. "
                  "Please enter the menu code corresponding to your desired query. "
                  "Enter 'MENU' to view menu options again. ")
        selection = input().upper()

    if selection == "INSERT":
        # return insertion statement to be executed
        return insert()
    else:
        # return the corresponding query
        return menu[selection][1]


if __name__ == "__main__":

    # configuration parameters for connection to the hotel database
    config = {
        "user": "lilywittle",
        "password": "bte@1234",
        "host": "35.196.173.141",
        "database": "theHotel"
    }

    # connect to the database
    try:
        db_conn = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print(error)
        sys.exit()
    # get cursor
    cursor = db_conn.cursor()

    # menu options
    menu_options = {
        "2A": ["List full details of all hotels.",
               "SELECT * FROM Hotel"],
        "2B": ["List full details of all hotels in London.",
               "SELECT * FROM Hotel WHERE city = 'London'"],
        "2C": ["List the names and addresses of all guests in London, alphabetically ordered by name.",
               "SELECT DISTINCT g.guestName, g.guestAddress FROM Guest g, Hotel h, Booking b "
               "WHERE b.guestNo = g.guestNo AND b.hotelNo = h.hotelNo AND h.city = 'London' "
               "ORDER BY g.guestName ASC"],
        "3A": ["List the average price of a room.",
               "SELECT AVG(price) AS average_price FROM Room"],
        "3B": ["List the price and type of all rooms at the Grosvenor Hotel.",
               "SELECT r.price, r.type FROM Room r, Hotel h "
               "WHERE r.hotelNo = h.hotelNo AND hotelName = 'Grosvenor Hotel'"],
        "3C": ["List the total income from bookings for the Grosvenor Hotel today.",
               "SELECT SUM(r.price) AS income_today FROM Room r, Booking b, Hotel h "
               "WHERE r.roomNo = b.roomNo AND r.hotelNo = h.hotelNo AND hotelName = 'Grosvenor Hotel' "
               "AND b.dateFrom <= NOW() AND b.dateTo >= NOW()"],
        "3D": ["List the number of rooms in each hotel in London.",
               "SELECT h.hotelNo, COUNT(r.roomNo) AS number_of_rooms FROM Room r, Hotel h "
               "WHERE r.hotelNo = h.hotelNo and city = 'London' "
               "GROUP BY h.hotelNo"],
        "3E": ["List the most commonly booked room type for each hotel in London.",
               "SELECT h.hotelNo, (SELECT r.type FROM Room r, Booking b "
               "WHERE b.roomNo = r.roomNo AND b.hotelNo = r.hotelNo AND b.hotelNo = h.hotelNo "
               "GROUP BY r.type ORDER BY COUNT(b.roomNo) DESC LIMIT 1) "
               "AS most_common_room_type FROM Hotel h WHERE h.city = 'London'"],
        "3F": ["Update the price of all rooms by 5%.",
               "UPDATE Room SET price = price * 1.05"],
        "3G": ["Create a view containing the hotel name and the names of the guests staying at the hotel.",
               "DROP VIEW IF EXISTS hotel_and_guests; "
               "CREATE VIEW hotel_and_guests AS SELECT h.hotelName, g.guestName FROM Guest g, Booking b, Hotel h "
               "WHERE g.guestNo = b.guestNo AND h.hotelNo = b.hotelNo"],
        "3H": ["Give the users Manager and Director full access to the hotel_and_guests view from 3g, "
               "with the privilege to pass the access on to other users.",
               "CREATE USER IF NOT EXISTS Manager; CREATE USER IF NOT EXISTS Director; "
               "GRANT ALL PRIVILEGES ON hotel_and_guests TO Manager, Director WITH GRANT OPTION"],
        "3IA": ["Give the user Accounts SELECT access to the hotel_and_guests view from 3g",
                "CREATE USER IF NOT EXISTS Accounts; GRANT SELECT ON  hotel_and_guests TO Accounts"],
        "3IB": ["Revoke access to the hotel_and_guests view from 3g from the user Accounts",
                "CREATE USER IF NOT EXISTS Accounts; REVOKE SELECT ON hotel_and_guests FROM Accounts"],
        "INSERT": ["Insert new data into a table."],
        "EXIT": ["Exit menu.", None]
    }

    # print welcome and menu options
    print("Welcome to the Hotel Database.")
    print_menu(menu_options)

    # get 1st query from user input
    query = get_query(menu_options)

    # loop until user is done
    while query is not None:
        try:
            # execute the query on the database
            if ";" in query:
                # need multi parameter if the query contains multiple SQL statements
                cursor.execute(query, multi=True)
            else:
                cursor.execute(query)
        except mysql.connector.Error as e:
            print("Could not execute the query. ERROR: " + e.msg)
        else:
            # print the column names for the returned data
            # only iterate if the cursor returns results
            if cursor.description:
                column_names = ""
                for column in cursor.description:
                    column_names += "{0: <25}".format(column[0])
                print(column_names)
                print('-'*len(column_names))
                # print the returned data
                for row in cursor.fetchall():
                    data = ""
                    for col in row:
                        data += "{0: <25}".format(str(col))
                    print(data)
            # if no results returned (updating, setting permissions, etc.)
            else:
                success = "Database operation executed successfully. "
                if cursor.rowcount > 0:
                    success += str(cursor.rowcount) + " rows affected."
                print(success)
        # get the user's next query
        query = get_query(menu_options)

    # exit choice chosen or failed to get query
    cursor.close()
    db_conn.commit()
    print("Goodbye.")
    db_conn.close()

