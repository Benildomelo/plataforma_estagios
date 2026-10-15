import json
import pika


RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672

EXCHANGE_NAME = "estagios"
ROUTING_KEY = "candidatura.criada"


def publicar_evento(evento):
    conexao = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT
        )
    )

    canal = conexao.channel()

    canal.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="fanout",
        durable=True
    )

    canal.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=json.dumps(evento)
    )

    conexao.close()