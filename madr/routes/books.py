from fastapi import APIRouter

router = APIRouter(prefix="/livros", tags=["Livros"])


@router.get("/")
def get_list(): ...


@router.get("/{id}")
def get_one(id: int): ...


@router.post("/adicionar")
def create(): ...


@router.put("/atualizar")
def update(): ...


@router.delete("/excluir")
def delete(): ...
