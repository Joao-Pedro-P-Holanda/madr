from contextlib import asynccontextmanager
from fastapi import FastAPI
from madr.routes import auth, authors, books
import uvicorn

from madr.core.orm import init_mappings, remove_mappings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mappings()
    yield
    remove_mappings()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
