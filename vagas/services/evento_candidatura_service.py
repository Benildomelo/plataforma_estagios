
import logging

logger = logging.getLogger(__name__)


class EventoCandidaturaService:

    @staticmethod
    def processar(evento):
        if evento.get("tipo") != "candidatura.criada":
            raise ValueError("Tipo de evento não reconhecido.")

        campos_obrigatorios = [
            "candidatura_id",
            "aluno_id",
            "vaga_id",
            "status",
        ]

        for campo in campos_obrigatorios:
            if campo not in evento:
                raise ValueError(
                    f"Evento sem o campo obrigatório: {campo}"
                )

        logger.info(
            "Candidatura processada: ID=%s, aluno=%s, vaga=%s, status=%s",
            evento["candidatura_id"],
            evento["aluno_id"],
            evento["vaga_id"],
            evento["status"],
        )

        print(
            f"Candidatura {evento['candidatura_id']} processada "
            f"para o aluno {evento['aluno_id']}, "
            f"vaga {evento['vaga_id']}."
        )
