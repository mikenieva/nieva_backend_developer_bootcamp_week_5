from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field


class Genre(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"
    HISTORY = "history"
    TECHNOLOGY = "technology"


class Publication(BaseModel):
    """Los datos de la edición. Viaja anidado dentro del libro."""

    publisher: str = Field(min_length=1, max_length=100, examples=["Editorial Sudamericana"])
    year: int = Field(ge=1450, examples=[1967])
    edition: int = Field(default=1, ge=1, examples=[1])


class BookBase(BaseModel):
    """Los campos que comparten todas las versiones de un libro."""

    title: str = Field(min_length=1, max_length=200, examples=["Cien años de soledad"])
    isbn: str = Field(pattern=r"^[0-9]{13}$", examples=["9780307474728"])
    genre: Genre
    pages: int = Field(gt=0, le=10000, examples=[496])
    price: float = Field(gt=0, description="Precio de reposición si el lector lo pierde",
                         examples=[389.0])
    author_id: int = Field(examples=[1])
    publication: Publication


class BookCreate(BookBase):
    """Lo que el cliente manda al dar de alta un libro."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    acquisition_cost: float = Field(gt=0)
    supplier: str = Field(min_length=1, max_length=100)

    @field_validator("isbn", mode="before")
    @classmethod
    def remove_separators(cls, v: object) -> object:
        if isinstance(v, str):
            return v.replace("-", "").replace(" ", "")
        return v

    @field_validator("isbn")
    @classmethod
    def valid_checksum(cls, v: str) -> str:
        total = sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(v))
        if total % 10 != 0:
            raise ValueError("el dígito verificador del ISBN no cuadra")
        return v

class BookResponse(BookBase):
    """Lo que la API devuelve de un libro."""

    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def years_since_publication(self) -> int:
        return date.today().year - self.publication.year

class BookSummary(BaseModel):
    published_year: int = Field(alias="publishedYear")    

class BookUpdate(BaseModel):
    """Lo que el cliente manda al actualizar: todo opcional."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    genre: Genre | None = None
    pages: int | None = Field(default=None, gt=0, le=10000)
    price: float | None = Field(default=None, gt=0)

    @field_validator("title", "genre", "pages", "price")
    @classmethod
    def not_null(cls, v: object) -> object:
        if v is None:
            raise ValueError("no puede ser null: si no quieres cambiarlo, no lo mandes")
        return v


class BookInDB(BookBase):
    """Cómo guarda el servidor un libro. Incluye lo que nunca sale."""

    id: int
    acquisition_cost: float
    supplier: str
    created_at: datetime
    updated_at: datetime