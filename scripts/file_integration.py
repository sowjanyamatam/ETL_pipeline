import os
import shutil
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv
from my_constants import *
logger = logging.getLogger(__name__)

class Convert(): 
    def __init__(self, domain, BASE_DIR, config_file_contents):
        """
        Initialize all the instance variables
        """
        self.domain = domain
        self.BASE_DIR = BASE_DIR
        self.config_file_contents = config_file_contents
        self.files_list = []
        self.paths_based_on_domain()
        

    def paths_based_on_domain(self):
        """
        Here, based on domain from main - we are configuring the path variable.
        """
        self.input_path = self.BASE_DIR / self.config_file_contents[SOURCE_FILES_PATH][f"{self.domain}_source_path"]
        self.target_path = self.BASE_DIR / self.config_file_contents[FOLDER_PATHS][f"{self.domain}_input_path"]

    def data_extraction(self):
        """
        This function checks all the list of files in the given path folder.
        If there are files present in the particualr folder : moves the data to "files_input" folder.
        If no - prints " No files to process and exists"
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
                file_path = os.path.join(self.input_path, file1)
                shutil.move(file_path, self.target_path)
            logger.info(f"{self.domain} : Files moved from source to 'files_input' folder")
        else:
            logger.info(f"No files to process in {self.domain} folder...")

def run_file_integration():
    """
    If imported to another file - this function will be called and the data extraction process will be triggered.
    """

    # Configuring it to relative path so that i works in other systems. Removed absolute local paths.
    BASE_DIR = Path(__file__).resolve().parent.parent
    config_path = BASE_DIR / "config" / "config.yml"
    with open(config_path, "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)

    logging.basicConfig(
        level = config_file_contents["logging"]["level"],
        format = config_file_contents["logging"]["format"],
    )

    domains_list = ["material_header","material_item"]

    print()
    print()
    logger.info("-----Extraction of data from files in file_directory - header and item files for Material domain...-----")
    print()

    for domain in domains_list:
        print()
        logger.info(f"Now processing domain : *** {domain} ***")
        convert_object = Convert(domain, BASE_DIR, config_file_contents)
        convert_object.data_extraction()

if __name__ == "__main__":
    run_file_integration()
         