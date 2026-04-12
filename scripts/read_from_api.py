import logging
logger = logging.getLogger(__name__)
import yaml
import pandas as pd
import requests
import json

class APIRead():
    with open("config/config.yml", "r") as yml_file:
        config_file_contents = yaml.safe_load(yml_file)
    logging.basicConfig(
    level = config_file_contents["logging"]["level"],
    format = config_file_contents["logging"]["format"],
    )
    api_url = config_file_contents["api_details"]["api_url"]

    def read_fromAPI(self):
        response_from_API = requests.get(self.api_url)
        json_response_from_api = json.dumps((response_from_API.json()), indent = 3)
        print(json_response_from_api)
        
if __name__ == "__main__":
    api_object = APIRead()
    api_object.read_fromAPI()