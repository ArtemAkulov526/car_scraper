from sqlalchemy import  Integer, String, DateTime, func
from datetime import datetime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

class Cars(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    price_usd: Mapped[int | None] = mapped_column(Integer)
    odometer: Mapped[int | None] = mapped_column(Integer)
    username: Mapped[str | None] = mapped_column(String(255))
    phone_number: Mapped[str | None] = mapped_column(String)
    image_url: Mapped[str | None] = mapped_column(String)
    images_count: Mapped[int | None] = mapped_column(Integer)
    car_number: Mapped[str | None] = mapped_column(String(255))
    car_vin: Mapped[str | None] = mapped_column(String(17), unique=True)
    datetime_found: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


