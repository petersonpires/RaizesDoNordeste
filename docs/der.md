# DER — Diagrama Entidade-Relacionamento

## Projeto Raízes do Nordeste

Este diagrama representa as 11 entidades definidas no arquivo `app/models.py`, incluindo as chaves primárias (PK), as chaves estrangeiras (FK) e os relacionamentos.

```mermaid
erDiagram
    USUARIOS {
        int id PK
        string nome
        string email UK
        string senha_hash
        string perfil
        boolean ativo
        boolean consentimento_fidelidade
        datetime criado_em
    }

    UNIDADES {
        int id PK
        string nome
        string endereco
        string telefone
        boolean ativa
        datetime criada_em
    }

    PRODUTOS {
        int id PK
        string nome
        text descricao
        decimal preco
        string categoria
        boolean ativo
        datetime criado_em
    }

    ESTOQUES {
        int id PK
        int unidade_id FK
        int produto_id FK
        int quantidade
    }

    PEDIDOS {
        int id PK
        int usuario_id FK
        int unidade_id FK
        string status
        string canal_pedido
        decimal valor_total
        text observacao
        datetime criado_em
    }

    ITENS_PEDIDO {
        int id PK
        int pedido_id FK
        int produto_id FK
        int quantidade
        decimal preco_unitario
    }

    PAGAMENTOS {
        int id PK
        int pedido_id FK
        string metodo
        string status
        decimal valor
        datetime criado_em
    }

    FIDELIDADE {
        int id PK
        int usuario_id FK,UK
        int pontos
        datetime atualizado_em
    }

    AUDITORIA {
        int id PK
        int usuario_id FK
        string acao
        text detalhes
        datetime criado_em
    }

    PONTUACOES_PEDIDOS {
        int id PK
        int pedido_id FK,UK
        int usuario_id FK
        int pontos
        datetime criado_em
    }

    PROMOCOES {
        int id PK
        string nome
        text descricao
        int produto_id FK
        decimal percentual_desconto
        datetime data_inicio
        datetime data_fim
        boolean ativa
        datetime criada_em
    }

    USUARIOS ||--o{ PEDIDOS : realiza
    UNIDADES ||--o{ PEDIDOS : recebe
    UNIDADES ||--o{ ESTOQUES : possui
    PRODUTOS ||--o{ ESTOQUES : compoe
    PEDIDOS ||--o{ ITENS_PEDIDO : contem
    PRODUTOS ||--o{ ITENS_PEDIDO : integra
    PEDIDOS ||--o{ PAGAMENTOS : possui
    USUARIOS ||--o| FIDELIDADE : participa
    USUARIOS |o--o{ AUDITORIA : gera
    USUARIOS ||--o{ PONTUACOES_PEDIDOS : recebe
    PEDIDOS ||--o| PONTUACOES_PEDIDOS : gera
    PRODUTOS ||--o{ PROMOCOES : participa
```

## Legenda

- **PK:** chave primária.
- **FK:** chave estrangeira.
- **UK:** restrição de unicidade.
- **1:N:** um registro pode estar associado a vários registros.
- **1:0..1:** um registro pode estar associado a zero ou um registro.
- **0..1:N:** relacionamento com participação opcional de um dos lados.

## Observações sobre o modelo

1. Um usuário pode realizar vários pedidos.
2. Uma unidade pode receber vários pedidos e possuir vários registros de estoque.
3. Um produto pode aparecer em diferentes registros de estoque e itens de pedidos.
4. Um pedido pode conter vários itens.
5. O campo `usuario_id` em `auditoria` é opcional.
6. O campo `usuario_id` em `fidelidade` possui restrição de unicidade.
7. O campo `pedido_id` em `pontuacoes_pedidos` possui restrição de unicidade.
8. O relacionamento entre pedido e pagamento está configurado como um para um no ORM (`uselist=False`), mas o campo `pagamentos.pedido_id` não possui restrição `unique=True` no modelo apresentado. Portanto, essa cardinalidade ainda não é garantida pelo banco de dados.

## Fonte

Diagrama elaborado a partir do código-fonte `app/models.py` do projeto Raízes do Nordeste.