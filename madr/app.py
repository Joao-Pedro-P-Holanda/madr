from fastapi import FastAPI
from madr.routes import auth, authors, books
import uvicorn

app = FastAPI()


app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
