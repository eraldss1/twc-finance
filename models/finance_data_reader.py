import sys
import os
from datetime import datetime
import time
import pandas as pd
import numpy as np
import progressbar
import shutil

from mysql.connector import Error, connect


class FinanceDataReader:
    connection = None
    path = None

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
            (
                kwargs["file_name"],
                kwargs["sheet_name"],
                kwargs["status"]
            ),
        )

        result = cursor.fetchall()
        cursor.close()

        row_count = result[0][0]
        if row_count > 0:
            return True
        else:
            return False

    def insert_to_log_data(self, **kwargs):
        cursor = self.connection.cursor(prepared=True)
        print("   ", kwargs['status'], ": ", kwargs['deskripsi'], sep="")

        cursor.execute(
            """
            INSERT INTO logdata 
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                None,
                kwargs['file_name'],
                kwargs['data_type'],
                kwargs['sheet_name'],
                kwargs['period_time'],
                kwargs['execute_time'],
                kwargs['status'],
                kwargs['deskripsi'],
                kwargs['jumlah_row']
            ),
        )

        self.connection.commit()
        cursor.close()

    def process_file(self, file_path):
        execute_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_time_str = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        file_name = os.path.basename(file_path)
        xls = pd.ExcelFile(file_path)
        sheet_to_df_map = {}

        for sheet_name in xls.sheet_names:
            sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

        # Mengambil periode waktu berdasarkan nama file
        period_time = self.get_period_time(file_name=file_name)

        # Baca data pada sheet 'Data Konversi(Data Mart)'
        data = sheet_to_df_map['Data Konversi(Data Mart)']

        # Konversi struktur data
        data = data.replace({np.nan: None})
        dict_data = data.to_dict('records')
        cur = self.connection.cursor()

        print('Start:', execute_time_str)

        # Membuat bar progress
        bar = progressbar.ProgressBar(
            maxval=len(dict_data),
            widgets=[
                progressbar.Bar('=', '[', ']'),
                ' ',
                progressbar.Percentage()
            ]
        )

        bar.start()
        j = 0
        k = 0
        sheet_name = 'Data Konversi(Data Mart)'
        data_type = 'FinanceDataReader'

        # Mengecek data pada logData apakah sudah tersedia
        is_exist = self.check_log_data(
            file_name=file_name,
            data_type=data_type,
            sheet_name=sheet_name,
            status='Success'
        )

        # Jika pada logData data belum pernah ada, masukkan ke table finance
        if not is_exist:
            # Masukkan data row by row
            for i in range(len(dict_data)):
                bar.update(i)
                time.sleep(0.01)

                data_hasil = list(dict_data[i].values())
                data_hasil.append(execute_time)

                if isinstance(data_hasil[0], (int, float)):
                    data_hasil = [0 if v is None else v for v in data_hasil]
                    #len_data = len(df_db.loc[(df_db['id_cluster_finance']==int(data_hasil[0])) & (df_db["member_name"]==data_hasil[3]) & (df_db["component_name"]==data_hasil[5]) & (df_db["bytelevel"]==int(data_hasil[6])) & (df_db["b_realization"]==int(data_hasil[7])) & (df_db["PY"]==int(data_hasil[8])) & (df_db["PM"]==int(data_hasil[10]))])

                    cur.execute("""
                                SELECT COUNT(*) 
                                FROM finance
                                WHERE id_cluster_finance = '%s' 
                                AND unit_name = '%s' 
                                AND id_component_name = '%s' 
                                AND bytelevel = '%s' 
                                AND bRealization = '%s' 
                                AND py = '%s' 
                                AND pm = '%s'
                                """ %
                                (int(data_hasil[0]),
                                 data_hasil[3], data_hasil[4],
                                 data_hasil[6],
                                 int(data_hasil[7]),
                                 int(data_hasil[8]),
                                 int(data_hasil[10])))

                    data = cur.fetchall()
                    len_data = data[0][0]
                    if len_data == 0:
                        j += 1
                        cur.execute("""
                                    INSERT INTO finance 
                                    VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                                    """ %
                                    (data_hasil[0],
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
                                     data_hasil[12]))

                else:
                    k += 1

            bar.finish()
            self.connection.commit()
            cur.close()

            # Jika jumlah data sesuai, masukkan Log Success ke logData
            if (j+k) == (len(dict_data)):
                self.insert_to_log_data(
                    file_name=file_name,
                    data_type=data_type,
                    sheet_name=sheet_name,
                    period_time=period_time,
                    execute_time=execute_time_str,
                    status="Success",
                    deskripsi="Done",
                    jumlah_row=str(j),
                )

            # Jika jumlah data tidak sesuai, masukkan Log Error
            else:
                self.insert_to_log_data(
                    file_name=file_name,
                    data_type=data_type,
                    sheet_name=sheet_name,
                    period_time=period_time,
                    execute_time=execute_time_str,
                    status="Error",
                    deskripsi="Data sudah terdapat di database",
                    jumlah_row=str(j),
                )

            # Pindahkan file
            destination = os.path.join(os.path.dirname(file_path), "archive")
            shutil.move()

        # Jika pada logData data sudah pernah ada, masukkan Log Error
        else:
            self.insert_to_log_data(
                file_name=file_name,
                data_type=data_type,
                sheet_name=sheet_name,
                period_time=period_time,
                execute_time=execute_time_str,
                status="Error",
                deskripsi="Data sudah pernah diinput atau sheet tidak sesuai",
                jumlah_row=str(j),
            )

    def get_period_time(self, file_name):
        period_time = file_name.split('.')[0].replace("TWCFIN", '').title()
        period_time = period_time[:3]+"_"+period_time[3:]
        return period_time

    def __del__(self):
        if self.connection != None:
            self.connection.close()
