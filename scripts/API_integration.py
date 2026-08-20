import logging
logger = logging.getLogger(__name__)
import yaml
import pandas as pd
import requests
from pathlib import Path
import os
import csv
from datetime import datetime
from my_constants import *
logger = logging.getLogger(__name__)
class APIRead():
    def __init__(self, BASE_DIR, config_file_contents, current_date_time, current_date):
        self.BASE_DIR = BASE_DIR
        self.config_file_contents = config_file_contents
        self.current_date_time = current_date_time
        self.current_date = current_date
        self.api_url = ""
        self.target_path = self.BASE_DIR / config_file_contents[FOLDER_PATHS]["api_files_input_path"]
        self.file_name = f"api_file_{self.current_date}_{self.current_date_time}"

    def read_fromAPI(self):
        self.api_url = self.config_file_contents["api_details"]["api_url"]
        self.file_path = os.path.join(self.target_path, self.file_name + ".csv")
        self.response_from_API = requests.get(self.api_url)
        json_data = self.response_from_API.json()
        self.df_json_data = pd.DataFrame([json_data])
        self.file_row_count = len(self.df_json_data)
    
    def writeto_datafile(self):
        if self.response_from_API.status_code == 200:
            self.df_json_data.to_csv(self.file_path, index = False)
            logger.info("API data moved to data file in 'files_input' folder")
            self.writeto_controlfile()
        else:
            logger.info("API connection failed with - ",self.response_from_API.status_code)
    
    def writeto_controlfile(self):
        control_file_path = os.path.join(self.target_path, self.file_name + "_control_file.csv")
        with open(control_file_path,"w") as control_file:
            write_pointer = csv.writer(control_file)
            write_pointer.writerow(["file_name", "row_count"])
            write_pointer.writerow([self.file_name, self.file_row_count])
        logger.info("API data moved to control file in 'files_input' folder")

def run_API_integration():
    """
    If imported to another file - this function will be called and the data extraction process will be triggered.
    """ 
    # Configuring it to relative path so that i works in other systems. Removed absolute local paths.
    BASE_DIR = Path(__file__).resolve().parent.parent
    config_path = BASE_DIR / "config" / "config.yml"
    with open(config_path, "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)

    current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
    current_date = datetime.now().strftime("%Y%m%d")
    
    
    logging.basicConfig(
        level = config_file_contents["logging"]["level"],
        format = config_file_contents["logging"]["format"],
    )

    api_object = APIRead(BASE_DIR, config_file_contents, current_date_time, current_date)
    api_object.read_fromAPI()
    api_object.writeto_datafile()            
        
if __name__ == "__main__":
    run_API_integration()
   