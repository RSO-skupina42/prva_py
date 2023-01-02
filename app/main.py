import psycopg2
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
import requests

from . import crud, models, schemas
from .database import SessionLocal, engine, hostname, username, password, database

from fastapi_health import health

from .helpers import get_date_and_time

import sentry_sdk

sentry_sdk.init(
    dsn="https://de026afa4ed84d37b803d9fff82b4d7c@o4504420047716352.ingest.sentry.io/4504420048764928",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)

models.Base.metadata.create_all(bind=engine)


def check_db_connection():
    try:
        conn = psycopg2.connect(f"dbname={database} user={username} host={hostname} password={password} "
                                f"connect_timeout=1")
        conn.close()
        return True
    except:
        print("I am unable to connect to the database")
        return False


def get_ms_status():
    global database_working
    database_working = check_db_connection()
    print(broken, database_working)
    if broken or not database_working:
        return {"status": "broken"}
    return {"status_ms": "The microservice is working",
            "status_db": "Database is working and connected to the microservice",
            "date": get_date_and_time()}


def is_ms_alive():
    if broken or not database_working:
        return False
    return True


app = FastAPI()
Instrumentator().instrument(app).expose(app)
app.add_api_route("/health/liveness", health([is_ms_alive, get_ms_status]))
broken = False
database_working = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users", response_model=list[schemas.User])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name_and_last_name(db, name=user.name, last_name=user.last_name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


@app.delete("/users/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)


@app.get("/users/{id}")
async def get_user(id: int):
    return f"This is the id that was sent through {id}."


@app.get("/cities", response_model=list[schemas.City])
async def get_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cities = crud.get_cities(db, skip=skip, limit=limit)
    return cities


# for creating a city
@app.post("/cities/", response_model=schemas.City)
async def create_city(city: schemas.CreateCity, db: Session = Depends(get_db)):
    db_city = crud.get_city(db, post_code=city.post_code)
    if db_city:
        raise HTTPException(status_code=400, detail="City already registered")
    return crud.create_city(db=db, city=city)


@app.get("/countries", response_model=list[schemas.Country])
async def get_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = crud.get_countries(db, skip=skip, limit=limit)
    return countries


@app.post("/countries/", response_model=schemas.Country)
async def create_country(country: schemas.CreateCountry, db: Session = Depends(get_db)):
    db_country = crud.get_country(db, country_code=country.country_code)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already registered")
    return crud.create_country(db=db, country=country)


@app.post("/break")
async def break_app():
    global broken
    broken = True
    return {"The app has been broken"}


# sentry error trigger
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


@app.post("/countries/{country_id}/cities/", response_model=schemas.City)
def create_city_for_country(country_id: int, city: schemas.CreateCity, db: Session = Depends(get_db)):
    return crud.create_country_city(db=db, city=city, country_id=country_id)


@app.post("/cities/{city_id}/users/", response_model=schemas.User)
def create_user_for_city(city_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_city_user(db=db, user=user, city_id=city_id)
