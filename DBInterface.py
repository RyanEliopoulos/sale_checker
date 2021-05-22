import sqlite3


class DBInterface:

    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.db_connection: sqlite3.Connection = sqlite3.connect(self.db_path, 10)
        self.db_connection.row_factory = sqlite3.Row
        self.db_cursor: sqlite3.Cursor = self.db_connection.cursor()

    def manual_control(self):
        """  For debugging
        """
        sqlstring = """
                        SELECT * FROM api_tokens 
                    """

        self.db_cursor.execute(sqlstring)
        resultset = self.db_cursor.fetchall()
        print("Heres the result set")
        print(resultset)
        for thing in resultset:
            print(thing[0])
            print(thing[1])
            print(thing[2])

    def seed_db(self) -> tuple[int, str]:
        """
        Initializes an empty database with appropriate tables.
        Drops tables if they already exist.

        :return: (int: 0 upon success, else -1,
                  str: Error/success message)
        """
        # Dropping tables
        sqlstring: str = """ DROP TABLE IF EXISTS api_tokens """
        self.db_cursor.execute(sqlstring)
        sqlstring = """ DROP TABLE IF EXISTS alerts """
        self.db_cursor.execute(sqlstring)

        # Creating table to house desired alerts
        # INTEGER alert_id is a shortcut for rowid. In other words, it will auto increment for us
        sqlstring: str = """ CREATE TABLE alerts (
                            alert_id INTEGER PRIMARY KEY,
                            product_name STRING NOT NULL,
                            upc INT NOT NULL,
                            target_discount INT NOT NULL)
                          """
        try:
            self.db_cursor.execute(sqlstring)
        except sqlite3.Error:
            return -1, 'Failed creating alert table'
        # Creating table to manage API tokens. Intended to only ever have 1 entry
        # INT for id field allows us to
        sqlstring: str = """ CREATE TABLE api_tokens (
                            id INT PRIMARY KEY,
                            access_token STRING NOT NULL,
                            refresh_token STRING NOT NULL,
                            timestamp INTEGER NOT NULL) 
                            """
        try:
            self.db_cursor.execute(sqlstring)
        except sqlite3.Error:
            return -1, 'Failed to create alert table'
        return 0, 'Success'

    def retrieve_tokens(self) -> tuple[int, tuple]:
        """
        Pulls api tokens
        :return: (int: -1 upon failure else 0,
                 tuple: Failure message
                 OR
                 tuple:
                    (str: access_token,
                    str: refresh_token,
                    int: unix_timestamp when tokens issued)
        """
        sqlstring: str = """ SELECT * FROM api_tokens
                             WHERE id = (?)
                         """
        try:
            self.db_cursor.execute(sqlstring, (1,))
        except sqlite3.Error:
            return -1, ('Failed to select tokens from the database',)

        resultrow: tuple = self.db_cursor.fetchone()
        if resultrow is None:
            return -1, ('No tokens in the database',)
        access_token: str = resultrow[1]
        refresh_token: str = resultrow[2]
        timestamp: str = resultrow[3]
        return 0, (access_token, refresh_token, timestamp)

    def update_tokens(self, access_token: str,
                      refresh_token: str,
                      unix_timestamp: str) -> tuple[int, str]:
        """
        Replaces the only row in the api_tokens table with updated tokens
        :return: (int: -1 if failure, else 0,
                 str: Success/failure message)
        """

        # Checking if the table is empty
        sqlstring: str = """ SELECT id from api_tokens 
                             WHERE id = (?)
                         """
        try:
            self.db_cursor.execute(sqlstring, (1,))
        except sqlite3.Error:
            return -1, 'Error reading from api_tokens table'
        alert_id: int = self.db_cursor.fetchone()
        if alert_id is not None:  # An existing entry to delete
            sqlstring = """ DELETE FROM api_tokens
                            WHERE id = (?)
                        """
            try:
                self.db_cursor.execute(sqlstring, alert_id)
            except sqlite3.Error:
                return -1, 'Error deleting old tokens from db'
        # Inserting new token data
        sqlstring = """ INSERT INTO api_tokens (id, access_token, refresh_token, timestamp)
                        VALUES (?, ?, ?, ?)
                    """
        try:
            self.db_cursor.execute(sqlstring, (1,
                                               access_token,
                                               refresh_token,
                                               unix_timestamp))
        except sqlite3.Error:
            return -1, 'Error inserting tokens into db'
        return 0, 'Success'

    def add_alert(self, product_name: str, upc: int, target_discount: int) -> tuple[int, str]:
        """
        Inserts the alert into the db
        :param product_name:
        :param upc: Taken from the item page on the website. Unique item identifier
        :param target_discount:  percentage
        :return: (int: -1 upon failure else 0,
                  str: outcome details
        """

        sqlstring: str = """ INSERT INTO alerts (product_name, upc, target_discount)
                             VALUES (?, ?, ?)
                         """
        try:
            self.db_cursor.execute(sqlstring, (product_name, upc, target_discount))
        except sqlite3.Error:
            return -1, 'Failed to insert alert'
        return 0, 'Success'

    def delete_alert(self, alert_id: int) -> tuple[int, str]:
        sqlstring: str = """ DELETE FROM alerts WHERE alert_id = (?)"""
        try:
            self.db_cursor.execute(sqlstring, (alert_id,))
        except sqlite3.Error:
            return -1, 'Failed to delete alert'
        return 0, 'Success'

    def retrieve_alerts(self) -> tuple[int, tuple]:
        """
        Pulls all rows from the alerts table
        :return: (int: -1 upon failure else 0,
                 tuple:
                    failure:  Failure message
                    else: List[{'alert_id': int,
                                 'product_name': str,
                                 'upc': int,
                                 'target_discount': int]

        """

        sqlstring: str = """ SELECT * FROM alerts """
        try:
            self.db_cursor.execute(sqlstring)
        except sqlite3.Error:
            return -1, ('Failure to select from alert table',)
        result_set = self.db_cursor.fetchall()
        result_list = []
        for row in result_set:
            new_dict: dict = dict()
            new_dict['alert_id'] = row[0]
            new_dict['product_name'] = row[1]
            new_dict['upc'] = row[2]
            new_dict['target_discount'] = row[3]
            result_list.append(new_dict)
        return 0, tuple(result_list)

