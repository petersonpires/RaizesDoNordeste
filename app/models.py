from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(30), nullable=False, default="CLIENTE")
    ativo = Column(Boolean, nullable=False, default=True)
    consentimento_fidelidade = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    pedidos = relationship("Pedido", back_populates="usuario")


class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(200), nullable=False)
    telefone = Column(String(30), nullable=True)
    ativa = Column(Boolean, nullable=False, default=True)
    criada_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    estoques = relationship("Estoque", back_populates="unidade")
    pedidos = relationship("Pedido", back_populates="unidade")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    categoria = Column(String(80), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    estoques = relationship("Estoque", back_populates="produto")
    itens_pedido = relationship("ItemPedido", back_populates="produto")


class Estoque(Base):
    __tablename__ = "estoques"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)

    unidade = relationship("Unidade", back_populates="estoques")
    produto = relationship("Produto", back_populates="estoques")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    status = Column(String(30), nullable=False, default="CRIADO")
    canal_pedido = Column(String(30), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False, default=0)
    observacao = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="pedidos")
    unidade = relationship("Unidade", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")
    pagamento = relationship(
        "Pagamento",
        back_populates="pedido",
        uselist=False,
    )


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    metodo = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False, default="PENDENTE")
    valor = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    pedido = relationship("Pedido", back_populates="pagamento")


class Fidelidade(Base):
    __tablename__ = "fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
        unique=True,
    )
    pontos = Column(Integer, nullable=False, default=0)
    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    acao = Column(String(100), nullable=False)
    detalhes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

class PontuacaoPedido(Base):
    __tablename__ = "pontuacoes_pedidos"

    id = Column(Integer, primary_key=True, index=True)

    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id"),
        nullable=False,
        unique=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    pontos = Column(Integer, nullable=False)

    criado_em = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Promocao(Base):
    __tablename__ = "promocoes"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(100), nullable=False)

    descricao = Column(Text, nullable=True)

    produto_id = Column(
        Integer,
        ForeignKey("produtos.id"),
        nullable=False,
    )

    percentual_desconto = Column(
        Numeric(5, 2),
        nullable=False,
    )

    data_inicio = Column(DateTime, nullable=False)

    data_fim = Column(DateTime, nullable=False)

    ativa = Column(Boolean, nullable=False, default=True)

    criada_em = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
