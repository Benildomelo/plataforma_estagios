from decimal import Decimal, InvalidOperation

from django.utils import timezone

from ..models import Curso
from ..repositories.vaga_repository import VagaRepository


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
        cursos_ids,
    ):
        if not titulo:
            raise ValueError(
                "O título da vaga é obrigatório."
            )

        if not descricao:
            raise ValueError(
                "A descrição da vaga é obrigatória."
            )

        if not local:
            raise ValueError(
                "O local da vaga é obrigatório."
            )

        if not carga_horaria:
            raise ValueError(
                "A carga horária é obrigatória."
            )

        # Remove valores vazios e IDs repetidos.
        cursos_ids = list(dict.fromkeys(
            str(curso_id).strip()
            for curso_id in cursos_ids
            if str(curso_id).strip()
        ))

        if not cursos_ids:
            raise ValueError(
                "Selecione pelo menos um curso."
            )

        # Valida os IDs dos cursos.
        try:
            cursos_ids = [
                int(curso_id)
                for curso_id in cursos_ids
            ]
        except (TypeError, ValueError):
            raise ValueError(
                "Um ou mais cursos selecionados são inválidos."
            )

        cursos = list(
            Curso.objects.filter(
                id__in=cursos_ids,
                ativo=True
            )
        )

        if len(cursos) != len(cursos_ids):
            raise ValueError(
                "Um ou mais cursos não existem ou estão inativos."
            )

        # Valida o valor da bolsa.
        if bolsa:
            try:
                bolsa = Decimal(
                    str(bolsa).replace(',', '.')
                )
            except (InvalidOperation, ValueError):
                raise ValueError(
                    "Informe um valor válido para a bolsa."
                )

            if not bolsa.is_finite() or bolsa < 0:
                raise ValueError(
                    "A bolsa deve ser um valor igual ou superior a zero."
                )
        else:
            bolsa = None

        # Cria a vaga já publicada para os alunos.
        return VagaRepository.criar_com_cursos(
            empresa=empresa,
            titulo=titulo,
            descricao=descricao,
            requisitos=requisitos,
            local=local,
            carga_horaria=carga_horaria,
            bolsa=bolsa,
            cursos=cursos,
            status="APROVADA",
            data_publicacao=timezone.now(),
            ativo=True,
        )

    @staticmethod
    def encerrar_vaga(vaga, empresa):
        if vaga.empresa != empresa:
            raise ValueError(
                "Você não pode encerrar esta vaga."
            )

        if not vaga.ativo:
            raise ValueError(
                "Esta vaga já está encerrada."
            )

        return VagaRepository.encerrar(vaga)
