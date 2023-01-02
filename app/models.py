from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base

# middle table
user_city = Table(
    'user_city',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('city_id', Integer, ForeignKey('cities.id'), primary_key=True))


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    last_name = Column(String)
    foreign_key_cart = Column(Integer, unique=True)

    city_id = Column(Integer, ForeignKey('cities.id'))
    cities = relationship("City", back_populates="users")


# City model
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String)
    post_code = Column(String, unique=True)
    post_number = Column(Integer)

    users = relationship("User", back_populates="cities")

    country_id = Column(Integer, ForeignKey("countries.id"))
    countries = relationship("Country", back_populates="cities")


# Country model
class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String, unique=True)
    country_code = Column(String, unique=True)

    cities = relationship("City", back_populates="countries")
