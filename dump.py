import os
import asyncio
import json
import logging
from sqlalchemy import select
from datetime import datetime, timezone
from app.db import AsyncSessionLocal

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

async def create_database_dump(output_dir: str = "dumps"):
    """Creates a JSON dump of all cars in the database"""
    from app.models import Cars
    
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

asyncio.run(create_database_dump())
