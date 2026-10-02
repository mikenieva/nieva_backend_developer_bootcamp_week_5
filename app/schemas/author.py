from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field, model_validator


class AuthorBase(BaseModel):
    """Los campos que comparten todas las versiones de un autor."""

    name: str = Field(min_length=2, max_length=100, examples=["Gabriel García Márquez"])
    nationality: str | None = Field(default=None, max_length=50, examples=["Colombia"])
    birth_date: date | None = Field(default=None, examples=["1927-03-06"])
    death_date: date | None = Field(default=None, examples=["2014-04-17"])


class AuthorCreate(AuthorBase):
    """Lo que el cliente manda al registrar un autor."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("name")
    @classmethod
    def collapse_inner_spaces(cls, v: str) -> str:
        return " ".join(v.split())

    @field_validator("birth_date", "death_date")
    @classmethod
    def not_in_the_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("la fecha no puede estar en el futuro")
        return v

    @model_validator(mode="after")
    def death_after_birth(self) -> Self:
        if self.birth_date and self.death_date and self.death_date <= self.birth_date:
            raise ValueError("death_date debe ser posterior a birth_date")
        return self

class AuthorInDB(AuthorBase):
    """Cómo guarda el servidor un autor."""

    id: int
    created_at: datetime

class AuthorResponse(AuthorBase):
    """Lo que la API devuelve de un autor."""

    id: int
    created_at: datetime
    book_count: int

    @computed_field
    @property
    def age(self) -> int | None:
        if self.birth_date is None:
            return None
        end = self.death_date or date.today()
        had_birthday = (end.month, end.day) >= (self.birth_date.month, self.birth_date.day)
        return end.year - self.birth_date.year - (0 if had_birthday else 1)


