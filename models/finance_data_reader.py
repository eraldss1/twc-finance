import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
from alive_progress import alive_bar
from mysql.connector import Error, connect

from utils.get_period import get_period_time


class FinanceDataReader:
    connection = None
    path = None

    current_file_name = None
    current_data_type = None
    current_sheet_name = None
    current_period_time = None
    current_execute_time = None

    #################
    # Constructor
    def __init__(self, **config):
        try:
            self.connection = connect(
                host=config["host"],
                user=config["user"],
                password=config["password"],
                database=config["database"],
            )
            self.path = config["path"]

        except Error as e:
            print(e)
            sys.exit(1)

    # Destructor
    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    # ----------------

    #################
    # Test connection available
    def check_connection(self):
        if self.connection.is_connected:
            print("Connected")
        else:
            print("Not connected")

    # ----------------

    #################
    # Check if file_name exist in logdata and success to processed
    def check_log_data(self):
        cursor = self.connection.cursor(prepared=True)
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM logData
            WHERE fileName=(?)
            AND sheetName=(?)
            AND status=(?)
            """,
            (self.current_file_name, self.current_sheet_name, "Success"),
        )

        result = cursor.fetchall()
        cursor.close()

        row_count = result[0][0]
        if row_count > 0:
            return True
        else:
            return False

    # Insert new log data
    def insert_to_log_data(self, **kwargs):
        cursor = self.connection.cursor(prepared=True)
        print(f"{kwargs['status']}: {kwargs['deskripsi']}")

        cursor.execute(
            """
            INSERT INTO logdata 
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                self.current_file_name,
                self.current_data_type,
                self.current_sheet_name,
                self.current_period_time,
                self.current_execute_time,
                kwargs["status"],
                kwargs["deskripsi"],
                kwargs["jumlah_row"],
            ),
        )

        self.connection.commit()
        cursor.close()

    # ----------------

    #################
    # For each new file processing, generate the atrributes for logging
    def set_current_process_attributes(self, file_path):
        # Timestamp saat eksekusi file
        self.current_execute_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Nama file
        self.current_file_name = os.path.basename(file_path)

        # Mengambil periode waktu berdasarkan nama file
        self.current_period_time = get_period_time(self.current_file_name)

        # Nama sheet yang akan di proses
        self.current_sheet_name = "Data Konversi(Data Mart)"

        # Data finance
        self.current_data_type = "FinanceDataReader"

    # Reset attribute for the next process
    def reset_current_process_attributes(self):
        self.current_file_name = None
        self.current_data_type = None
        self.current_sheet_name = None
        self.current_period_time = None
        self.current_execute_time = None

    # Check if row already in finance table
    def check_finance(self, data):
        cursor = self.connection.cursor(prepared=True)
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM finance
            WHERE id_cluster_finance=(?)
            AND unit_name=(?)
            AND id_component_name=(?)
            AND bytelevel=(?)
            AND bRealization=(?)
            AND py=(?)
            AND pm=(?)
            """,
            (
                int(data[0]),
                data[3],
                data[4],
                data[6],
                int(data[7]),
                int(data[8]),
                int(data[10]),
            ),
        )
        result = cursor.fetchall()
        cursor.close()

        row_count = result[0][0]
        if row_count > 0:
            return True
        else:
            return False

    # Insert new row to finance
    def insert_to_finance(self, data):
        cursor = self.connection.cursor(prepared=True)
        cursor.execute(
            """
            INSERT INTO finance
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            tuple([x for x in data]),
        )

        self.connection.commit()
        cursor.close()

    # File processing
    def process_file(self, file_path):
        self.set_current_process_attributes(file_path)

        xls = pd.ExcelFile(file_path)
        sheet_to_df_map = {}

        for sn in xls.sheet_names:
            sheet_to_df_map[sn] = xls.parse(sn)

        # Baca data pada sheet 'Data Konversi(Data Mart)'
        data = sheet_to_df_map[self.current_sheet_name]

        # Konversi struktur data
        data = data.replace({np.nan: None})
        rows = data.to_dict(orient="records")
        cursor = self.connection.cursor()

        print("Start:", str(self.current_execute_time))

        inserted = 0
        not_inserted = 0

        # Mengecek data pada logData apakah sudah tersedia
        is_file_duplicate = self.check_log_data()

        # Jika pada logData data belum pernah ada, masukkan ke table finance
        if not is_file_duplicate:
            with alive_bar(len(data)) as bar:
                for row in rows:
                    arr = list(row.values())
                    arr.append(self.current_execute_time)

                    if isinstance(arr[0], (int, float)):
                        # If the cells contain None, set to 0
                        arr = [0 if value is None else value for value in arr]

                        is_row_duplicate = self.check_finance(arr)

                        if not is_row_duplicate:
                            inserted += 1
                            self.insert_to_finance(arr)
                        else:
                            # print(row)
                            not_inserted += 1

                    else:
                        not_inserted += 1

                    bar.text(f"| OK: {inserted} ~ DUPLICATE: {not_inserted}")
                    bar()

                # self.connection.commit()
                xls.close()
                cursor.close()

                # Jika jumlah data sesuai, masukkan Log Success ke logData
                if (inserted + not_inserted) == (len(data)):
                    self.insert_to_log_data(
                        status="Success",
                        deskripsi="Done",
                        jumlah_row=str(inserted),
                    )

                # Jika jumlah data tidak sesuai, masukkan Log Error
                else:
                    self.insert_to_log_data(
                        status="Error",
                        deskripsi="Data sudah terdapat di database",
                        jumlah_row=str(inserted),
                    )

                # Pindahkan file
                source = file_path
                destination = os.path.join(
                    os.path.dirname(file_path), "archive", self.current_file_name
                )
                os.rename(source, destination)

                print(f"Inserted: {inserted} \tNot inserted: {not_inserted}")
                # Selesai

        # Jika pada logData data sudah pernah ada, masukkan Log Error
        else:
            self.insert_to_log_data(
                status="Error",
                deskripsi="Data sudah pernah diinput atau sheet tidak sesuai",
                jumlah_row=str(inserted),
            )

        self.reset_current_process_attributes()

        print("\nListen to directory: {}".format(self.path))
        time.sleep(5)

    # ----------------
