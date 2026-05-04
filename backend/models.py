from sqlalchemy import Column, Integer, Float, DateTime
from database import Base
import datetime

class ROI(Base):
    __tablename__ = "rois"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    x = Column(Float)
    y = Column(Float)
    width = Column(Float)
    height = Column(Float)
