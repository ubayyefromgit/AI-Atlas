# backend/services/ingestion/cleaners.py
import re
import pandas as pd
from typing import Any

def clean_string(val: Any) -> str | None:
    if pd.isna(val):
        return None
    
    val_str = str(val).strip()
    if val_str == "" or val_str.lower() == "nan" or val_str.lower() == "none":
        return None
        
    # Normalize unicode / multiple spaces
    val_str = re.sub(r'\s+', ' ', val_str)
    return val_str

def parse_multi_value(val: Any) -> list[str]:
    cleaned = clean_string(val)
    if not cleaned:
        return []
    
    # Handle JSON array strings loosely if someone exported them that way
    if cleaned.startswith('[') and cleaned.endswith(']'):
        # Very rough fallback for simple arrays
        cleaned = cleaned[1:-1].replace("'", "").replace('"', "")
        
    # Split on ; or | or ,
    # Priority: if ; exists, it's likely a semicolon delimited list. 
    # If not, check | then ,
    if ';' in cleaned:
        items = cleaned.split(';')
    elif '|' in cleaned:
        items = cleaned.split('|')
    else:
        items = cleaned.split(',')
        
    return [item.strip() for item in items if item.strip()]

def safe_int(val: Any) -> int | None:
    cleaned = clean_string(val)
    if not cleaned:
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None

def normalize_url(val: Any) -> str | None:
    cleaned = clean_string(val)
    if not cleaned:
        return None
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        return f"https://{cleaned}"
    return cleaned
