
import json
import pika

from ..services.evento_candidatura_service import (
    EventoCandidaturaService,
)


RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672

EXCHANGE_NAME = "estagios"
QUEUE_NAME = "candidaturas"


def processar_evento(ch, method, properties, body):
    try:
        evento = json.loads(body)

        EventoCandidaturaService.processar(evento)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except (ValueError, json.JSONDecodeError) as erro:
        print(f"Erro ao processar evento: {erro}")

        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )


def iniciar_consumidor():
    conexao = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
        )
    )

    canal = conexao.channel()

    canal.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="fanout",
        durable=True,
    )

    canal.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    canal.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
    )

    canal.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=processar_evento,
    )

    print("Consumidor aguardando eventos...")

    try:
        canal.start_consuming()
    finally:
        if conexao.is_open:
            conexao.close()


if __name__ == "__main__":
    iniciar_consumidor()
