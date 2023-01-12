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
import aiohttp
from sentry_sdk import set_level

from fastapi.middleware.cors import CORSMiddleware

sentry_sdk.init(
    dsn="https://60d860690425432bb80de5af728ffe3b@o4504418811641857.ingest.sentry.io/4504418813280256",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
    debug=False,
    server_name="uporabniki",
    release="v1.0.0",
    environment="production"
)
set_level("info")

models.Base.metadata.create_all(bind=engine)

broken = False


def check_db_connection(check_db_free=False):
    try:
        conn = psycopg2.connect(f"dbname={database} user={username} host={hostname} password={password} "
                                f"connect_timeout=1")
        cursor = conn.cursor()
        db_space_left_mb = -1
        if check_db_free is True:
            cursor.execute("SELECT pg_database_size( current_database() )")
            db_space_left_mb = 20 - cursor.fetchall()[0][0] / 1024 / 1024
        cursor.close()
        conn.close()
        if db_space_left_mb != -1:
            if db_space_left_mb > 5:
                return True
            return False
        return True
    except:
        print("I am unable to connect to the database")
        return False


def get_ms_status():
    global broken
    return not broken
    # global database_working
    # database_working = check_db_connection()
    # print(broken, database_working)
    # if broken or not database_working:
    #     return {"status": "broken"}
    # return {"status_ms": "The microservice is working",
    #         "status_db": "Database is working and connected to the microservice",
    #         "date": get_date_and_time()}


def is_ms_alive():
    if broken or not database_working:
        return False
    return True


def check_db_conn():
    return check_db_connection()


def check_db_space_left():
    return check_db_connection(True)


async def health_success_failure_handler(**conditions):
    rez = {"status": "UP", "checks": []}
    for cond in conditions:
        to_add = {
            "name": cond,
            "status": conditions[cond]
        }
        rez["checks"].append(to_add)
        if not conditions[cond]:
            rez["status"] = "DOWN"
    return rez


tags_metadata = [
    {"name": "users"},
    {"name": "cities"},
    {"name": "countries"},
    {"name": "health"},
]

app = FastAPI(
    root_path="/pusers",
    docs_url="/openapi",
    openapi_tags=tags_metadata,
)
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

health_handler = health([get_ms_status, check_db_conn, check_db_space_left],
                        success_handler=health_success_failure_handler,
                        failure_handler=health_success_failure_handler)
app.add_api_route("/health/liveness", health_handler, name="check liveness", tags=["health"])
app.add_api_route("/health/readiness", health_handler, name="check readiness", tags=["health"])
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


@app.get("/users", response_model=list[schemas.User], tags=["users"])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/", response_model=schemas.User, tags=["users"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name_and_last_name(db, name=user.name, last_name=user.last_name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    # TODO first create kosarica by calling Anžes microservice, and get the id of the kosarica
    async with aiohttp.ClientSession() as session:
        async with session.post('http://20.54.18.220/kosaricems/kosarice/',
                                json={"imeKosarice": f"{user.name}{user.last_name}"}) as resp:
            kosarica = await resp.json()
    kosarica_id = kosarica["id"]
    user.foreign_key_cart = kosarica_id
    # and use it to create the user
    return crud.create_user(db=db, user=user)


@app.delete("/users/{user_id}", response_model=schemas.User, tags=["users"])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)


@app.get("/users/{id}")
async def get_user(id: int):
    return f"This is the id that was sent through {id}."


@app.post("/users/login", response_model=schemas.User, tags=["users"])
async def get_user_with_name_and_last_name(user: schemas.UserBase, db: Session = Depends(get_db)):
    return crud.get_user_by_name_and_last_name(db, name=user.name, last_name=user.last_name)


@app.get("/cities", response_model=list[schemas.City], tags=["cities"])
async def get_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cities = crud.get_cities(db, skip=skip, limit=limit)
    return cities


# for creating a city
@app.post("/cities/", response_model=schemas.City, tags=["cities"])
async def create_city(city: schemas.CreateCity, db: Session = Depends(get_db)):
    db_city = crud.get_city(db, post_code=city.post_code)
    if db_city:
        raise HTTPException(status_code=400, detail="City already registered")
    return crud.create_city(db=db, city=city)


@app.get("/countries", response_model=list[schemas.Country], tags=["countries"])
async def get_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = crud.get_countries(db, skip=skip, limit=limit)
    return countries


@app.post("/countries/", response_model=schemas.Country, tags=["countries"])
async def create_country(country: schemas.CreateCountry, db: Session = Depends(get_db)):
    db_country = crud.get_country(db, country_code=country.country_code)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already registered")
    return crud.create_country(db=db, country=country)


@app.post("/break", tags=["health"])
async def break_app():
    global broken
    broken = True
    return {"The app has been broken"}


# sentry error trigger
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


@app.post("/countries/{country_id}/cities/", response_model=schemas.City, tags=["countries"])
def create_city_for_country(country_id: int, city: schemas.CreateCity, db: Session = Depends(get_db)):
    return crud.create_country_city(db=db, city=city, country_id=country_id)


@app.post("/cities/{city_id}/users/", response_model=schemas.User, tags=["cities"])
def create_user_for_city(city_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_city_user(db=db, user=user, city_id=city_id)


@app.get("/try_vreme")
async def get_vreme():
    url = "http://20.54.18.220/recommend/priporocila/Ljubljana"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    return {"This is the weather": data}
