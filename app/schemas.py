from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=100)
    perfil: str = "CLIENTE"
    consentimento_fidelidade: bool = False


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool
    consentimento_fidelidade: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel):
    email: EmailStr
    senha: str


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UnidadeCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    endereco: str = Field(min_length=5, max_length=200)
    telefone: Optional[str] = None


class UnidadeResposta(BaseModel):
    id: int
    nome: str
    endereco: str
    telefone: Optional[str]
    ativa: bool
    criada_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ProdutoCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: Optional[str] = None
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    categoria: str = Field(min_length=2, max_length=80)


class ProdutoResposta(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    preco: Decimal
    categoria: str
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class EstoqueCriar(BaseModel):
    unidade_id: int = Field(gt=0)
    produto_id: int = Field(gt=0)
    quantidade: int = Field(ge=0)


class EstoqueResposta(BaseModel):
    id: int
    unidade_id: int
    produto_id: int
    quantidade: int

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoCriar(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class PedidoCriar(BaseModel):
    unidade_id: int = Field(gt=0)
    canal_pedido: str
    observacao: Optional[str] = None
    itens: list[ItemPedidoCriar] = Field(min_length=1)


class ItemPedidoResposta(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: Decimal

    model_config = ConfigDict(from_attributes=True)


class PedidoResposta(BaseModel):
    id: int
    usuario_id: int
    unidade_id: int
    status: str
    canal_pedido: str
    valor_total: Decimal
    observacao: Optional[str]
    criado_em: datetime
    itens: list[ItemPedidoResposta]

    model_config = ConfigDict(from_attributes=True)


class StatusPedidoAtualizar(BaseModel):
    status: str


class PagamentoCriar(BaseModel):
    metodo: str
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class PagamentoResposta(BaseModel):
    id: int
    pedido_id: int
    metodo: str
    status: str
    valor: Decimal
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class FidelidadeResposta(BaseModel):
    id: int
    usuario_id: int
    pontos: int
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditoriaResposta(BaseModel):
    id: int
    usuario_id: Optional[int]
    acao: str
    detalhes: Optional[str]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)