from datetime import datetime, timezone

from app.exceptions import BookNotFoundError, DuplicateIsbnError
from app.schemas.book import BookCreate, BookInDB, BookUpdate, Genre
from app.services.author_service import AuthorService


class BookService:
    def __init__(self, authors: AuthorService) -> None:
        self._authors = authors
        self._books: dict[int, BookInDB] = {}
        self._next_id: int = 1

    def create(self, data: BookCreate) -> BookInDB:
        self._authors.get_by_id(data.author_id)
        if any(book.isbn == data.isbn for book in self._books.values()):
            raise DuplicateIsbnError(data.isbn)

        now = datetime.now(timezone.utc)
        book = BookInDB(id=self._next_id, created_at=now, updated_at=now, **data.model_dump())
        self._books[book.id] = book
        self._next_id += 1
        return book

    def get_by_id(self, book_id: int) -> BookInDB:
        book = self._books.get(book_id)
        if book is None:
            raise BookNotFoundError(book_id)
        return book

    def list_all(
        self,
        skip: int,
        limit: int,
        genre: Genre | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        author_id: int | None = None,
    ) -> list[BookInDB]:
        books = list(self._books.values())
        if genre is not None:
            books = [b for b in books if b.genre == genre]
        if min_price is not None:
            books = [b for b in books if b.price >= min_price]
        if max_price is not None:
            books = [b for b in books if b.price <= max_price]
        if author_id is not None:
            books = [b for b in books if b.author_id == author_id]
        return books[skip : skip + limit]

    def count_by_author(self, author_id: int) -> int:
        return sum(1 for b in self._books.values() if b.author_id == author_id)

    def update(self, book_id: int, data: BookUpdate) -> BookInDB:
        book = self.get_by_id(book_id)
        changes = data.model_dump(exclude_unset=True)
        updated = book.model_copy(update={**changes, "updated_at": datetime.now(timezone.utc)})
        self._books[book_id] = updated
        return updated

    def delete(self, book_id: int) -> None:
        self.get_by_id(book_id)
        del self._books[book_id]