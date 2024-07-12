from typing import Union
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table

Base = declarative_base()
class PessoaFisica(Base):
    __tablename__ = 'pessoafisica'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    cpf = Column(String, unique=True)
    email = Column(String)
    ativo =  Column(Integer)

class StatusEvento(Base):
    __tablename__ = "statusevento"

    id = Column("pk_statusevento", Integer, primary_key=True)
    nome = Column(String(200), unique=True)
    ativo: Column(Integer)

    eventos = relationship("Evento")

    def __init__(self, nome: str):
        self.nome = nome
        self.ativo = 1

class Evento(Base):
    __tablename__ = "evento"

    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    ativo = Column(Integer)
    datainicio = Column(DateTime, default=datetime.now())
    datafim = Column(DateTime, default=datetime.now())
    idstatusevento = Column(Integer, ForeignKey("statusevento.pk_statusevento"), 
        nullable=False)
    idcentrosdeinteresse = Column(Integer)

    def __init__(self, nome:str, data_inicio:Union[DateTime, None] = None, 
        data_fim:Union[DateTime, None] = None):
        """
        Cria um Evento

        Arguments:
            nome: a descrição do evento
            data_inicio: data de início de um evento: pode durar mais de um
                            dia
            data_fim: dafa final do evento
        """
        self.nome = nome
        if data_inicio:
            self.datainicio = data_inicio
        if data_fim:
            self.datafim = data_fim
        self.ativo = 1
        self.statusevento = 1
        self.idcentrosdeinteresse = 1
    
    def update(self, nome:str, data_inicio:Union[DateTime, None] = None):
        """
        Atualiza um evento

        Arguments:
            nome: a descrição do evento
            data_inicio: data do evento
        """
        self.nome = nome
        if data_inicio:
            self.datainicio = data_inicio

class Sala(Base):
    __tablename__ = ("sala")

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    def __init__(self, nome:str):
        self.nome = nome

class Responsavel(PessoaFisica):
    __tablename__ = "responsavel"

    id = Column(Integer, primary_key=True)
    matricula = Column(String(200))
    idevento = Column(Integer, ForeignKey(Evento.id), 
        nullable=False)

    def __init__(self, matricula: str, idevento:int, **kwargs):
        super().__init__(**kwargs)
        self.matricula = matricula
        self.idevento = idevento
        self.ativo = 1

    __mapper_args__ = {
        'inherit_condition': (id == PessoaFisica.id)
    }

class Participante(PessoaFisica):
    __tablename__ = "participante"

    id = Column(Integer, primary_key=True)
    inscricao = Column(String(200))
    idevento = Column(Integer, ForeignKey(Evento.id), 
        nullable=False)
    cep = Column(String)
    logradouro = Column(String)
    numero = Column(String)
    complemento = Column(String)
    bairro = Column(String)
    localidade = Column(String)
    uf = Column(String)

    centros_de_interesse = relationship(
        "CentroDeInteresse", 
        secondary="participantecentrodeinteresse",
        back_populates="participantes")

    def __init__(self, inscricao: str, idevento:int ,cep: str, logradouro: str, numero: str
        ,complemento: str, bairro: str, localidade: str, uf: str , **kwargs):
        super().__init__(**kwargs)
        self.inscricao = inscricao
        self.idevento = idevento
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.localidade = localidade
        self.uf = uf

    # def __init__(self, inscricao: str, idevento:int , cep: str, logradouro: str,
    #     numero: str, complemento: str, bairro: str, localidade: str, uf: str,
    #     **kwargs):
    #     super().__init__(**kwargs)
    #     self.inscricao = inscricao
    #     self.idevento = idevento,
    #     self.cep = cep,
    #     self.logradouro = logradouro,
    #     self.numero = numero, 
    #     self.complemento = complemento,
    #     self.bairro = bairro,
    #     self.localidade = localidade,
    #     self.uf = uf

    __mapper_args__ = {
        'inherit_condition': (id == PessoaFisica.id)
    }

class CentroDeInteresse(Base):
    __tablename__ = 'centrosdeinteresse'

    id = Column(Integer, primary_key=True)
    tema = Column(String)
    ativo =  Column(Integer)
    idResponsavel = Column(Integer,ForeignKey(Responsavel.id))
    idSala = Column(Integer, ForeignKey("sala.id"), nullable=False)

    participantes = relationship(
        Participante, 
        secondary="participantecentrodeinteresse",
        back_populates="centros_de_interesse"
    )

    def __init__(self, tema:str, responsavel:Responsavel, sala: Sala):
        self.tema = tema
        self.idResponsavel = responsavel.id
        self.idSala = sala.id
        self.ativo = 1

participantecentrodeinteresse = Table(
    'participantecentrodeinteresse', 
    Base.metadata,
    Column('IdParticipante', Integer, ForeignKey(Participante.id)),
    Column('IdCentrosDeInteresse', Integer, ForeignKey(CentroDeInteresse.id))
)

Participante.centros_de_interesse = relationship(
    CentroDeInteresse, 
    secondary=participantecentrodeinteresse, 
    back_populates="participantes"
)

CentroDeInteresse.participantes = relationship(
    Participante,
    secondary=participantecentrodeinteresse,
    back_populates="centros_de_interesse"
)