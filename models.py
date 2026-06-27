from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(8), unique=True, index=True, nullable=False)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
