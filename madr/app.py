from fastapi import FastAPI
from .routes import auth, authors, books

app = FastAPI()


app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)
