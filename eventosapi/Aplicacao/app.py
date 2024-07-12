from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request
from urllib.parse import unquote
import logging
import re
import jwt
from datetime import datetime


# basic do logging
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

from sqlalchemy.exc import IntegrityError
from model import Session, StatusEvento, Responsavel, Sala, Evento, CentroDeInteresse, Participante
from schemas import *
from schemas import EventoSchema
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, Table, MetaData, select 
from typing import Optional, List

info = Info(title="Eventos API", version="1.0.0",
    description="Serviço que permite a manutenção de eventos (workshops, encontros de estudo)")
app = OpenAPI(__name__, info=info)

CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")

evento_tag = Tag(name="Evento", description=""" Endpoints de suporte à manutenção de eventos: os eventos
    funcionam como encontros de estudos que podem ter um ou mais centros de interesse que serão elaborados
    e presididos por um determinado responsável e terá seus participantes atrelados.
    """)

responsavel_tag = Tag(name="Responsável", description="""Endpoints de suporte à responsável: os resposáveis
    presidirão os centros de intersse do evento nos quais os participantes vão dedicir de associam ou não.
    """)

centrodeinteresse_tag = Tag(name="Centro de Interesse", description="""Endpoints de Centros de Interesse:
    são os temas que serão desenvolvidos pelos responsáveis no evento.
    """)

sala_tag = Tag(name="Sala", description="""Sala física, representando o espaço físico onde o centro de
    interesse será desenvolvido e onde os participantes serão recebidos.
    """)

participante_tag = Tag(name="Participante", description="""Participantes do Evento: os participantes
    do evento poderão estar inscrito em um ou mais centros de interesse.
    """)

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


def token_required(f):
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'Token is missing'}, 403

        try:
            token = token.replace("Bearer ","")

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 403
        except jwt.InvalidTokenError as e:
            logging.debug('exception')
            logging.debug(e)
            return {'message': 'Token is invalid'}, 403

        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap


# ========================================================================================================
# Endpoints de eventos
# ========================================================================================================
@app.get('/evento', tags=[evento_tag],
        responses={"200": ListagemEventosSchema, "404": ErrorSchema})
def get_evento():
    """ Consulta todos os eventos da base de dados
    Retorna um modelo representando uma lista de eventos
    """
    try:
        session = Session()
        logging.debug("Consulta todos os eventos")
        eventos = session.query(Evento).filter(Evento.ativo == 1)

        return mapeaentidades_paraschemaeventos(eventos), 200
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os eventos {e}")
        return {"message": error_msg}, 500

@app.get('/eventoporid', tags=[evento_tag],
        responses={"200": ListagemEventosSchema, "404": ErrorSchema})
def get_evento_by_id(query: SearchEventoSchema):
    """ Consulta um evento por id
    Retorna o evento quando existente na base de dados
    """
    try:
        session = Session()
        logging.debug("Consulta todos os eventos")
        evento = session.query(Evento).filter(
            Evento.ativo == 1,
            Evento.id == query.id).first()

        return mapeaentidade_paraschemaevento(evento), 200
    except Exception as e:
        # caso um erro fora do previsto
        #alert("Erro ao consultar")
        logging.warning(f"Erro ao consultar os eventos {e}")
        return {"message": error_msg}, 500

