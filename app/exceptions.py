class AuthorNotFoundError(Exception):
    """El autor pedido no existe."""

    def __init__(self, author_id: int) -> None:
        self.author_id = author_id
        self.message = f"El autor con id {author_id} no existe"
        super().__init__(self.message)


class BookNotFoundError(Exception):
    """El libro pedido no existe."""

    def __init__(self, book_id: int) -> None:
        self.book_id = book_id
        self.message = f"El libro con id {book_id} no existe"
        super().__init__(self.message)


class DuplicateIsbnError(Exception):
    """Ya hay un libro con ese ISBN."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        self.message = f"Ya existe un libro con el ISBN {isbn}"
        super().__init__(self.message)