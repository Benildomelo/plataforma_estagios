@'
# UNIPI Conecta — Plataforma de Estágios

## Descrição
Projeto acadêmico para gerenciamento de vagas e candidaturas de estágio, desenvolvido em Django, com comunicação assíncrona utilizando RabbitMQ e um microserviço em FastAPI.

## Tecnologias
- Python e Django
- RabbitMQ e Pika
- FastAPI e Uvicorn
- HTTPX
- Git e GitHub

## Arquitetura da comunicação assíncrona
1. O aluno solicita uma candidatura.
2. O serviço Django valida a vaga por meio do microserviço FastAPI.
3. A candidatura é registrada no banco de dados.
4. Após a confirmação da transação, o produtor publica um evento `candidatura.criada` no exchange `estagios`.
5. O RabbitMQ distribui o evento usando o padrão Publish/Subscribe com exchange do tipo `fanout`.
6. O consumidor escuta a fila `candidaturas`, desserializa o evento e encaminha os dados ao serviço de processamento.
7. O consumidor confirma mensagens processadas e rejeita eventos inválidos.

## Pré-requisitos
- Python
- RabbitMQ
- Erlang, necessário para executar o RabbitMQ
- Ambiente virtual Python

## Instalação
Clone o repositório e acesse a pasta do projeto.

Crie e ative um ambiente virtual:

```bash
python -m venv venv
