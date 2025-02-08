from pydantic import BaseModel, ValidationError
import pandas as pd
import json
import csv
import os

from utils.my_logging import logging 

class Extract:
    def __init__(self, path:str, schema_class:BaseModel=None) -> None:
        self.path = path
        self.files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        self.schema_class = schema_class

    def read_pharmacy_data(self):
        pharmacy_cache = {}
        for file in self.files:
            with open(self.path + '/' + file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pharmacy_cache[row['npi']] = row['chain']
        return pharmacy_cache
    
    def read_and_validate_events(self):
        valid_data = []

        for file in self.files:
            with open(self.path + '/' + file, 'r') as f:
                try:
                    data = json.load(f)
                    for event in data:
                        try:
                            # Validate the event using the schema class
                            valid_event = self.schema_class(**event)
                            valid_data.append(valid_event)
                        except ValidationError as e:
                            logging.info(f"In {file} invalid event found and skipped: {e}")
                except json.JSONDecodeError as e:
                    logging.info(f"Error reading JSON from {self.path + '/' + file}: {e}")
        return valid_data