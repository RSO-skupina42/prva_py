from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

from fastapi_health import health

from .helpers import get_date_and_time

models.Base.metadata.create_all(bind=engine)


def get_ms_status():
    if broken:
        return {"status": "broken"}
    return {"status": "The microservice is working",
            "date": get_date_and_time()}


def is_ms_alive():
    if broken:
        return False
    return True


app = FastAPI()
app.add_api_route("/health/liveness", health([is_ms_alive, get_ms_status]))
broken = False


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
    db_city = crud.get_city(db, city_id=city.id)
    if db_city:
        raise HTTPException(status_code=400, detail="City already registered")
    return crud.create_city(db=db, city=city)


@app.get("/countries", response_model=list[schemas.Country])
async def get_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = crud.get_countries(db, skip=skip, limit=limit)
    return countries


@app.post("/countries/", response_model=schemas.Country)
async def create_country(country: schemas.CreateCountry, db: Session = Depends(get_db)):
    db_country = crud.get_country(db, country_id=country.id)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already registered")
    return crud.create_country(db=db, country=country)


@app.post("/break")
async def break_app():
    global broken
    broken = True
    return {"The app has been broken"}
