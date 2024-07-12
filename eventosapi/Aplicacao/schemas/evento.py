from typing import Optional, List
from model.entidades import Evento
from pydantic import BaseModel
from datetime import datetime

class SearchEventoSchema(BaseModel):
    " Contém o id a ser usado como parâmetros para buscas "
    id: int = 1

class EventoSchema(BaseModel):
    """ Representa um evento a ser adicionado ou atualizado 
    """
    nome: str = "1o Encontro de Estudos sobe autismo na infância"
    data_inicio: str
    status_evento_id: int = 1

class EventoViewSchema(BaseModel):
    """ Representa um evento existente na base
    """
    nome: str = "2o Encontro de Estudos sobe autismo na infância"
    data_inicio: str
    id: int = 1

class ListagemEventosSchema(BaseModel):
    """ Define como uma listagem de eventos (EventoSchema)
    """
    eventos:List[EventoViewSchema]

def mapeaentidades_paraschemaeventos(eventos: List[Evento]):
    """ Mapea uma lista de entidades Eventos para lista de EventosSchema

    Retorna ums lista de EventosSchema
    """
    result = []
    for evento in eventos:
        result.append({
            "nome": evento.nome,
            "data_inicio": evento.datainicio,
            "data_fim": evento.datafim,
            "id": evento.id
        })

    return {"eventos": result}

def mapeaentidade_paraschemaevento(evento: Evento):
    """ Mapea a entidade de evento para lista de EventosSchema

    Retorna ums lista de EventosSchema
    """
    return {
        "nome": evento.nome,
        "data_inicio": evento.datainicio,
        "data_fim": evento.datafim,
        "id": evento.id
    }