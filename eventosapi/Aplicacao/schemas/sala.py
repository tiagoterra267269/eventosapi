from typing import Optional, List
from model.entidades import Sala
from pydantic import BaseModel
from datetime import datetime

class SalaViewSchema(BaseModel):
    """ Define a sala retornada
    """
    id: int = 1
    nome: str = "Sala 1"

class ListagemSalasSchema(BaseModel):
    """ Define como uma listagem de salas será retornada.
    """
    salas:List[SalaViewSchema]

def mapeaentidade_paraschemasala(salas: List[Sala]):
    """ Mapea uma lista de entidade Sala para umalista de SalasSchema

    Retorna uma lista de SalasSchema
    """
    result = []
    for sala in salas:
        result.append({
            "nome": sala.nome,
            "id": sala.id
        })

    return {"salas": result}