from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.vaga_repository import VagaRepository
from ..clients.microservico_client import validar_vaga


class CandidaturaService:

    @staticmethod
    def candidatar(aluno, vaga_id):

        vaga = VagaRepository.buscar_por_id(vaga_id)

        if not vaga:
            raise ValueError("Vaga não encontrada.")

        if vaga.status != "APROVADA":
            raise ValueError("Esta vaga não está disponível para candidatura.")

        if not vaga.ativo:
            raise ValueError("Esta vaga está inativa.")

        # Comunicação síncrona com o microserviço
        validacao = validar_vaga(vaga.id)

        if not validacao.get("valida"):
            raise ValueError("A vaga foi rejeitada pelo microserviço.")

        candidatura_existente = (
            CandidaturaRepository.buscar_por_aluno_e_vaga(aluno, vaga)
        )

        if candidatura_existente:
            return candidatura_existente, False

        candidatura = CandidaturaRepository.criar(
            aluno=aluno,
            vaga=vaga
        )

        return candidatura, True