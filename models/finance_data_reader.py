import os
import shutil
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import progressbar
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
        print("   ", kwargs["status"], ": ", kwargs["deskripsi"], sep="")

        cursor.execute(
            """
            INSERT INTO logdata 
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                None,
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
        self.execute_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Nama file
        self.file_name = os.path.basename(file_path)

        # Mengambil periode waktu berdasarkan nama file
        self.period_time = get_period_time(self.file_name)

        # Nama sheet yang akan di proses
        self.sheet_name = "Data Konversi(Data Mart)"

        # Data finance
        self.data_type = "FinanceDataReader"

    # Reset attribute for the next process
    def reset_current_process_attributes(self):
        self.current_file_name = None
        self.current_data_type = None
        self.current_sheet_name = None
        self.current_period_time = None
        self.current_execute_time = None

    # File processing
    def process_file(self, file_path):
        self.set_current_process_attributes(file_path)

        xls = pd.ExcelFile(file_path)
        sheet_to_df_map = {}

        for sn in xls.sheet_names:
            sheet_to_df_map[sn] = xls.parse(sn)

        # Baca data pada sheet 'Data Konversi(Data Mart)'
        data = sheet_to_df_map[self.sheet_name]

        # Konversi struktur data
        data = data.replace({np.nan: None})
        dict_data = data.to_dict("records")
        cur = self.connection.cursor()

        print("Start:", str(self.execute_time))

        # Membuat bar progress
        bar = progressbar.ProgressBar(
            maxval=len(dict_data),
            widgets=[progressbar.Bar("=", "[", "]"), " ", progressbar.Percentage()],
        )

        bar.start()
        j = 0
        k = 0

        # Mengecek data pada logData apakah sudah tersedia
        is_exist = self.check_log_data()

        # Jika pada logData data belum pernah ada, masukkan ke table finance
        if not is_exist:
            # Masukkan data row by row
            for i in range(len(dict_data)):
                bar.update(i)
                time.sleep(0.01)

                data_hasil = list(dict_data[i].values())
                data_hasil.append(self.execute_time)

                if isinstance(data_hasil[0], (int, float)):
                    data_hasil = [0 if v is None else v for v in data_hasil]

                    cur.execute(
                        """
                                SELECT COUNT(*) 
                                FROM finance
                                WHERE id_cluster_finance = '%s' 
                                AND unit_name = '%s' 
                                AND id_component_name = '%s' 
                                AND bytelevel = '%s' 
                                AND bRealization = '%s' 
                                AND py = '%s' 
                                AND pm = '%s'
                                """
                        % (
                            int(data_hasil[0]),
                            data_hasil[3],
                            data_hasil[4],
                            data_hasil[6],
                            int(data_hasil[7]),
                            int(data_hasil[8]),
                            int(data_hasil[10]),
                        )
                    )

                    data = cur.fetchall()
                    len_data = data[0][0]
                    if len_data == 0:
                        j += 1
                        cur.execute(
                            """
                                    INSERT INTO finance 
                                    VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                                    """
                            % (
                                data_hasil[0],
                                data_hasil[1],
                                data_hasil[2],
                                data_hasil[3],
                                data_hasil[4],
                                data_hasil[5],
                                data_hasil[6],
                                data_hasil[7],
                                data_hasil[8],
                                data_hasil[9],
                                data_hasil[10],
                                data_hasil[11],
                                data_hasil[12],
                            )
                        )

                else:
                    k += 1

            bar.finish()
            self.connection.commit()
            cur.close()

            # Jika jumlah data sesuai, masukkan Log Success ke logData
            if (j + k) == (len(dict_data)):
                self.insert_to_log_data(
                    status="Success",
                    deskripsi="Done",
                    jumlah_row=str(j),
                )

            # Jika jumlah data tidak sesuai, masukkan Log Error
            else:
                self.insert_to_log_data(
                    status="Error",
                    deskripsi="Data sudah terdapat di database",
                    jumlah_row=str(j),
                )

            # Pindahkan file
            source = file_path
            destination = os.path.join(os.path.dirname(file_path), "archive")
            shutil.move(source, destination)

            # Selesai

        # Jika pada logData data sudah pernah ada, masukkan Log Error
        else:
            self.insert_to_log_data(
                status="Error",
                deskripsi="Data sudah pernah diinput atau sheet tidak sesuai",
                jumlah_row=str(j),
            )

        self.reset_current_process_attributes()

    # ----------------
