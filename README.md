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

### Com poetry

A configuração inicial é feita com:
```poetry sync```

Seguido de :
```poetry rub alembic upgrade head```

O comando para iniciar a API é:
```sh
# para o modo de produção é só substituir fastapi dev por fastapi run
poetry run fastapi dev madr/app.py
``` 

Os testes podem ser executados com:
```poetry run pytest```

### Com 

