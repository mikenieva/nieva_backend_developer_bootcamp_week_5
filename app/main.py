import logging
from app.middleware.request_logging import request_logging_middleware
from fastapi.middleware.cors import CORSMiddleware


from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import AuthorNotFoundError, BookNotFoundError, DuplicateIsbnError
from app.routers import authors, books

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

tags_metadata = [
    {"name": "health", "description": "Estado del servicio."},
    {"name": "authors", "description": "Registrar y consultar autores."},
    {"name": "books", "description": "El catálogo: alta, consulta, cambios y baja de libros."},
]

app = FastAPI(
    title="Library API",
    description="API de biblioteca: Week 5, Backend Python Developer Bootcamp",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.middleware("http")(request_logging_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

app.include_router(authors.router)
app.include_router(books.router)


@app.exception_handler(AuthorNotFoundError)
@app.exception_handler(BookNotFoundError)
async def not_found_handler(request: Request, exc: AuthorNotFoundError | BookNotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})


@app.exception_handler(DuplicateIsbnError)
async def duplicate_isbn_handler(request: Request, exc: DuplicateIsbnError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.get("/", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Responde `ok` si el servicio está arriba."""
    return {"status": "ok", "service": "library-api"}