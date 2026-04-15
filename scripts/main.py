import pandas as pd
import os
import shutil
from datetime import datetime
import yaml
import sqlalchemy as sqla
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from my_constants import *
from file_integration import run_file_integration
from DB_integration import run_DB_integration
from API_integration import run_API_integration
logger = logging.getLogger(__name__)

class Convert(): 
    def __init__(self, domain, engine_conn, BASE_DIR, config_file_contents):
        """
        Initialize all the instance variables
        """
        self.domain = domain
        self.config_file_contents = config_file_contents
        self.engine_object = engine_conn
        self.BASE_DIR = BASE_DIR
        self.validation_flag = 0
        self.files_present = 1
        self.data_file = ""
        self.control_file = ""
        self.df_data_file = None
        self.df_control_file = None
        self.data_file_path = ""
        self.control_file_path = ""
        self.files_list = []
        self.file_name = ""
        self.tables_paths_based_on_domain()

    def tables_paths_based_on_domain(self):
        """
        Here, based on domain from main - we are configuring the path variable and table destination
        """
        domain_name = self.domain
        domain_parts = self.domain.split("_")
        domain_main = domain_parts[0]
        self.data_table = self.config_file_contents[CUSTOMER_DOMAINS][domain_main]["tables"][domain_name]["table"]
        self.control_table = self.config_file_contents[CUSTOMER_DOMAINS][domain_main]["tables"][domain_name]["control_table"]
        self.schema_raw = self.config_file_contents[CUSTOMER_DOMAINS][domain_main]["schema_raw"]
        self.schema_validated = self.config_file_contents[CUSTOMER_DOMAINS][domain_main]["schema_validated"]
        self.input_path = self.BASE_DIR / self.config_file_contents[FOLDER_PATHS][f"{self.domain}_input_path"]
        self.processed_path = self.BASE_DIR / self.config_file_contents[FOLDER_PATHS][f"{self.domain}_processed_path"]

    def data_extraction(self):
        """
        This function checks all the list of files in the given path folder.
        If there are files present in the particualr folder : moves the data to corresponding schema_raw folder in postgres db
        else - exits and print - "No files to process"
        """
        logger.info("Checking if files exist in the particular folder...")
        files_folders_list = os.listdir(self.input_path)
        # To remove hidden .file and folders present
        for list_item in files_folders_list:
            if list_item.startswith("."):
                    continue
            else:
                list_item_path = os.path.join(self.input_path, list_item)
                if os.path.isfile(list_item_path):
                    self.files_list.append(list_item)
        logger.info(f"Present list of files - {self.files_list}")
        if len(self.files_list) != 0:
            for file1 in self.files_list:
                if "control" in file1:
                    self.control_file = file1
                    self.control_file_path = os.path.join(self.input_path, self.control_file)
                    self.df_control_file = pd.read_csv(self.control_file_path)
                    self.df_control_file.to_sql(self.control_table, self.engine_object, schema = self.schema_raw, if_exists = "append", index = False)
                else:
                    self.data_file = file1
                    self.data_file_path = os.path.join(self.input_path, self.data_file)
                    self.df_data_file = pd.read_csv(self.data_file_path)
                    self.df_data_file.to_sql(self.data_table, self.engine_object, schema = self.schema_raw, if_exists = "append", index = False)  
            logger.info("Data moved to redshift DB raw schema..")
        else:
            logger.info(f"No files to process in {self.domain} folder...")
            self.files_present = 0
        

    def data_validation(self):
        """
        This function validates the row_count in the control file and the no. of rows present in the data file.
        - If the given files are not in .csv, .json or .txt, it moves the files to error folder, else moves them to processed folder(for backup),
            and then to postgres schema_validated folder with extra columns(created date, timestamp, filename, processed date_time)
        - Differentiates the control and data file.
        """
        if self.files_present != 0:
            valid_formats = (".csv", ".json", ".txt")
            for file1 in self.files_list:
                if "control" in file1:                   
                    row_count_controlfile = self.df_control_file.at[0, 'row_count']
                else:                  
                    row_count_datafile = len(self.df_data_file)
            #If row count is equal, if control file corresponds to correct data file and if file format is correct, then move to Processed folder, else move to error folder.
            self.file_name = self.data_file
            if (self.df_control_file.at[0, 'file_name'] == os.path.splitext(self.data_file)[0]) and (row_count_controlfile == row_count_datafile) and (self.data_file.endswith(valid_formats) and self.control_file.endswith(valid_formats)):
                self.validation_flag = 1
            else:
                error_folder_path = self.BASE_DIR / self.config_file_contents[FOLDER_PATHS]["error_folder_path"]
                shutil.move(self.control_file_path, error_folder_path)                
                shutil.move(self.data_file_path, error_folder_path)
                if (self.df_control_file.at[0, 'file_name'] != os.path.splitext(self.data_file)[0]):
                    logger.error("Control file does not correspond to the data file: file names do not match. Please check..")
                elif (row_count_controlfile != row_count_datafile):
                    logger.error("Row count doesnot match  - files moved to Error folder, please check..")
                else:
                    logger.error("Please place files in valid formats (.csv, .json, .txt), for now moved the files to error folder...")

    def data_load(self):
        if self.validation_flag == 1 :
            date_timestamp_extract = self.df_control_file['file_name'].str.extract(r'_(\d{8})_(\d{14})').iloc[0]
            self.df_data_file['creation_date'] = date_timestamp_extract[0]
            self.df_data_file['creation_timestamp'] = date_timestamp_extract[1]
            self.df_data_file['file_name'] = self.file_name
            self.df_data_file['processed_date_time'] = datetime.now().strftime("%Y%m%d%H%M%S")
            
            self.df_control_file.to_sql(self.control_table, self.engine_object, schema = self.schema_validated, if_exists = "append", index = False)
            self.df_data_file.to_sql(self.data_table, self.engine_object, schema = self.schema_validated, if_exists = "append", index = False)  
            shutil.move(self.control_file_path, self.processed_path)
            shutil.move(self.data_file_path, self.processed_path)                
            logger.info("Files validated and moved to respective processed folders and to schmea = schma_validated in postgres db...")

def run_pipeline():

    # Configuring it to relative path so that i works in other systems. Removed absolute local paths.
    BASE_DIR = Path(__file__).resolve().parent.parent
    config_path = BASE_DIR / "config" / "config.yml"
    with open(config_path, "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)

    db_name = config_file_contents["access_details"]["target_db"]
    load_dotenv()
    db_password = os.getenv("db_password")
    db_username = os.getenv("db_username")
    db_host = os.getenv("DB_HOST", config_file_contents["access_details"]["host"])

    logging.basicConfig(
        level = config_file_contents["logging"]["level"],
        format = config_file_contents["logging"]["format"],
    )

    domains_list = ["material_header","material_item","sales_header","sales_item","api_files"]
    engine_conn = sqla.create_engine(f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:5432/{db_name}")

    run_file_integration()
    run_DB_integration()
    run_API_integration()

    print()
    print()
    logger.info("-----Starting pipeline cycle for all datasets - header and item files for Material and sales domains...-----")
    print()

    while(True):
        try:
            for domain in domains_list:
                print()
                logger.info(f"Now processing domain : *** {domain} ***")
                convert_object = Convert(domain, engine_conn, BASE_DIR, config_file_contents)
                convert_object.data_extraction()
                convert_object.data_validation()
                convert_object.data_load()
            time.sleep(10)
        except Exception as e:
            logger.error(f"Pipeline crashed: {e}")
            time.sleep(10)  

if __name__ == "__main__":
    run_pipeline()  
            