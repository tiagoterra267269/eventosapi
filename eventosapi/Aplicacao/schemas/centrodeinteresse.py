from typing import Optional, List
from model.entidades import CentroDeInteresse
from pydantic import BaseModel
from datetime import datetime

class ExcluirSchema(BaseModel):
    id: int = 1

class SearchCentroDeInteresseSchema(BaseModel):
    eventoId: int = 1 

class CentroDeInteresseSchema(BaseModel):
    """ Define um novo centro de interesse a ser inserido na base
    """
    tema: str = "Abordagens pedagógicas e o autismo infantil"
    salaId: int = 1
    responsavelId: int = 1
    id: int = 1

class CentroDeInteresseViewSchema(BaseModel):
    """ Define o centro de interesse retornado
    """
    tema: str = "Tecnologia e autismo"
    id: int = 1

class ListagemCentroDeInteressesSchema(BaseModel):
    """ Define como uma listagem de centro de interesses será retornada.
    """
    centrodeinteresses:List[CentroDeInteresseViewSchema]

class CentroDeInteressePorParticipanteViewSchema(BaseModel):
    """ Define o centro de interesse retornado
    """ 
    idcentrodeinteresse: int = 1
    tema: str = "tema"
    idparticipante: int = 0
    responsavel: str = "responsavel"

class ListagemCentroDeInteressePorParticipanteSchema(BaseModel):
    """ Define uma listagem de centros de interesse
    """
    centrodeinteresses:List[CentroDeInteressePorParticipanteViewSchema]

def mapeaentidade_paraschemacentrodeinteresse(centrodeinteresses: List[CentroDeInteresse]):
    """ Mapea uma lista de entidades CentroDeInteresses para lista de CentroDeInteressesSchema

    Retorna uma lista de CentroDeInteressesSchema
    """
    result = []
    for centrodeinteresse in centrodeinteresses:
        result.append({
            "tema": centrodeinteresse.tema,
            "responsavel": centrodeinteresse.nome_1,
            "sala": centrodeinteresse.nome,
            "id" :centrodeinteresse.id
        })

    return {"centrodeinteresses": result}

def mapeaentidade_paraumschemacentrodeinteresse(centrodeinteresse: CentroDeInteresse):
    """ Mapea a entidade centro de interesse para schema de centro de interesse

    Retorna um schema de centro de interesse
    """
    return {
        "tema": centrodeinteresse.tema,
        "id" :centrodeinteresse.id
    }

def mapeaentidade_paraschemacentrodeinteresseporparticipante(
    centrodeinteresses: List[CentroDeInteresse]):
    """ Mapea uma lista de entidades CentroDeInteresses para lista 
        de CentroDeInteressesSchema
    Retorna uma lista de CentroDeInteressesSchema
    """
    result = []
    for centrodeinteresse in centrodeinteresses:
        result.append({
            "idcentrodeinteresse": centrodeinteresse.CentroDeInteresse.id,
            "tema": centrodeinteresse.CentroDeInteresse.tema,
            "idparticipante": centrodeinteresse.Participante.id if centrodeinteresse.Participante else 0,
            "responsavel": centrodeinteresse.Responsavel.nome
        })

    return {"centrodeinteresses": result}