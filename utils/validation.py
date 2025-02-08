from pydantic import BaseModel, ValidationError, condecimal, conint
from typing import List, Optional
import json
import csv
import os

# Define the Pharmacy Schema
class Pharmacy(BaseModel):
    npi: str
    chain: str

# Define the Claims Event Schema
class ClaimEvent(BaseModel):
    id: str
    npi: str
    ndc: str
    price: condecimal(gt=0)  # Price must be greater than 0
    quantity: condecimal(gt=0) # Quantity must be greater than 0
    timestamp: str

# Define the Revert Event Schema
class RevertEvent(BaseModel):
    id: str
    claim_id: str
    timestamp: str
