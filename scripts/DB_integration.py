import logging
import sqlalchemy as sqla
logger = logging.getLogger(__name__)
import yaml
import pandas as pd
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

class DBConvert(): 

    def __init__(self, domain, engine_object, config_file_contents, current_date_time, current_date):
        """
        create engine object to establish connection to DBMS. It provides connection pool that manages
        database connections.
        "engine = create_engine(dialect+driver://username:password@host:port/database_name)"
        """
        self.config_file_contents = config_file_contents
        self.current_date_time = current_date_time
        self.current_date = current_date
        self.domain = domain
        self.data_file_row_count = 0
        self.engine_object = engine_object
        self.details()
    
    def details(self):
        domain_main = self.domain.split("_")[0]
        self.table_name = self.config_file_contents["customer_domains"][domain_main]["tables"][self.domain]["table"]
        self.input_path = self.config_file_contents["folder_paths"][f"{self.domain}_input_path"]
        self.file_name = f"{self.domain}_{self.current_date}_{self.current_date_time}"
        self.schema_name = self.config_file_contents["customer_domains"][domain_main]["schema_source"]

    def read_db_table(self):
        """
        text() function converts string to SQL executable. Pandas executes it on engine.
        Function to read database table contents
        """
        sql_object = sqla.text(f"SELECT * from {self.schema_name}.{self.table_name}")
        self.df_table_contents = pd.read_sql_query(sql = sql_object, con = self.engine_object)
        # print(df_table_contents.head())

    def write_datafile_to_files_input(self):
        """
        This function moves the data from database to files_input respective folders as data file.
        """
        write_datafile = os.path.join(self.input_path, self.file_name + ".csv")
        self.df_table_contents.to_csv(write_datafile, index = False)
        self.data_file_row_count = len(self.df_table_contents)

    def write_controlfile_to_files_input(self):
        """
        This function moves the data from database to files_input respective folder as control file.
        """
        write_controlfile = os.path.join(self.input_path, self.file_name + "_control_file.csv")
        with open(write_controlfile,"w") as control_file:
            write_pointer = csv.writer(control_file)
            write_pointer.writerow(["file_name", "row_count"])
            write_pointer.writerow([self.file_name, self.data_file_row_count])

def run_DB_integration():
    """
    If imported to another file - this function will be called and the data extraction process will be triggered.
    """
    with open("config/config.yml", "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)
    
        load_dotenv()
        db_password = os.getenv("db_password")
        db_username = os.getenv("db_username")
        db_name = config_file_contents["access_details"]["source_db"]
        db_host = os.getenv("DB_HOST", config_file_contents["access_details"]["host"])

        logging.basicConfig(
            level = config_file_contents["logging"]["level"],
            format = config_file_contents["logging"]["format"],
        ) 
        domain_list = ["sales_header", "sales_item"]
        engine_object = sqla.create_engine(f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:5432/{db_name}")
    
        current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
        current_date = datetime.now().strftime("%Y%m%d")

        for domain in domain_list :
            convert_object = DBConvert(domain, engine_object, config_file_contents, current_date_time, current_date)
            convert_object.read_db_table()
            convert_object.write_datafile_to_files_input()
            convert_object.write_controlfile_to_files_input()
            logger.info(f"Table data now moved to input folder for domain - *** {domain} ***")                

if __name__ == "__main__":
    run_DB_integration()