@app.post('/evento', tags=[evento_tag],responses={"200": 
    EventoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_evento(form: EventoSchema):
    """ Adiciona um novo Evento à base de dados
    Retorna o evento adicioado
    """    

    evento = Evento(
        nome=form.nome,
        data_inicio=trataData(form.data_inicio),
        data_fim=trataData(form.data_inicio))
    logging.debug(f"Adicionando evento de nome: '{evento.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando evento
        session.add(evento)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logging.debug(f"Adicionado evento de nome: '{evento.nome}'")

        return mapeaentidade_paraschemaevento(evento), 200
        # return apresenta_evento(evento), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "Evento de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao adicionar evento '{evento.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(f"Erro ao adicionar evento '{evento.nome}', {error_msg}")
        return {"message": error_msg}, 400

@app.post('/atualizarevento', tags=[evento_tag],responses={"200": 
    EventoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def update_evento(form: EventoViewSchema):
    """ Atualiza os dados básicos de um evento
    Retorna um evento atualizado
    """    
    try:
        # criando conexão com a base
        session = Session()
        
        evento = session.query(Evento).filter(Evento.id == form.id).first()

        evento.update(form.nome, form.data_inicio)

        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logging.debug(f"Atualizo o evento de nome: '{evento.nome}'")

        return mapeaentidade_paraschemaevento(evento), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "Evento de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao adicionar evento '{evento.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(f"Erro ao adicionar evento '{evento.nome}', {error_msg}")
        return {"message": error_msg}, 400

def trataData(data_str: str) -> datetime:
    try:
        data_formatada = datetime.strptime(data_str, "%Y-%m-%d")
        return data_formatada
    except ValueError:
        # Se a conversão falhar, trata o erro ou retorna None
        raise ValueError("Formato de data inválido. Use o formato dd/MM/yyyy.")

@app.delete('/evento', tags=[evento_tag],responses={"200": EventoViewSchema, "409": 
    ErrorSchema, "400": ErrorSchema})
def delete_evento(form: ExcluirSchema):
    """Remove um evento pelo id
    Retorna o evento excluído
    """
    try:
        logging.debug(f"Excluindoo  evento de id: '{form.id}'")
        # criando conexão com a base
        session = Session()

        eventoparaexclusao = session.query(Evento).filter(
            Evento.ativo == 1, Evento.id == form.id).first()
        
        logging.debug(f"Obtem centro de interesse para exclusão : '{eventoparaexclusao.nome}'")
        
        # exclui o responsavel: nossa exclusao é lógica para garantir rastreabilidade
        eventoparaexclusao.ativo = 0

        # efetivando o comando de adição de novo item na tabela
        session.commit()

        return mapeaentidade_paraschemaevento(eventoparaexclusao), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "Evento de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao excluir evento '{form.id}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível excluir novo item :/"
        logging.warning(f"Erro ao excluir evento '{form.id}', {error_msg}")
        return {"message": error_msg}, 400

# ========================================================================================================
# Endpoints de responsáveis 
# ========================================================================================================
@app.post('/responsavel', tags=[responsavel_tag],responses={"200": ResponsavelViewSchema, "409": 
    ErrorSchema, "400": ErrorSchema})
def add_responsavel(form: ResponsavelSchema):
    """Adiciona um novo Responsavel à base de dados
    Retorna o responsável adicionado
    """    
    try:
        responsavel = Responsavel(
            matricula=form.matricula,
            idevento=form.eventoId,
            nome=form.nome,
            email=form.email,
            cpf=form.cpf)

        logging.debug(f"Adicionando responsavel de nome: '{responsavel.nome}'")
        # criando conexão com a base
        session = Session()

        if session.query(Responsavel).filter(
            Responsavel.matricula == responsavel.matricula, 
            Responsavel.idevento == responsavel.idevento,
            Responsavel.ativo == 1).first() != None:
            return {"message": "Já existe um responsável cadastrado com essa matricula!"}, 400

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',responsavel.email):
            return {"message": "Formato de e-mail inválido!"}, 400
        elif session.query(Responsavel).filter(
            Responsavel.email == responsavel.email, 
            Responsavel.idevento == responsavel.idevento,
            Responsavel.ativo == 1).first() != None:
            return {"message": "Já existe um responsável cadastrado com esse e-mail"}, 400

        # adicionando responsavel
        session.add(responsavel)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logging.debug(f"Adicionado responsavel de nome: '{responsavel.nome}'")
        return mapeaentidade_paraschemaresponsavel(responsavel), 200
        # return apresenta_responsavel(responsavel), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "Responsavel de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao adicionar responsavel '{responsavel.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(f"Erro ao adicionar responsavel '{responsavel.nome}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/responsavel', tags=[responsavel_tag], responses={"200": ListagemEventosSchema, "404": ErrorSchema})
def get_responsavel(query: SearchResponsavelSchema):
    """ Obtém todos os responsáveis de acordo com o evento
    Retorna uma lista de responsáveis de um evento
    """    
    try:
        session = Session()
        
        logging.debug("Consulta todos os responsavels")
        
        # obtém os responsáveis válidos
        responsavelsvalidos = session.query(Responsavel).filter(
            Responsavel.ativo == 1, Responsavel.idevento == query.eventoid)
        
        return mapeaentidade_paraschemaresponsaveis(responsavelsvalidos), 200
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os responsavels {e}")
        return {"message": error_msg}, 500

@app.delete('/responsavel', tags=[responsavel_tag],responses={"200": ResponsavelViewSchema, "409": 
    ErrorSchema, "400": ErrorSchema})
def delete_responsavel(form: ExcluirSchema):
    """Remove responsavel na base de dados
    Retorna o responsavel excluído
    """    
    try:
        logging.debug(f"Excluindoo  responsavel de id: '{form.id}'")
        # criando conexão com a base
        session = Session()

        # valida se existem centros de interesse cadastrados
        if session.query(CentroDeInteresse).filter(
            CentroDeInteresse.idResponsavel == form.id).count() > 0:
            return {"message": "Existem Centros de interesse vinculados a esse centro de interesse, necessário a exclusão!"}, 400

        # obtém responsável para exclusão
        responsavelparaexclusao = session.query(Responsavel).filter(
            Responsavel.ativo == 1, 
            Responsavel.id == form.id).first()
        
        logging.debug(f"Obtem responsavel para exclusão : '{responsavelparaexclusao.nome}'")
        
        # exclui o responsavel: nossa exclusao é lógica para garantir rastreabilidade
        responsavelparaexclusao.ativo = 0

        # efetivando o comando de adição de novo item na tabela
        session.commit()

        return mapeaentidade_paraschemaresponsavel(
            responsavelparaexclusao), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "Responsavel de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao adicionar responsavel '{responsavel.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(f"Erro ao adicionar responsavel '{responsavel.nome}', {error_msg}")
        return {"message": error_msg}, 400


# ========================================================================================================
# Endpoints de centro de interessee
# ========================================================================================================
@app.post('/centrodeinteresse', tags=[centrodeinteresse_tag],responses={
    "200": CentroDeInteresseViewSchema, "409": ErrorSchema, 
    "400": ErrorSchema})
def add_centrodeinteresse(form: CentroDeInteresseSchema):
    """Adiciona um novo centor de interesse à base de dados
    Retorna uma representação dos centro de interesse e comentários associados.
    """    
    try:
        # criando conexão com a base
        session = Session()

        logging.debug(f"Adicionando centrodeinteresse de nome: '{form.tema}'")

        responsavel = session.query(Responsavel).filter(
            Responsavel.id == form.responsavelId, Responsavel.ativo == 1).first()

        if (responsavel == None):
            return {"message": "Responsável inexistente na base de dados!"}, 400

        salas = session.query(Sala).all()

        query = select(CentroDeInteresse,Responsavel).\
            select_from(CentroDeInteresse).join(Responsavel,\
                Responsavel.id == CentroDeInteresse.idResponsavel).filter(
                CentroDeInteresse.ativo == 1, 
                Responsavel.idevento == responsavel.idevento)

        existecentrosdeinteressedoevento = get_count(session,query)

        # Se existem centros de interesse
        if existecentrosdeinteressedoevento > 0:
            # Valida se o responsável que está sendo designado já está em outro centro de interesse
            if get_count(session, query.filter(
                CentroDeInteresse.idResponsavel == form.responsavelId)) > 0:
                return {"message": "Esse responsável já se encontra designado para outro centro de interesse"}, 400
            elif get_count(session, query.filter(
                CentroDeInteresse.idSala == form.salaId)) > 0:
                return {"message": "A sala selecionada já está vinculada a um centro de interesse!"}, 400
            elif existecentrosdeinteressedoevento >= len(salas):
                return {"message": "A quantidade de salas está esgotadas para cadastro de mais centros de interesse!"}, 400

        # centro de interesse validado
        sala = session.query(Sala).filter(Sala.id == form.salaId).first()
        centrodeinteresse = CentroDeInteresse(tema=form.tema, responsavel=responsavel, 
            sala=sala)

        # adicionando centrodeinteresse
        session.add(centrodeinteresse)
        
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logging.debug(f"Adicionado centrodeinteresse de nome: '{centrodeinteresse.tema}'")
        
        return mapeaentidade_paraumschemacentrodeinteresse(
            centrodeinteresse), 200
        # return apresenta_centrodeinteresse(centrodeinteresse), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "CentroDeInteresse de mesmo nome já salvo na base :"
        logging.warning(f"Erro ao adicionar centrodeinteresse '{centrodeinteresse.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(f"Erro ao adicionar centrodeinteresse '{centrodeinteresse.nome}', {error_msg}")
        return {"message": error_msg}, 400

def get_count(session, query):
        query_with_count = query.with_only_columns([func.count().label('total')])
        return session.execute(query_with_count).scalar()


@app.get('/centrodeinteresse', tags=[centrodeinteresse_tag],
    responses={"200": ListagemEventosSchema, "404": ErrorSchema})
def get_centrodeinteresse(query: SearchCentroDeInteresseSchema):
    """ Consulta todos os centros de interesse da base de dados
    Retorna uma lista de centros de interesse
    """
    try:
        session = Session()
        logging.debug("Consulta todos os centrodeinteresses")
        
        queryCentrosDeInteresse = select(Sala.nome, Responsavel.nome, 
        CentroDeInteresse.tema, Responsavel.idevento, CentroDeInteresse.id).\
            select_from(CentroDeInteresse).join(Responsavel, 
                CentroDeInteresse.idResponsavel == Responsavel.id).\
                select_from(Sala).join(Sala, CentroDeInteresse.idSala == Sala.id)

        queryCentrosDeInteresse = queryCentrosDeInteresse.filter(
            Responsavel.idevento == query.eventoId, CentroDeInteresse.ativo == 1)

        results = session.execute(queryCentrosDeInteresse)
        
        return mapeaentidade_paraschemacentrodeinteresse(results), 200
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os centrodeinteresses {e}")
        return {"message": error_msg}, 500

@app.delete('/centrodeinteresse', tags=[centrodeinteresse_tag],responses={"200": CentroDeInteresseViewSchema, "409": 
    ErrorSchema, "400": ErrorSchema})
def delete_centrodeinteresse(form: ExcluirSchema):
    """Remove um centro de interesse da base de dados
    Retorna um centro de interesse
    """    
    try:
        logging.debug(f"Excluindoo  responsavel de id: '{form.id}'")
        # criando conexão com a base
        session = Session()

        centrodeinteresseparaexclusao = session.query(CentroDeInteresse)\
            .filter(CentroDeInteresse.ativo == 1, 
                CentroDeInteresse.id == form.id).first()

        if centrodeinteresseparaexclusao.participantes.count() > 0:
            return {"message": "Existem participantes vinculados a esse centro de interesse, necessário a exclusão!"}, 400
        
        logging.debug(f"Obtem centro de interesse para exclusão : '{centrodeinteresseparaexclusao.tema}'")
        
        # exclui o responsavel: nossa exclusao é lógica para garantir rastreabilidade
        centrodeinteresseparaexclusao.ativo = 0

        # efetivando o comando de adição de novo item na tabela
        session.commit()

        return mapeaentidade_paraumschemacentrodeinteresse(
            centrodeinteresseparaexclusao), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        logging.warning(f"Erro ao excluir centro de interesse '{form.id}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível excluir novo item :/"
        logging.warning(f"Erro ao excluir centro de interesse '{form.id}', {error_msg}")
        return {"message": error_msg}, 400

# ========================================================================================================
# Endpoints de sala
# ========================================================================================================
@app.get('/sala', tags=[sala_tag],
    responses={"200": ListagemSalasSchema, "404": ErrorSchema})
def get_sala():
    """ Consulta todos os salas 
    Retorna uma lista de salas 
    """
    try:
        session = Session()
        logging.debug("Consulta todas as salas")

        salas = session.query(Sala).all()

        return mapeaentidade_paraschemasala(salas), 200
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os salas {e}")
        return {"message": error_msg}, 500

# ========================================================================================================
# Endpoints de Participantes
# ========================================================================================================
@app.post('/participante', tags=[participante_tag],responses={"200": 
    ParticipanteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_participante(form: ParticipanteSchema):
    """Adiciona um novo Participante ao evento
    Retorna um participante de acordo com evento
    """    
    try:

        logging.debug(f"Adicionando participante de nome: '{form.nome}'")

        # criando conexão com a base
        session = Session()

        # valida participantes
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',form.email):
            return {"message": "Formato de e-mail inválido!"}, 400
        elif session.query(Participante).filter(
            Participante.email == form.email, 
            Participante.idevento == form.idevento,
            Participante.ativo == 1).first() != None:
            return {"message": "Já existe um responsável cadastrado com esse e-mail"}, 400

        if session.query(Participante).filter(
            Participante.idevento == form.idevento, Participante.nome == form.nome, 
            Participante.ativo == 1).count() > 0:
            return {"message": "Jà existe um participante cadastrado com esse nome"}, 400
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',form.email):
            return {"message": "Formato de e-mail inválido!"}, 400
        elif session.query(Participante).filter(
            Participante.idevento == form.idevento, 
            Participante.email == form.email, 
            Participante.ativo == 1).count() > 0:
            return {"message": "Esse e-mail já se encontra designado para outro participante"}, 400
        elif session.query(Participante).filter(
            Participante.idevento == form.idevento, Participante.inscricao == form.inscricao, 
            Participante.ativo == 1).count() > 0:
            return {"message": "Já existe um participante com essa inscrição"}, 400

        participante = Participante(
            nome=form.nome,
            email=form.email,
            inscricao=form.inscricao,
            idevento=form.idevento,
            ativo=1,
            cep=form.cep,
            logradouro=form.logradouro,
            numero=form.numero,
            complemento=form.complemento,
            bairro=form.bairro,
            localidade=form.localidade,
            uf=form.uf
        )

        centrodeinteresses = session.query(CentroDeInteresse).filter(
            CentroDeInteresse.id.in_(form.centrosdeinteresse)).all()

        for centrodeinteresse in centrodeinteresses:
            participante.centros_de_interesse.append(centrodeinteresse)

        # adicionando participante
        session.add(participante)

        # efetivando o comando de adição de novo item na tabela
        session.commit()

        logging.debug(f"Adicionado participante de nome: '{participante.nome}'")
        return mapeaentidade_paraschemaparticipante(participante), 200
        # return apresenta_participante(participante), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        error_msg = "Participante de mesmo nome já salvo na base :/"
        logging.warning(f"Erro ao adicionar participante '{participante.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.warning(e)
        logging.warning(f"Erro ao adicionar participante '{participante.nome}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/participante', tags=[participante_tag],
    responses={"200": ListagemEventosSchema, "404": ErrorSchema})
def get_participante(query: SearchParticipanteSchema):
    """ Consulta todos os participantes de um evento
    Retorna uma lista de participantes
    """
    try:
        session = Session()
        logging.debug("Consulta todos os participantes")

        participantes = session.query(Participante).filter(
            Participante.idevento == query.eventoId, Participante.ativo == 1)

        return mapeaentidade_paraschemaparticipantes(participantes), 200
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os participantes {e}")
        return {"message": error_msg}, 500

@app.get('/participante/centrosdeinteresse', tags=[participante_tag],
    responses={"200": ListagemCentroDeInteressePorParticipanteSchema, 
    "404": ErrorSchema})
def get_participante_centrosdeinteressee(query: SearchCentroDeInteresseSchema):
    """ Consulta todos os centros de interesses para associar um participante 
    Retorna uma lista conetendo os centros de interesse
    """
    try:
        session = Session()
        logging.debug("Consulta todos os centros de interesse") 
    
        centrosdeinteresseporevento = session.query(Participante, 
        CentroDeInteresse, Responsavel).outerjoin(
            CentroDeInteresse.participantes).join(Responsavel, 
            CentroDeInteresse.idResponsavel == Responsavel.id).\
                filter(Participante.id == query.eventoId,
                CentroDeInteresse.ativo == 1)
        
        return mapeaentidade_paraschemacentrodeinteresseporparticipante(
            centrosdeinteresseporevento), 200
    except Exception as e:
        # caso um erro fora do previsto
        logging.warning(f"Erro ao consultar os participantes {e}")
        return {"message": error_msg}, 500

@app.delete('/participante', tags=[participante_tag],responses={"200": 
    ParticipanteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def delete_participante(form: ExcluirSchema):
    """Remove um participante da base de ddos
    Retorna o participante removido
    """
    try:
        logging.debug(f"Excluindo participante de id: '{form.id}'")
        # criando conexão com a base
        session = Session()

        participanteparaexclusao = session.query(Participante).filter(
            Participante.ativo == 1, 
            Participante.id == form.id).first()
        
        logging.debug(f"Obtem participante para exclusão : '{participanteparaexclusao.nome}'")
        
        # exclui o responsavel: nossa exclusao é lógica para garantir rastreabilidade
        participanteparaexclusao.ativo = 0

        # efetivando o comando de adição de novo item na tabela
        session.commit()

        return mapeaentidade_paraschemaparticipante(participanteparaexclusao), 200
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        logging.warning(e)
        logging.warning(f"Erro ao exckyur participante '{form.id}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logging.error(e)
        logging.warning(f"Erro ao excluir participante {form.id}, {error_msg}")
        return {"message": error_msg}, 400