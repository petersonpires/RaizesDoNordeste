# Arquitetura do Sistema — Raízes do Nordeste

## 1. Visão geral

O Raízes do Nordeste é um sistema de gerenciamento de uma rede de lanchonetes, desenvolvido em Python com o framework FastAPI.

A aplicação disponibiliza uma API REST para autenticação, gerenciamento de unidades, produtos, estoque, pedidos, pagamentos, fidelidade, promoções e consultas administrativas.

## 2. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem de programação |
| FastAPI | Desenvolvimento da API REST |
| Uvicorn | Servidor de execução da aplicação |
| SQLAlchemy | Mapeamento objeto-relacional e acesso ao banco |
| Pydantic | Validação dos dados de entrada e saída |
| SQLite | Persistência dos dados |
| JWT | Autenticação baseada em tokens |
| Swagger UI | Documentação interativa da API |
| Postman | Execução dos testes da API |

## 3. Organização em camadas

A arquitetura do sistema é organizada por responsabilidades.

### 3.1. Camada de apresentação — API

Responsável por receber as requisições HTTP, validar parâmetros, acionar as operações e devolver respostas.

Os endpoints são disponibilizados por meio do FastAPI.

Exemplos:

- `/auth`
- `/unidades`
- `/produtos`
- `/estoque`
- `/pedidos`
- `/pagamentos`

### 3.2. Camada de aplicação

Responsável por coordenar as operações do sistema, como confirmar pedidos, atualizar seus status, registrar pagamentos e executar regras relacionadas ao estoque.

Na implementação atual, parte dessa lógica está diretamente nas funções dos endpoints. A separação em serviços independentes poderá ser realizada em uma evolução futura.

### 3.3. Camada de domínio

Representa as entidades e as regras de negócio.

As principais entidades são:

- Usuario
- Unidade
- Produto
- Estoque
- Pedido
- ItemPedido
- Pagamento
- Fidelidade
- Auditoria

### 3.4. Camada de infraestrutura

Responsável pela comunicação com o banco de dados e pelos recursos técnicos utilizados pela aplicação.

O SQLAlchemy realiza o mapeamento das entidades e o acesso aos registros persistidos no SQLite.

## 4. Fluxo de uma requisição

1. O cliente envia uma requisição HTTP.
2. O FastAPI identifica o endpoint correspondente.
3. Quando necessário, o sistema verifica o token JWT e as permissões.
4. Os dados recebidos são validados.
5. A operação consulta ou modifica as entidades por meio do SQLAlchemy.
6. O banco de dados registra as alterações.
7. A API devolve uma resposta JSON com o código HTTP correspondente.

## 5. Fluxo de confirmação e cancelamento de pedidos

Na confirmação de um pedido:

1. O sistema identifica o pedido.
2. Verifica se o pedido pode ser confirmado.
3. Confere a disponibilidade dos produtos em estoque.
4. Desconta as quantidades necessárias.
5. Atualiza o status do pedido.
6. Persiste as alterações.

No cancelamento de um pedido confirmado, quando permitido pelas regras de negócio:

1. O sistema identifica o pedido.
2. Verifica se o cancelamento é permitido.
3. Devolve as quantidades dos itens ao estoque.
4. Atualiza o status do pedido para CANCELADO.
5. Persiste as alterações.

## 6. Segurança

O sistema utiliza autenticação JWT e controle de permissões para proteger operações que exigem identificação do usuário.

As senhas são armazenadas em formato de hash, e não em texto simples.

O cadastro público atribui o perfil CLIENTE, impedindo que usuários obtenham privilégios administrativos por meio do cadastro comum.

## 7. Documentação e testes

A documentação interativa da API está disponível em:

`http://127.0.0.1:8000/docs`

A coleção de testes automatizados está armazenada na pasta `postman` do projeto.

Na execução registrada em 31 de outubro de 2026, foram aprovadas 14 verificações automáticas, sem falhas.

## 8. Considerações finais

A arquitetura adotada permite organizar os recursos da API e persistir os dados das operações da rede de lanchonetes.

Como possibilidade de evolução, as regras de negócio atualmente presentes nos endpoints poderão ser transferidas para serviços específicos, ampliando a separação entre as camadas.