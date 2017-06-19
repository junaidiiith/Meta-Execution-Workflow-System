import mysql.connector
from mysql.connector import errorcode


class AddToDb:
    def __init__(self, **kwargs):
        self.user = kwargs.get('username')
        self.passwrd = kwargs.get('password')
        self.database = kwargs.get('database')
        self.conn = mysql.connector.connect(username=self.user, password=self.passwrd)
        cursor = self.conn.cursor()
        try:
            self.conn.database = kwargs.get('database')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(cursor)
                self.conn.database = self.database
            else:
                print(err)
        try:
            cursor.execute(kwargs.get('table'))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("table already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

        cursor.execute(kwargs.get('query'))

        self.conn.commit()
        cursor.close()
        self.conn.close()

    def create_database(self, cursor):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.database))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

