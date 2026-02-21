import csv
import os
import glob
from decimal import Decimal, InvalidOperation
from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.orm import Session

# Internal Imports
from src.models.merchant_event import MerchantEvent  
from src.schemas.merchant_event import MerchantEventCreate 

def _convert_to_iso8601(timestamp_str: str) -> str:
    """
    Convert timestamp string to ISO 8601 format using datetime.isoformat().
    If empty or cannot parse, returns empty string.
    """
    if not timestamp_str or not timestamp_str.strip():
        return ""
    
    timestamp_str = timestamp_str.strip()
    
    # Try parsing common datetime formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]
    
    # Try fromisoformat first for ISO 8601 strings
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.isoformat()
    except ValueError:
        pass
    
    # Try other common formats
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If all parsing fails, return empty string
    return "" 

def seed_data_from_folder(db: Session, folder_path: str):
    """
    Scans a folder for all CSV files and seeds them into the database.
    """
    # 1. Global Check: If the table already has data, skip the entire folder
    if db.query(MerchantEvent).first():
        print("Database already contains data. Skipping bulk seed...")
        return

    # 2. Find all CSV files in the directory
    csv_pattern = os.path.join(folder_path, "*.csv")
    csv_files = sorted(glob.glob(csv_pattern))

    if not csv_files:
        print(f"No CSV files found in {folder_path}")
        return

    print(f"Found {len(csv_files)} files. Starting bulk seed...")

    for file_path in csv_files:
        print(f"Processing: {os.path.basename(file_path)}...")
        _process_single_csv(db, file_path)

def _process_single_csv(db: Session, csv_file_path: str):
    """
    Internal helper to process a single CSV file.
    SKIPS rows ONLY if event_id or merchant_id is missing/empty.
    For all other fields (including empty event_timestamp), stores the row as is.
    event_id is read from the CSV file.
    """
    valid_records = []

    with open(csv_file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Get event_id and merchant_id from CSV
                event_id = row.get("event_id", "").strip()
                merchant_id = row.get("merchant_id", "").strip()
                
                # SKIP only if event_id is missing or empty
                if not event_id:
                    print(f"Skipping row: event_id is missing or empty")
                    continue
                
                # SKIP if event_id already exists in the database (duplicate)
                if db.query(MerchantEvent).filter(MerchantEvent.event_id == event_id).first():
                    print(f"Skipping row: event_id {event_id} already exists in database")
                    continue
                
                # Convert event_timestamp to ISO 8601 format
                raw_timestamp = row.get("event_timestamp", "")
                iso_timestamp = _convert_to_iso8601(raw_timestamp)
                
                # Extract all fields - empty strings will be converted to None by Pydantic
                event_data = MerchantEventCreate(
                    event_id=event_id,
                    merchant_id=merchant_id,
                    event_timestamp=iso_timestamp,
                    product=row.get("product", ""),
                    event_type=row.get("event_type", ""),
                    amount=row.get("amount", ""),
                    status=row.get("status", ""),
                    channel=row.get("channel", ""),
                    region=row.get("region", ""),
                    merchant_tier=row.get("merchant_tier", "")
                )
                
                # Append the dictionary for SQLAlchemy bulk insert
                valid_records.append(event_data.model_dump())

            except Exception as e:
                # Log row errors but keep going
                print(f"Error processing row in {os.path.basename(csv_file_path)}: {e}")
                
        # Execute Bulk Insert for this file
        if valid_records:
            db.execute(insert(MerchantEvent), valid_records)
            db.commit()
            print(f"Successfully seeded {len(valid_records)} records from {os.path.basename(csv_file_path)}.")
        else:
            print(f"No valid records to insert from {os.path.basename(csv_file_path)}.")
