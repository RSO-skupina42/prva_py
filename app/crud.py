from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name_and_last_name(db: Session, name: str, last_name: str):
    return db.query(models.User).filter(models.User.name == name, models.User.last_name == last_name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, last_name=user.last_name, foreign_key_cart=user.foreign_key_cart)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.name = db_user.name if user.name == "" else user.name
    db_user.last_name = db_user.last_name if user.last_name == "" else user.last_name
    db_user.cities = user.cities
    db_user.foreign_key_cart = db_user.foreign_key_cart if user.foreign_key_cart is None else user.foreign_key_cart
    # db_user.foreign_key_cart = user.foreign_key_cart
    db.commit()
    db.refresh(db_user)
    return db_user


def get_city(db: Session, city_id: int):
    return db.query(models.City).filter(models.City.id == city_id).first()


def get_cities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.City).offset(skip).limit(limit).all()


def create_city(db: Session, city: schemas.CreateCity):
    db_city = models.City(city_name=city.city_name, post_code=city.post_code)
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def delete_city(db: Session, city_id: int):
    db_city = db.query(models.City).filter(models.City.id == city_id).first()
    db.delete(db_city)
    db.commit()
    return db_city


def get_country(db: Session, country_id: int):
    return db.query(models.Country).filter(models.Country.id == country_id).first()


def get_countries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Country).offset(skip).limit(limit).all()


def create_country(db: Session, country: schemas.CreateCountry):
    db_country = models.Country(country_name=country.country_name, country_code=country.country_code)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country
