from django.db import models
from django.contrib.auth.models import User


class Curso(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Aluno(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=150)
    matricula = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    
class Empresa(models.Model):
    id = models.BigAutoField(primary_key=True)
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=250, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_fantasia    

class Vaga(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
        ('ENCERRADA', 'Encerrada'),
    ]

    id = models.BigAutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    requisitos = models.TextField(blank=True)
    bolsa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    carga_horaria = models.CharField(max_length=50)
    local = models.CharField(max_length=200)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )
    data_publicacao = models.DateTimeField(null=True, blank=True)
    data_encerramento = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo    

class Candidatura(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANALISE', 'Em análise'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
        ('CANCELADA', 'Cancelada'),
    ]

    id = models.BigAutoField(primary_key=True)
    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT)
    vaga = models.ForeignKey(Vaga, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )
    data_candidatura = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'vaga'],
                name='candidatura_unica_aluno_vaga'
            )
        ]

    def __str__(self):
        return f'{self.aluno} - {self.vaga}'