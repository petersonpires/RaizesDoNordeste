
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.database import Base, engine
from app import models

from app.api.auth_routes import router as auth_router
from app.api.unidade_routes import router as unidade_router
from app.api.produto_routes import router as produto_router
from app.api.estoque_routes import router as estoque_router
from app.api.pedido_routes import router as pedido_router
from app.api.pagamento_routes import router as pagamento_router
from app.api.fidelidade_routes import router as fidelidade_router
from app.api.promocao_routes import router as promocao_router
from app.api import relatorio_routes


# ========================================
# LOCALIZAÇÃO DAS PASTAS
# ========================================

PASTA_APP = Path(__file__).resolve().parent

PASTA_TEMPLATES = PASTA_APP / "templates"
PASTA_STATIC = PASTA_APP / "static"


# ========================================
# BANCO DE DADOS
# ========================================

Base.metadata.create_all(bind=engine)


# ========================================
# APLICAÇÃO FASTAPI
# ========================================

app = FastAPI(
    title="Raízes do Nordeste",
    description="API de gerenciamento de uma rede de lanchonetes.",
    version="1.0.0",
)


# ========================================
# ARQUIVOS CSS E JAVASCRIPT
# ========================================

app.mount(
    "/static",
    StaticFiles(directory=str(PASTA_STATIC)),
    name="static",
)


# ========================================
# PÁGINAS HTML
# ========================================

templates = Jinja2Templates(
    directory=str(PASTA_TEMPLATES)
)


# ========================================
# ROTAS DA API
# ========================================

app.include_router(auth_router)
app.include_router(unidade_router)
app.include_router(produto_router)
app.include_router(estoque_router)
app.include_router(pedido_router)
app.include_router(pagamento_router)
app.include_router(fidelidade_router)
app.include_router(promocao_router)
app.include_router(relatorio_routes.router)


# ========================================
# TELA DE LOGIN
# ========================================

@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


# ========================================
# PAINEL ADMINISTRATIVO
# ========================================

@app.get("/painel", response_class=HTMLResponse)
def abrir_painel(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="painel.html",
    )


# ========================================
# TELA DE PRODUTOS
# ========================================

@app.get("/produtos/pagina", response_class=HTMLResponse)
def abrir_pagina_produtos(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="produtos.html",
    )


# ========================================
# TELA DE GERENCIAMENTO DE PEDIDOS
# ========================================

@app.get("/pedidos/pagina", response_class=HTMLResponse)
def abrir_pagina_pedidos(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="pedidos.html",
    )


# ========================================
# VERIFICAÇÃO DA API E BANCO
# ========================================

@app.get("/health")
def verificar_saude():

    try:

        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "banco_de_dados": "conectado",
        }

    except Exception:

        return {
            "status": "erro",
            "banco_de_dados": "desconectado",
        }
