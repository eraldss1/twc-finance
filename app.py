from models.finance_data_reader import FinanceDataReader
from models.watcher import Watcher
import yaml

with open("./config/twc_config.yml", "r") as file:
    twc_config = yaml.safe_load(file)

    driver = FinanceDataReader(
        host=twc_config["host"],
        user=twc_config["user"],
        password=twc_config["password"],
        database=twc_config["database"],
        path=twc_config["directory_to_watch"],
    )

    watcher = Watcher(path=twc_config["directory_to_watch"], driver=driver)

if __name__ == "__main__":
    watcher.run()
