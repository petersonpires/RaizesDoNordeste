# Diagrama de Classes — Raízes do Nordeste

## 1. Apresentação

Este diagrama representa as principais classes de persistência do sistema Raízes do Nordeste, conforme definidas no arquivo `app/models.py`.

As classes correspondem às entidades gerenciadas pelo SQLAlchemy.

## 2. Diagrama de classes

```mermaid
classDiagram
    direction TB

    class Usuario {
        +Integer id
        +String nome
        +String email
        +String senha_hash
        +String perfil
        +Boolean ativo
        +Boolean consentimento_fidelidade
        +DateTime criado_em
    }

    class Unidade {
        +Integer id
        +String nome
        +String endereco
        +String telefone
        +Boolean ativa
        +DateTime criada_em
    }

    class Produto {
        +Integer id
        +String nome
        +Text descricao
        +Decimal preco
        +String categoria
        +Boolean ativo
        +DateTime criado_em
    }

    class Estoque {
        +Integer id
        +Integer unidade_id
        +Integer produto_id
        +Integer quantidade
    }

    class Pedido {
        +Integer id
        +Integer usuario_id
        +Integer unidade_id
        +String status
        +String canal_pedido
        +Decimal valor_total
        +Text observacao
        +DateTime criado_em
    }

    class ItemPedido {
        +Integer id
        +Integer pedido_id
        +Integer produto_id
        +Integer quantidade
        +Decimal preco_unitario
    }

    class Pagamento {
        +Integer id
        +Integer pedido_id
        +String metodo
        +String status
        +Decimal valor
        +DateTime criado_em
    }

    class Fidelidade {
        +Integer id
        +Integer usuario_id
        +Integer pontos
        +DateTime atualizado_em
    }

    class Auditoria {
        +Integer id
        +Integer usuario_id
        +String acao
        +Text detalhes
        +DateTime criado_em
    }

    class PontuacaoPedido {
        +Integer id
        +Integer pedido_id
        +Integer usuario_id
        +Integer pontos
        +DateTime criado_em
    }

    class Promocao {
        +Integer id
        +String nome
        +Text descricao
        +Integer produto_id
        +Decimal percentual_desconto
        +DateTime data_inicio
        +DateTime data_fim
        +Boolean ativa
        +DateTime criada_em
    }

    Usuario "1" --> "0..*" Pedido : realiza
    Unidade "1" --> "0..*" Pedido : recebe
    Unidade "1" --> "0..*" Estoque : possui
    Produto "1" --> "0..*" Estoque : compoe
    Pedido "1" --> "0..*" ItemPedido : contem
    Produto "1" --> "0..*" ItemPedido : integra
    Pedido "1" --> "0..1" Pagamento : pagamento
    Usuario "1" --> "0..1" Fidelidade : fidelidade
    Usuario "0..1" --> "0..*" Auditoria : auditoria
    Usuario "1" --> "0..*" PontuacaoPedido : pontuacoes
    Pedido "1" --> "0..1" PontuacaoPedido : pontuacao
    Produto "1" --> "0..*" Promocao : promocoes
```

## 3. Descrição das classes

| Classe | Responsabilidade |
|---|---|
| Usuario | Armazenar os dados dos usuários e seus perfis de acesso. |
| Unidade | Representar as unidades da rede de lanchonetes. |
| Produto | Armazenar os produtos do cardápio. |
| Estoque | Controlar a quantidade de cada produto em uma unidade. |
| Pedido | Registrar os pedidos realizados pelos usuários. |
| ItemPedido | Representar os produtos e quantidades de um pedido. |
| Pagamento | Registrar os pagamentos associados aos pedidos. |
| Fidelidade | Armazenar os pontos de fidelidade do usuário. |
| Auditoria | Registrar eventos relevantes para rastreabilidade. |
| PontuacaoPedido | Registrar os pontos atribuídos a um pedido. |
| Promocao | Armazenar regras de desconto vinculadas a produtos. |

## 4. Observações

- As classes representam o modelo de persistência, não todas as funções da aplicação.
- Os relacionamentos foram identificados a partir das chaves estrangeiras e das declarações `relationship` existentes no código.
- A relação entre Pedido e Pagamento é representada como um para zero ou um na aplicação, mas a unicidade não está garantida por uma restrição explícita no banco de dados.
- O diagrama será convertido em formato visual e incluído no relatório final em PDF.

## 5. Fonte

Diagrama elaborado a partir do arquivo `app/models.py` do projeto Raízes do Nordeste.