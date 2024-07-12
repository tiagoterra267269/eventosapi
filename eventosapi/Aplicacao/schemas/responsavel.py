from typing import Optional, List
from model.entidades import Responsavel
from pydantic import BaseModel
from datetime import datetime

class ExcluirSchema(BaseModel):
    " Contém o id a ser usado como parâmetro para exclusão "
    id: int = 1

class ResponsavelSchema(BaseModel):
    """ Define um novo responsavel a ser inserido na base
    """
    nome: str = "Jane Doe"
    email: str = "janedoe@email.com"
    cpf: str = "11122233344"
    matricula: str = "00000001"
    eventoId: int = 1
    id: int = 1

class ResponsavelViewSchema(BaseModel):
    """ Define o responsavel retornado
    """
    nome: str = "Jane Doe"
    email: str = "janedoe@email.com"
    cpf: str = "11122233344"
    matricula: str = "00000001"
    id: int = 1

class ListagemResponsavelsSchema(BaseModel):
    """ Define como uma listagem de responsavels será retornada.
    """
    responsavels:List[ResponsavelViewSchema]

class SearchResponsavelSchema(BaseModel):
    eventoid: int

def mapeaentidade_paraschemaresponsavel(responsavel: Responsavel):
    """ Mapea a entiedade Responsavel para schema de Responsavel

    Retorna ums lista de EventosSchema
    """
    return {
        "nome": responsavel.nome,
        "matricula": responsavel.matricula,
        "id": responsavel.id,
        "cpf": responsavel.cpf,
        "email": responsavel.email
    }

    return {"eventos": result}

def mapeaentidade_paraschemaresponsaveis(responsavels: List[Responsavel]):
    """ Mapea uma lista de entidade Responsavel para lista de ResponsavelsSchema

    Retorna uma lista de ResponsavelsSchema
    """
    result = []
    for responsavel in responsavels:
        result.append({
            "nome": responsavel.nome,
            "matricula": responsavel.matricula,
            "id": responsavel.id,
            "cpf": responsavel.cpf,
            "email": responsavel.email
        })

    return {"responsavels": result}