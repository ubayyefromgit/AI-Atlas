# backend/services/ingestion/loader.py
import os
import pandas as pd
import logging

logger = logging.getLogger("ingestion")

class CSVLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load_csv(self, filename: str) -> pd.DataFrame:
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logger.error(f"Missing required file: {filepath}")
            raise FileNotFoundError(f"Missing required dataset file: {filename}")
            
        try:
            # We read all as strings initially to avoid pandas inferring floats for empty strings etc.
            df = pd.read_csv(filepath, dtype=str, keep_default_na=False)
            logger.info(f"Loaded {len(df)} rows from {filename}")
            return df
        except Exception as e:
            logger.error(f"Failed to parse CSV {filename}: {str(e)}")
            raise e
