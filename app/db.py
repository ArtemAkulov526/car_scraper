from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from models import Cars
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
import os
import asyncio
import json

load_dotenv()
Base = declarative_base()

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

DB_NAME = load_dotenv("DB_NAME")
DB_USER = load_dotenv("DB_USER")
DB_HOST = load_dotenv("DB_HOST") 
DB_PORT = load_dotenv("DB_PORT")
DB_PASSWORD = load_dotenv("DB_PASSWORD")

DATABASE_URL = "postgresql+asyncpg://DB_USER:DB_PASSWORD@db:5432/DB_NAME"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_cars_to_db(car_list):
    async with AsyncSessionLocal() as session:
        for car in car_list:
            try:
                exists = await session.execute(
                    Cars.__table__.select().where(Cars.url == car["url"])
                )
                if not exists.scalars().first():
                    db_car = Cars(
                        url=car["url"],
                        title=car.get("title"),
                        price_usd=car.get("price_usd"),
                        odometer=car.get("odometer"),
                        username=car.get("username"),
                        phone_number=car.get("phone_number"),
                        image_url=car.get("image_url"),
                        images_count=car.get("images_count"),
                        car_number=car.get("car_number"),
                        car_vin=car.get("car_vin")
                    )
                    session.add(db_car)
                    await session.commit() 
                    logger.info(f"Saved car to DB: {car.get('car_vin')} - {car.get('title')}")
            except IntegrityError:
                await session.rollback()
                logger.warning(f"Duplicate URL skipped: {car.get('url')}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving car to DB: {e} - {car.get('url')}")

async def create_database_dump(output_dir: str = "dumps"):
    """Creates a JSON dump of all cars in the database"""
    from models import Cars
    
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/cars_dump_{timestamp}.json"
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Cars))
        cars = result.scalars().all()
        
        cars_data = []
        for car in cars:
            car_dict = {
                "id": car.id,
                "url": car.url,
                "title": car.title,
                "price_usd": car.price_usd,
                "odometer": car.odometer,
                "username": car.username,
                "phone_number": car.phone_number,
                "image_url": car.image_url,
                "images_count": car.images_count,
                "car_number": car.car_number,
                "car_vin": car.car_vin,
                "datetime_found": car.datetime_found.isoformat() if car.datetime_found else None
            }
            cars_data.append(car_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cars_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Database dump created: {filename} cars)")
        return filename

asyncio.run(init_db()) #run once to create a db
asyncio.run(create_database_dump())
