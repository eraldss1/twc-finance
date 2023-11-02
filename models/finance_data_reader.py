import sys

from mysql.connector import Error, connect


class FinanceDataReader:
    def __init__(self, **config):
        try:
            self.connection = connect(
                host=config["host"],
                user=config["user"],
                password=config["password"],
                database=config["database"],
            )
        except Error as e:
            print(e)
            sys.exit(1)

    def check_connection(self):
        if(self.connection.is_connected):
            print("Connected")
        else:
            print("Not connected")

    def check_log_data(self, **kwargs):
        cursor = self.connection.cursor(prepared=True)
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM logData
            WHERE fileName=(?)
            AND sheetName=(?)
            AND status=(?)
            """,
            (kwargs["file_name"], kwargs["sheet_name"], kwargs["status"]),
        )

        if cursor.fetchone():
            return True
        else:
            return False

    

    def __del__(self):
        if self.connection != None:
            self.connection.close()
