from fastapi import APIRouter, Depends, status

from app.dependencies import BookFilters, PaginationParams, get_book_service
from app.schemas.book import BookCreate, BookInDB, BookResponse, BookUpdate
from app.services.book_service import BookService

router = APIRouter(prefix="/api/v1/books", tags=["books"])

NOT_FOUND = {404: {"description": "El libro no existe"}}
CONFLICT = {409: {"description": "Ya existe un libro con ese ISBN"}}
AUTHOR_NOT_FOUND = {404: {"description": "El autor de author_id no existe"}}


@router.get("", response_model=list[BookResponse], summary="Listar libros")
def list_books(
    page: PaginationParams = Depends(),
    filters: BookFilters = Depends(),
    books: BookService = Depends(get_book_service),
) -> list[BookInDB]:
    """Devuelve el catálogo, paginado y con filtros opcionales."""
    return books.list_all(
        page.skip, page.limit,
        genre=filters.genre, min_price=filters.min_price, max_price=filters.max_price,
    )


@router.get("/{book_id}", response_model=BookResponse, summary="Obtener un libro",
            responses=NOT_FOUND)
def get_book(book_id: int, books: BookService = Depends(get_book_service)) -> BookInDB:
    """Busca un libro por su id."""
    return books.get_by_id(book_id)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED,
             summary="Dar de alta un libro", responses={**AUTHOR_NOT_FOUND, **CONFLICT})
def create_book(data: BookCreate, books: BookService = Depends(get_book_service)) -> BookInDB:
    """Da de alta un libro. El autor tiene que existir y el ISBN no se puede repetir."""
    return books.create(data)


@router.put("/{book_id}", response_model=BookResponse, summary="Actualizar un libro",
            responses=NOT_FOUND)
def update_book(
    book_id: int,
    data: BookUpdate,
    books: BookService = Depends(get_book_service),
) -> BookInDB:
    """Actualización parcial: solo cambia los campos que mandes."""
    return books.update(book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Dar de baja un libro", responses=NOT_FOUND)
def delete_book(book_id: int, books: BookService = Depends(get_book_service)) -> None:
    """Da de baja un libro. No devuelve body."""
    books.delete(book_id)