import pandas as pd
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Crie uma base para os modelos
Base = declarative_base()


class Dados:
    # Arquivo Principal, Data, Horário, Usuário, Páginas, Cópias, Impressora, Arquivo, Tipo,
    # Tamanho,Tipo de Impressão,Estação,Duplex,Escala de Cinza.
    def __init__(self, principal, data, hora, user, paginas, copias, impressora, arquivo, est, duplex, escala_de_cinza,
                 id=None):
        self.id = id
        self.principal = principal
        self.data = data
        self.hora = hora
        self.user = user
        self.paginas = paginas
        self.copias = copias
        self.impressora = impressora
        self.arquivo = arquivo
        self.est = est
        self.duplex = duplex
        self.escala_de_cinza = escala_de_cinza

    def __repr__(self):
        return str(self.__dict__)

    def get_dictionary(self):
        return self.__dict__

    def get_dictionary_to_show(self, data_format='%d/%m/%Y'):
        if isinstance(self.data, pd.Timestamp):
            self.data = self.data.strftime(data_format)
            self.hora = self.hora.strftime("%H:%M:%S")
        return self.__dict__


class Documento(Base):
    __tablename__ = 'Documentos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    principal = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    user = Column(String, nullable=False)
    paginas = Column(Integer, nullable=False)
    copias = Column(Integer, nullable=False)
    impressora = Column(String, nullable=False)
    arquivo = Column(String, nullable=False)
    est = Column(String, nullable=False)
    duplex = Column(Boolean, default=False)
    escala_de_cinza = Column(Boolean, default=False)


# Defina o modelo CustomPDFs
class CustomPDF(Base):
    __tablename__ = 'CustomPDFs'

    nome = Column(String, primary_key=True)


# Defina o modelo CustomPDFsValues
class CustomPDFValue(Base):
    __tablename__ = 'CustomPDFsValues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, ForeignKey('CustomPDFs.nome'), nullable=False)
    tipo = Column(String, nullable=False)
    valor = Column(String, nullable=False)

    # Relacionamento
    custom_pdf = relationship('CustomPDF', backref='values')
