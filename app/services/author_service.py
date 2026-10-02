from datetime import datetime, timezone

from app.exceptions import AuthorNotFoundError
from app.schemas.author import AuthorCreate, AuthorInDB


class AuthorService:
    def __init__(self) -> None:
        self._authors: dict[int, AuthorInDB] = {}
        self._next_id: int = 1

    def create(self, data: AuthorCreate) -> AuthorInDB:
        author = AuthorInDB(
            id=self._next_id,
            created_at=datetime.now(timezone.utc),
            **data.model_dump(),
        )
        self._authors[author.id] = author
        self._next_id += 1
        return author

    def get_by_id(self, author_id: int) -> AuthorInDB:
        author = self._authors.get(author_id)
        if author is None:
            raise AuthorNotFoundError(author_id)
        return author

    def list_all(self, skip: int, limit: int) -> list[AuthorInDB]:
        return list(self._authors.values())[skip : skip + limit]