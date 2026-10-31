# Raízes do Nordeste

API de gerenciamento de uma rede de lanchonetes, desenvolvida em Python com FastAPI como parte do Projeto Multidisciplinar da UNINTER — Trilha Back-End.

## Objetivo

O sistema permite gerenciar usuários, unidades, produtos, estoque, pedidos, pagamentos simulados, fidelidade, promoções e informações administrativas.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- SQLite
- JWT
- Swagger UI
- Postman

## Funcionalidades

- Cadastro e autenticação de usuários.
- Controle de acesso por perfil.
- Cadastro e consulta de unidades.
- Gerenciamento de produtos.
- Controle de estoque por unidade.
- Criação, confirmação, acompanhamento e cancelamento de pedidos.
- Identificação e filtragem dos pedidos por canal: APP, TOTEM, BALCAO, PICKUP e WEB.
- Registro de pagamentos simulados.
- Programa de fidelidade com consentimento.
- Promoções e relatórios administrativos.
- Registro de eventos para auditoria.

## Requisitos para execução

- Python instalado.
- Acesso ao terminal do sistema operacional.

## Instalação

Clone o repositório ou baixe seus arquivos.

Abra o terminal na pasta principal do projeto.

### 1. Criar o ambiente virtual

No Windows:

```powershell
python -m venv .venv
```

### 2. Ativar o ambiente virtual

No PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 4. Executar a aplicação

```powershell
python -m uvicorn app.main:app --reload
```

### 5. Acessar a documentação

Com o servidor em execução, abra:

http://127.0.0.1:8000/docs

A especificação OpenAPI também pode ser consultada em:

http://127.0.0.1:8000/openapi.json

## Autenticação

A API utiliza tokens JWT para autenticação.

O cadastro público cria usuários com perfil CLIENTE.

As operações administrativas exigem permissões apropriadas.

O projeto contém o script `criar_admin.py`, utilizado para criar um usuário administrador.

**Importante:** não publique senhas, tokens JWT, arquivos `.env` com segredos ou dados pessoais reais no repositório.

## Banco de dados

O projeto utiliza SQLite e SQLAlchemy para persistência dos dados.

O arquivo local `raizes_do_nordeste.db` contém dados do ambiente de desenvolvimento e não deve ser publicado no repositório.

## Testes

Os testes da API foram executados no Postman.

Na execução registrada em 31 de outubro de 2026, foram obtidos:

- 12 requisições executadas.
- 14 verificações aprovadas.
- 0 verificações reprovadas.
- 0 erros de execução.

A coleção de testes está disponível na pasta `postman`.

Para executar os testes:

1. Inicie o servidor FastAPI.
2. Abra o Postman.
3. Importe a coleção JSON da pasta `postman`.
4. Configure as variáveis necessárias, sem divulgar credenciais.
5. Execute a coleção pelo Collection Runner.

## Documentação

A pasta `docs` contém:

- `requisitos.md` — requisitos funcionais e não funcionais.
- `arquitetura.md` — descrição da arquitetura.
- `der.md` — diagrama entidade-relacionamento.
- `diagrama_classes.md` — diagrama de classes.
- `casos_de_uso.md` — diagrama de casos de uso.
- `openapi.json` — especificação da API.
- Diagramas visuais em formato SVG.

## Estrutura principal

```text
RaizesDoNordeste/
├── app/
├── docs/
├── postman/
├── tests/
├── criar_admin.py
├── main.py
├── requirements.txt
└── README.md
```

## Considerações finais

O projeto demonstra o desenvolvimento de uma API REST para operações de uma rede de lanchonetes, incluindo autenticação, persistência de dados, regras de negócio, documentação técnica e testes automatizados.