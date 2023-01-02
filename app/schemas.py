from pydantic import BaseModel, Field


# User schema


# City schema
class CityBase(BaseModel):
    city_name: str
    post_code: str


class UserBase(BaseModel):
    name: str
    last_name: str
    foreign_key_cart: int


class User(UserBase):
    id: int
    city_id: int

    class Config:
        orm_mode = True


class City(CityBase):
    id: int
    post_number: int | None = None
    country_id: int | None = None
    users: list[User] | None = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class CreateCity(CityBase):
    post_number: int
    pass


class UserUpdate(UserBase):
    cities: list[City] = []

    class Config:
        orm_mode = True


# Country schema
class CountryBase(BaseModel):
    country_name: str
    country_code: str


class CreateCountry(CountryBase):
    pass


class Country(CountryBase):
    id: int
    cities: list[City] | None = []

    class Config:
        orm_mode = True
