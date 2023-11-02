from models.finance_data_reader import FinanceDataReader
import yaml

with open("./config/twc_dashboard_config.yml", "r") as file:
    twc_dashboard_config = yaml.safe_load(file)

    driver = FinanceDataReader(
        host=twc_dashboard_config["host"],
        user=twc_dashboard_config["user"],
        password=twc_dashboard_config["password"],
        database=twc_dashboard_config["database"],
    )

    ###########################
    # driver.check_connection()

    ###########################
    file_name = 'TWCFINFEB2022.xlsx'
    sheet_name = 'Data Konversi(Data Mart)'
    status = 'Success'
    print(driver.check_log_data(file_name=file_name,
          sheet_name=sheet_name, status=status))
