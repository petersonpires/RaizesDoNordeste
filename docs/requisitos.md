# Requisitos do Sistema — Raízes do Nordeste

## 1. Apresentação

O sistema Raízes do Nordeste é uma API desenvolvida em Python com FastAPI para gerenciar operações de uma rede de lanchonetes, incluindo usuários, unidades, produtos, pedidos, estoque, pagamentos e programas de fidelidade.

## 2. Requisitos funcionais

| Código | Requisito | Prioridade |
|---|---|---|
| RF01 | Permitir o cadastro e a autenticação de usuários com JWT. | Alta |
| RF02 | Controlar permissões conforme o perfil do usuário. | Alta |
| RF03 | Permitir o cadastro e a consulta de unidades da rede. | Alta |
| RF04 | Permitir o cadastro e a consulta de produtos do cardápio. | Alta |
| RF05 | Permitir a criação e a consulta de pedidos. | Alta |
| RF06 | Registrar o canal de origem dos pedidos: APP, TOTEM, BALCAO, PICKUP ou WEB. | Alta |
| RF07 | Permitir filtrar pedidos pelo canal de origem. | Alta |
| RF08 | Permitir confirmar pedidos e atualizar seu status. | Alta |
| RF09 | Permitir cancelar pedidos conforme as regras de negócio. | Alta |
| RF10 | Controlar o estoque dos produtos por unidade. | Alta |
| RF11 | Descontar o estoque na confirmação e devolver os itens em cancelamentos permitidos. | Alta |
| RF12 | Registrar pagamentos por meio de uma integração simulada. | Alta |
| RF13 | Permitir a participação no programa de fidelidade mediante consentimento. | Média |
| RF14 | Aplicar regras de promoções e descontos. | Média |
| RF15 | Disponibilizar consultas e relatórios administrativos. | Média |
| RF16 | Registrar eventos relevantes para auditoria. | Alta |

## 3. Requisitos não funcionais

| Código | Requisito | Prioridade |
|---|---|---|
| RNF01 | Utilizar uma arquitetura organizada em camadas. | Alta |
| RNF02 | Disponibilizar endpoints HTTP com dados em JSON. | Alta |
| RNF03 | Documentar a API utilizando OpenAPI/Swagger. | Alta |
| RNF04 | Armazenar senhas utilizando hash seguro. | Alta |
| RNF05 | Proteger endpoints que exigem autenticação e autorização. | Alta |
| RNF06 | Considerar os princípios da LGPD no tratamento dos dados pessoais. | Alta |
| RNF07 | Persistir os dados em banco de dados relacional. | Alta |
| RNF08 | Retornar códigos HTTP adequados e mensagens de erro compreensíveis. | Alta |
| RNF09 | Disponibilizar testes executáveis em coleção Postman. | Alta |
| RNF10 | Manter documentação para instalação e execução do projeto. | Alta |

## 4. Regras de negócio

- O cadastro público deve criar usuários com perfil CLIENTE.
- Operações administrativas devem exigir autorização apropriada.
- O pedido deve estar confirmado antes do registro do pagamento.
- A confirmação de pedidos deve respeitar a disponibilidade de estoque.
- O cancelamento deve respeitar o status do pedido.
- Um pedido já cancelado não pode ser cancelado novamente.
- Um canal de pedido inválido deve ser rejeitado.
- A participação na fidelidade deve respeitar o consentimento do usuário.

## 5. Tecnologias utilizadas

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT
- SQLite
- Swagger UI
- Postman

## 6. Evidências de testes

A coleção Postman foi executada com os seguintes resultados:

- 12 requisições executadas.
- 14 verificações automatizadas aprovadas.
- 0 verificações reprovadas.
- 0 erros de execução.

Foram verificados cenários positivos e negativos, incluindo autenticação, consulta de recursos, filtragem de pedidos, rejeição de canais inválidos, pedidos inexistentes e bloqueio de cancelamento duplicado.

## 7. Observações

Este documento apresenta os requisitos identificados para o projeto. A implementação e a cobertura de cada requisito deverão ser verificadas na documentação técnica e nos testes antes da entrega final.