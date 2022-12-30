from pydantic import BaseModel


# User schema


# City schema
class CityBase(BaseModel):
    city_name: str
    post_code: str


class CreateCity(CityBase):
    id: int
    pass


class City(CityBase):
    id: int
    post_number: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    last_name: str
    foreign_key_cart: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    cities: list[City] = []

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    cities: list[City] = []

    class Config:
        orm_mode = True


# Country schema
class CountryBase(BaseModel):
    country_name: str
    country_code: str


class CreateCountry(CountryBase):
    id: int
    pass


class Country(CountryBase):
    id: int
    cities: list[City] = []

    class Config:
        orm_mode = True
