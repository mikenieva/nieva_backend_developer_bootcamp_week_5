from fastapi import Depends, HTTPException, Query, status

from app.schemas.author import AuthorInDB
from app.schemas.book import Genre
from app.services.author_service import AuthorService
from app.services.book_service import BookService

author_service = AuthorService()
book_service = BookService(author_service)


def get_author_service() -> AuthorService:
    return author_service


def get_book_service() -> BookService:
    return book_service


class PaginationParams:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Cuántos resultados saltar"),
        limit: int = Query(default=20, ge=1, le=100, description="Máximo de resultados (1-100)"),
    ) -> None:
        self.skip = skip
        self.limit = limit


class BookFilters:
    def __init__(
        self,
        genre: Genre | None = Query(default=None, description="Filtra por género"),
        min_price: float | None = Query(default=None, ge=0, description="Precio mínimo"),
        max_price: float | None = Query(default=None, ge=0, description="Precio máximo"),
    ) -> None:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="min_price no puede ser mayor que max_price",
            )
        self.genre = genre
        self.min_price = min_price
        self.max_price = max_price


def get_author_or_404(
    author_id: int,
    authors: AuthorService = Depends(get_author_service),
) -> AuthorInDB:
    return authors.get_by_id(author_id)