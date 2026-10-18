
import json
import logging
import os

import pika


logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))

EXCHANGE_NAME = "estagios"
ROUTING_KEY = "candidatura.criada"


def publicar_evento(evento):
    conexao = None

    try:
        parametros = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            connection_attempts=1,
            socket_timeout=3,
        )

        conexao = pika.BlockingConnection(parametros)
        canal = conexao.channel()

        canal.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="fanout",
            durable=True,
        )

        canal.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=json.dumps(evento),
        )

        logger.info(
            "Evento publicado no RabbitMQ: %s",
            evento.get("tipo"),
        )

    except (pika.exceptions.AMQPError, OSError, ValueError):
        logger.exception(
            "RabbitMQ indisponível. "
            "O evento não foi publicado: %s",
            evento.get("tipo"),
        )

    finally:
        if conexao is not None and conexao.is_open:
            try:
                conexao.close()
            except pika.exceptions.AMQPError:
                logger.exception(
                    "Não foi possível fechar a conexão RabbitMQ."
                )
