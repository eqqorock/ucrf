from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer, index=True)
    mileage = Column(Integer, default=0)
    engine_type = Column(String, nullable=True)
    transmission = Column(String, nullable=True)

    service_history = relationship("ServiceHistory", back_populates="vehicle")
    forecasts = relationship("Forecast", back_populates="vehicle")


class ServiceHistory(Base):
    __tablename__ = "service_history"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    service_date = Column(Date)
    service_type = Column(String)
    cost = Column(Float)

    vehicle = relationship("Vehicle", back_populates="service_history")


class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    predicted_issue = Column(String)
    likelihood = Column(Float)
    estimated_cost = Column(Float)
    range_months = Column(Integer)

    vehicle = relationship("Vehicle", back_populates="forecasts")
