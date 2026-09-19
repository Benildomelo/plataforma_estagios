from .publicas import (
    inicio,
    lista_vagas,
    detalhe_vaga,
)

from .autenticacao import (
    entrar,
    entrar_aluno,
    entrar_empresa,
    trocar_senha_empresa,
    sair,
)

from .aluno import (
    minhas_candidaturas,
    area_aluno,
    cadastro_aluno,
    perfil_aluno,
    curriculo_aluno,
    editar_perfil_aluno,
)

from .empresa import (
    area_empresa,
    detalhe_vaga_empresa,
    atualizar_candidatura,
    perfil_empresa,
)

from .vagas import (
    candidatar,
    criar_vaga,
    editar_vaga,
    encerrar_vaga,
)