from ..repositories.vaga_repository import VagaRepository
from ..repositories.curso_repository import CursoRepository


class VagaService:

    @staticmethod
    def criar_vaga(
        empresa,
        titulo,
        descricao,
        requisitos,
        local,
        carga_horaria,
        bolsa,
        curso_id
    ):
        curso = CursoRepository.buscar_por_id(curso_id)

        if not curso:
            raise ValueError("Curso não encontrado.")

        if not curso.ativo:
            raise ValueError("O curso selecionado está inativo.")

        if not titulo:
            raise ValueError("O título da vaga é obrigatório.")

        if not descricao:
            raise ValueError("A descrição da vaga é obrigatória.")

        return VagaRepository.criar(
            empresa=empresa,
            titulo=titulo,
            descricao=descricao,
            requisitos=requisitos,
            local=local,
            carga_horaria=carga_horaria,
            bolsa=bolsa or None,
            curso=curso,
            status="PENDENTE",
            ativo=True
        )

    @staticmethod
    def encerrar_vaga(vaga, empresa):
        if vaga.empresa != empresa:
            raise ValueError("Você não pode encerrar esta vaga.")

        if not vaga.ativo:
            raise ValueError("Esta vaga já está encerrada.")

        return VagaRepository.encerrar(vaga)