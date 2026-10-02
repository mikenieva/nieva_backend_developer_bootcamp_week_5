from fastapi import APIRouter, Depends, status

from app.dependencies import (
    PaginationParams,
    get_author_or_404,
    get_author_service,
    get_book_service,
)
from app.schemas.author import AuthorCreate, AuthorInDB, AuthorResponse
from app.schemas.book import BookInDB, BookResponse
from app.services.author_service import AuthorService
from app.services.book_service import BookService

router = APIRouter(prefix="/api/v1/authors", tags=["authors"])

NOT_FOUND = {404: {"description": "El autor no existe"}}


def to_response(author: AuthorInDB, books: BookService) -> AuthorResponse:
    return AuthorResponse(**author.model_dump(), book_count=books.count_by_author(author.id))


@router.get("", response_model=list[AuthorResponse], summary="Listar autores")
def list_authors(
    page: PaginationParams = Depends(),
    authors: AuthorService = Depends(get_author_service),
    books: BookService = Depends(get_book_service),
) -> list[AuthorResponse]:
    """Devuelve los autores registrados, paginados."""
    return [to_response(a, books) for a in authors.list_all(page.skip, page.limit)]


@router.get("/{author_id}", response_model=AuthorResponse, summary="Obtener un autor",
            responses=NOT_FOUND)
def get_author(
    author: AuthorInDB = Depends(get_author_or_404),
    books: BookService = Depends(get_book_service),
) -> AuthorResponse:
    """Busca un autor por su id, con cuántos libros tiene en el catálogo."""
    return to_response(author, books)


@router.post("", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED,
             summary="Registrar un autor")
def create_author(
    data: AuthorCreate,
    authors: AuthorService = Depends(get_author_service),
    books: BookService = Depends(get_book_service),
) -> AuthorResponse:
    """Registra un autor. El `id` y la fecha de alta los genera el servidor."""
    return to_response(authors.create(data), books)


@router.get("/{author_id}/books", response_model=list[BookResponse],
            summary="Libros de un autor", responses=NOT_FOUND)
def list_author_books(
    author: AuthorInDB = Depends(get_author_or_404),
    page: PaginationParams = Depends(),
    books: BookService = Depends(get_book_service),
) -> list[BookInDB]:
    """Devuelve los libros de un autor, paginados."""
    return books.list_all(page.skip, page.limit, author_id=author.id)