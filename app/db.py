from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from models import Cars
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

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


