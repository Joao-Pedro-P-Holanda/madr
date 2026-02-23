# Meu Acervo Digital de Romances

Projeto de uma API em Python com FastAPI como projeto final do curso de Fastapi do Zero do Dunossauro.

Algumas coisas extras que incluí foram:
- Rota `minha-conta` com informações do usuário logado
- Campos de nacionalidade e ano de nascimento para os autores
- Campo de ISBN para livros
- Relação muitos para muitos de autores e livros
- Sanitização como `BeforeValidator` nos campos de nome
- Verificação dos schemas nos testes

## Execução

### Com UV

A configuração inicial é feita com:
```uv sync```

Seguido de :
```uv run alembic upgrade head```

O comando para iniciar a API é:
```sh
# para o modo de produção é só substituir fastapi dev por fastapi run
uv run fastapi dev 
``` 

Os testes podem ser executados com:
```uv run pytest```

### Com Docker

Para rodar a API com Docker basta usar:
```docker compose up```
na raiz do projeto
