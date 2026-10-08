from dataclasses import dataclass
from typing import Optional


@dataclass
class CandidaturaRequestDTO:
    aluno_id: int
    vaga_id: int


@dataclass
class CandidaturaResponseDTO:
    id: int
    aluno_id: int
    vaga_id: int
    status: str
    observacao: Optional[str] = None