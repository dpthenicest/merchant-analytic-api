import os
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Internal Imports
from src.database.database import Base
from src.models.merchant_event import MerchantEvent
# Update this import to match your new function name
from src.utils.csv_to_psql import seed_data_from_folder
from src.routers.analytic_routes import analytic_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown. 
    Truncates database on startup and seeds data from the folder.
    """
    logger.info("Starting up - truncating database and reseeding...")
    
    # 1. Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # 2. Truncate all existing data
    db = SessionLocal()
    try:
        db.query(MerchantEvent).delete()
        db.commit()
        logger.info("Database truncated.")
    except Exception as e:
        logger.error(f"Error truncating database: {e}")
        db.rollback()
    finally:
        db.close()
    
    # 3. Seed from folder
    db = SessionLocal()
    try:
        # Point to the root directory containing your CSVs
        data_folder = os.path.join(os.path.dirname(__file__), "../../../data")
        data_folder_env = os.getenv("DATA_FOLDER_PATH", "./data")
        data_folder = data_folder_env if os.path.exists(data_folder_env) else data_folder
        
        if os.path.exists(data_folder):
            seed_data_from_folder(db, data_folder)
            logger.info("Startup seeding process completed.")
        else:
            logger.warning(f"Data folder not found at: {data_folder}")
    except Exception as e:
        logger.error(f"Error during startup seeding: {e}")
    finally:
        db.close()

    yield 
    logger.info("Shutting down...")

# Initialize FastAPI with lifespan
app = FastAPI(
    debug=os.getenv('DEBUG', 'False').lower() == "true",
    lifespan=lifespan
)

# Include routers
app.include_router(analytic_router)

if __name__ == "__main__":
    # Using the import string "main:app" allows for hot-reloading
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
