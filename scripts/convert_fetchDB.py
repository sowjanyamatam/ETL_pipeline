import logging
import sqlalchemy as sqla
logger = logging.getLogger(__name__)
import yaml
import pandas as pd
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

with open("config/config.yml", "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)
load_dotenv()

logging.basicConfig(
    level = config_file_contents["logging"]["level"],
    format = config_file_contents["logging"]["format"],
    ) 


class Convert(): 
    current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
    current_date = datetime.now().strftime("%Y%m%d")
    db_password = os.getenv("db_password")
    db_username = os.getenv("db_username")
    db_name = config_file_contents["access_details"]["db_name"]
    input_folder_path = config_file_contents["folder_paths"]["input_folder_path"]

    def __init__(self):
        """
        create engine object to establish connection to DBMS. It provides connection pool that manages
        database connections.
        "engine = create_engine(dialect+driver://username:password@host:port/database_name)"
        """
        self.data_file_row_count = 0
        self.engine_object = sqla.create_engine(f"postgresql+psycopg2://{self.db_username}:{self.db_password}@localhost:5432/{self.db_name}")

    def read_db_table(self):
        """
        Connect is used to take one connection from pool with the help of engine_object and executes and puts it backs.
        text() function converts string to SQL executable. Pandas executes it on engine.
        Function to read database table contents
        """
        sql_object = sqla.text("SELECT * from car")
        self.df_table_contents = pd.read_sql_query(sql = sql_object, con = self.engine_object)
        # print(df_table_contents.head())

    def write_datafile_to_files_input(self):
        """
        This function moves the data from database to files_input folder as data file.
        """
        self.write_datafile = self.input_folder_path + "cars_" + self.current_date + "_" + self.current_date_time + ".csv"
        self.df_table_contents.to_csv(self.write_datafile, index = False)
        self.data_file_row_count = len(self.df_table_contents)

    def write_controlfile_to_files_input(self):
        """
        This function moves the data from database to files_input folder as data file.
        """
        self.write_controlfile = self.input_folder_path + "cars_" + self.current_date + "_" + self.current_date_time + "_control_file.csv"
        control_data_file = "cars_" + self.current_date + "_" + self.current_date_time
        with open(self.write_controlfile,"w") as control_file:
            write_pointer = csv.writer(control_file)
            write_pointer.writerow(["file_name", "row_count"])
            write_pointer.writerow([control_data_file, self.data_file_row_count])
             
if __name__ == "__main__":
    convert_object = Convert()
    convert_object.read_db_table()
    convert_object.write_datafile_to_files_input()
    convert_object.write_controlfile_to_files_input()
    logger.info("Table data now moved to input folder...")