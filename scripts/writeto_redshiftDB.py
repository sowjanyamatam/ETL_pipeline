import pandas as pd
import os
import shutil
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
import time
import yaml
import sqlalchemy as sqla
from dotenv import load_dotenv
import psycopg2

class Convert(): 
    """
    A class named "Convert".\n
    Attributes:
        NA
    """
    with open("config/config.yml", "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)
    processed_folder_path = config_file_contents["folder_paths"]["processed_folder_path"]
    db_name = config_file_contents["access_details"]["load_dbname"]

    load_dotenv()
    db_password = os.getenv("db_password")
    db_username = os.getenv("db_username")

    logging.basicConfig(
    level = config_file_contents["logging"]["level"],
    format = config_file_contents["logging"]["format"],
    )
    
    def __init__(self):
        """
        Initialize all the variables
        """
        self.files_folders_list = []
        self.files_list = []
        self.engine_object = sqla.create_engine(f"postgresql+psycopg2://{self.db_username}:{self.db_password}@localhost:5432/{self.db_name}")
       
    def write_to_redshiftDB(self):
        """
        This input and output file contents are moved to Redshift Database in Postgresql into schema_raw 
        and schema_output respectively.
        """
        # List of files in Processed folder
        self.files_folders_list = os.listdir(self.processed_folder_path)
        # To remove hidden .file and folders present
        for list_item in self.files_folders_list:
            if list_item.startswith("."):
                    continue
            else:
                self.list_item_path = os.path.join(self.processed_folder_path, list_item)
                if os.path.isfile(self.list_item_path):
                    self.files_list.append(list_item)
        # Read .csv contents and writing to db schema_output schema
        for file1 in self.files_list:
            if "control" in file1:
                control_file = file1
                control_file_path = os.path.join(self.processed_folder_path, control_file)
                df_control_file = pd.read_csv(control_file_path)
                df_control_file.to_sql("cars_control_file_processed", self.engine_object, schema = "schema_processed", if_exists = "append", index = False)
            else:
                data_file = file1
                data_file_path = os.path.join(self.processed_folder_path, data_file)
                df_data_file = pd.read_csv(data_file_path)
                df_data_file.to_sql("cars_processed", self.engine_object, schema = "schema_processed", if_exists = "append", index = False)
             
if __name__ == "__main__":
    convert_object = Convert()
    convert_object.write_to_redshiftDB()
    logger.info("Data moved to redshift DB..")