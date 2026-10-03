from django.core.management.base import BaseCommand
from vagas.models import Curso


class Command(BaseCommand):
    help = 'Cadastra cursos padrão no sistema'

    def handle(self, *args, **options):
        cursos = [
            'Ciência da Computação',
            'Sistemas de Informação',
            'Engenharia de Software',
            'Análise e Desenvolvimento de Sistemas',
            'Administração',
            'Ciências Contábeis',
            'Direito',
            'Enfermagem',
            'Farmácia',
            'Fisioterapia',
            'Nutrição',
            'Psicologia',
            'Engenharia Civil',
            'Engenharia Elétrica',
            'Engenharia Mecânica',
            'Arquitetura e Urbanismo',
            'Pedagogia',
            'Educação Física',
            'Serviço Social',
            'Marketing',
        ]

        cadastrados = 0
        existentes = 0

        for nome in cursos:
            curso, criado = Curso.objects.get_or_create(
                nome=nome,
                defaults={'ativo': True}
            )

            if criado:
                cadastrados += 1
            else:
                existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Concluído! {cadastrados} cursos cadastrados e '
                f'{existentes} já existiam.'
            )
        )