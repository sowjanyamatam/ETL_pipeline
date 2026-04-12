import pandas as pd
import os
import shutil
from datetime import datetime
import time
import yaml
import logging
logger = logging.getLogger(__name__)


with open("config/config.yml", "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)

input_folder_path = config_file_contents["folder_paths"]["input_folder_path"]
raw_folder_path = config_file_contents["folder_paths"]["raw_folder_path"]
processed_folder_path = config_file_contents["folder_paths"]["processed_folder_path"]
error_folder_path = config_file_contents["folder_paths"]["error_folder_path"]

logging.basicConfig(
    level = config_file_contents["logging"]["level"],
    format = config_file_contents["logging"]["format"],
    )



class Convert(): 
    def __init__(self):
        """
        Initialize all the variables
        """
        self.files_folders_list = []
        self.files_list = []
        self.data_file = ""
        self.control_file = ""
        self.raw_control_file_path = ""
        self.raw_data_file_path = ""
        self.df_control_file = pd.DataFrame()
        self.df_data_file = pd.DataFrame()
        self.error_flag = 0

    def file_exists(self):
        """
        This function checks all the list of files in the given input path folder.
        Returns:
            True : If there are files present 
            False : If there are no files present
        """
        logger.info("Checking if files exist...")
        self.files_folders_list = os.listdir(input_folder_path)
        # To remove hidden .file and folders present
        for list_item in self.files_folders_list:
            if list_item.startswith("."):
                    continue
            else:
                list_item_path = os.path.join(input_folder_path, list_item)
                if os.path.isfile(list_item_path):
                    self.files_list.append(list_item)
        logger.info(f"Present list of files - {self.files_list}")
        if len(self.files_list) == 0:
            return False
        else:
            return True

    def file_content_validation(self):
        """
        This function validates the row_count in the control file and the no. of rows present in the data file and validates.
            - If the given files are not in .csv, .json or .txt, it moves the files to error folder, else moves them to processed folder.
            - Differentiates the control and data file.
        """
        valid_formats = (".csv", ".json", ".txt")
        for file1 in self.files_list:
            if "control" in file1:
                self.control_file = file1
                control_file_path = os.path.join(input_folder_path, self.control_file)
                self.df_control_file = pd.read_csv(control_file_path)
                row_count_controlfile = self.df_control_file.at[0, 'row_count']
            else:
                self.data_file = file1
                data_file_path = os.path.join(input_folder_path, self.data_file)
                self.df_data_file = pd.read_csv(data_file_path)
                row_count_datafile = len(self.df_data_file)
        #If row count is equal, if control file corresponds to correct data file and if file format is correct, then move to Processed folder, else move to error folder.
        if (self.df_control_file.at[0, 'file_name'] == os.path.splitext(self.data_file)[0]) and (row_count_controlfile == row_count_datafile) and (self.data_file.endswith(valid_formats) and self.control_file.endswith(valid_formats)):
            shutil.move(control_file_path, raw_folder_path)
            shutil.move(data_file_path, raw_folder_path)
            logger.info("Files validated and moved to respected folders...")
        else:
            self.error_flag = 1
            shutil.move(control_file_path, error_folder_path)
            shutil.move(data_file_path, error_folder_path)
            if (self.df_control_file.at[0, 'file_name'] != os.path.splitext(self.data_file)[0]):
                logger.error("Control file does not correspond to the data file: file names do not match. Please check..")
            elif (row_count_controlfile != row_count_datafile):
                logger.error("Row count doesnot match  - files moved to Error folder, please check..")
            else:
                logger.error("Please place files in valid formats (.csv, .json, .txt), for now moved the files to error folder...")

    def file_conversion_datafile(self):
        """
        This function reads the datafile and saves it to .csv format.
         - Added extra columns: creation_date and timestamp from input file name, file name, processed date and time.
         - Moves file to output folder.
        """
        if self.error_flag == 0:
            self.processed_data_file_path = processed_folder_path + "cars_processed.csv"
            file_name = self.data_file
            # To add new column as date & time and change its format before moving files.
            date_timestamp_extract = self.df_control_file['file_name'].str.extract(r'_(\d{8})_(\d{14})').iloc[0]
            self.df_data_file['creation_date'] = date_timestamp_extract[0]
            self.df_data_file['creation_timestamp'] = date_timestamp_extract[1]
            self.df_data_file['file_name'] = file_name
            self.df_data_file['processed_date_time'] = datetime.now().strftime("%Y%m%d%H%M%S")
            if self.data_file.endswith(("txt", "csv", "json")):
                if os.path.exists(self.processed_data_file_path):
                    self.df_data_file.to_csv(self.processed_data_file_path, index = False, mode = "a", header = False)
                else:
                    self.df_data_file.to_csv(self.processed_data_file_path, index=False)
            else:
                logger.error("Please place files in valid formats (.csv, .json, .txt), for now moved the files to error folder...")

    def file_conversion_controlfile(self):
        """
        This function reads the control file and saves it to .csv format.
            - Moves file to Processed folder.
        """
        if self.error_flag == 0:
            self.processed_control_file_path = processed_folder_path + "cars_control_file_processed.csv"
            if self.control_file.endswith(("txt", "csv", "json")):
                if os.path.exists(self.processed_control_file_path):
                    self.df_control_file.to_csv(self.processed_control_file_path, index = False, mode = "a", header = False)
                else:
                    self.df_control_file.to_csv(self.processed_control_file_path, index = False)
            else:
                logger.error("Please place files in valid formats (.csv, .json, .txt), for now moved the files to error folder...")

             
if __name__ == "__main__":
    # Runs every 30secs and checks the input folder path for files.
    while(True):
        convert_object = Convert()
        if convert_object.file_exists():
            convert_object.file_content_validation()
            convert_object.file_conversion_datafile()
            convert_object.file_conversion_controlfile()
        else:
            logger.info("No files to process...")
        time.sleep(30)