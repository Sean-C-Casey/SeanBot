import os
import sqlite3
import datetime as dt
import settings as env


class DatabaseConnection:
    __instances = 0

    def __init__(self) -> None:
        self.connection = None
        dir = os.path.dirname(os.path.realpath(__file__))
        db_file = env.DB
        self.db_path = os.path.join(dir, db_file)

        if DatabaseConnection.__instances > 0:
            raise sqlite3.Error("Cannot have more than one connection")

        DatabaseConnection.__instances += 1
        if not os.path.exists(self.db_path):
            # Must create new database and set up tables
            self.connection = sqlite3.connect(self.db_path)
            self.__create_tables()
            pass
        else:
            # Database already exists. Just open it
            self.connection = sqlite3.connect(self.db_path)
    

    def dispose(self):
        DatabaseConnection.__instances -= 1
        self.connection.close()
        del self
    

    def __create_tables(self):
        sql1 = """CREATE TABLE auth_token (
                      id INTEGER PRIMARY KEY,
                      token TEXT NOT NULL,
                      expiry INTEGER NOT NULL
                  );
               """
        sql2 = """CREATE TABLE post (
                      id INTEGER PRIMARY KEY,
                      title TEXT UNIQUE NOT NULL,
                      date TEXT NOT NULL
                  );
               """
        sql3 = """CREATE TABLE subscriber (
                      id INTEGER PRIMARY KEY,
                      first_name TEXT NOT NULL,
                      last_name TEXT NOT NULL,
                      email TEXT NOT NULL
                  );
               """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.execute(sql3)
            self.connection.commit()
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to create tables")
    

    def insert_subscriber(self, f_name, l_name, email):
        sql = "INSERT INTO subscriber(first_name, last_name, email)" \
              "VALUES('%s', '%s', '%s')" % (f_name, l_name, email)
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to insert values")
            return None
    

    def fetch_subscribers(self):
        sql = "SELECT first_name, last_name, email FROM subscriber"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to fetch data")
            return None
    

    def store_token(self, token, expiry):
        sql = "INSERT INTO auth_token(token, expiry)" \
              "VALUES('%s', %d)" % (token, expiry)
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to insert values")
            return None
    
    def retrieve_token(self) -> tuple:
        # First check the count
        sql = "SELECT COUNT(*) FROM auth_token"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            token_count = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to check token table count")
            return None
        
        if token_count == 0: # Empty table; no tokens stored
            return None
        else: # One token or more in database
            # Select most recent token only
            sql = "SELECT token, expiry FROM auth_token ORDER BY -expiry LIMIT 1"
            try:
                cursor = self.connection.cursor()
                cursor.execute(sql)
                row = cursor.fetchone()
                token, expiry = row

                if dt.datetime.now().timestamp() >= expiry:
                    # Token has expired. Delete it and return None
                    self.__clear_tokens()
                    return None
                else:
                    if token_count > 1:
                        self.__clear_tokens(limit=expiry)
                    return row
            except sqlite3.Error as e:
                print("Error:", e)
                print("Failed to retrieve token from database")
                return None
    

    def __clear_tokens(self, limit=None):
        # If given, delete everything older than limit
        sql = "DELETE FROM auth_token"
        if limit:
            sql += " WHERE expiry < %d" % limit
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to delete old tokens from database")
    

    # Return date in string format; is converted into datetime object elsewhere
    def retrieve_post_date(self, title):
        sql = "SELECT date FROM post WHERE title = '%s'" % title
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            date = cursor.fetchone()
            if date is not None:
                return date[0]
            else:
                return date
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to retrieve post date")
            return None


    def store_post(self, title, date: str):
        sql = "INSERT INTO post(title, date) VALUES('%s', '%s')" % (title, date)
        try:
            # Insert new entry
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            # Entry already exists, update instead
            sql = "UPDATE post SET date = '%s' WHERE title = '%s'" % (date, title)
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as e:
            print("Error:", e)
            print("Failed to save post date")


    def delete_post(self):
        pass
