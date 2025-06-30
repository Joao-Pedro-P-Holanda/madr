from fastapi import APIRouter

router = APIRouter(prefix="/conta", tags=["Conta"])


@router.post("/entrar")
def login(): ...


@router.post("/cadastrar")
def sign_up(): ...


@router.put("/atualizar")
def update_account(): ...


@router.delete("/excluir")
def delete_account(): ...
