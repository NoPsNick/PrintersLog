# -*- coding: latin-1 -*-
import ast
import datetime

import pandas as pd
from pandas import Timestamp
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

from configuration import Config

# Crie uma base para os modelos
Base = declarative_base()

data_format = Config().get_data_format()


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

    def get_dictionary(self) -> dict[str, str | int | Timestamp]:
        return self.__dict__

    def get_dictionary_to_show(self, formato=data_format) -> dict[str, str | int]:
        if isinstance(self.data, datetime.date):
            self.data = self.data.strftime(formato)
            self.hora = self.hora.strftime("%H:%M:%S")
        return self.__dict__


class PDFs:
    def __init__(self, nome: str, tipo: str, valor: str, id: int = None):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.valor = valor

    def get_dictionary(self):
        return self.__dict__

    def get_dict_no_name_id(self):
        return {self.tipo: dict(ast.literal_eval(self.valor))}



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

    def get_schema(self):
        schema = {}
        for column in self.__table__.columns:
            schema[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'default': column.default.arg if column.default else None,
            }
        return schema

    def validar_dataframe(self, df: pd.DataFrame):
        schema = self.get_schema()

        for column_name, properties in schema.items():
            if column_name not in df.columns:
                raise ValueError(f"A coluna '{column_name}' está ausente no DataFrame.")

            # Tratamento especial para a coluna de ID autoincrementável
            if column_name == 'id' and properties['primary_key']:
                continue  # Não precisamos validar o tipo de dado ou valores nulos para IDs autoincrementáveis

            # Verificação de tipo de dado
            expected_type = properties['type']
            if expected_type == 'INTEGER':
                if not pd.api.types.is_integer_dtype(df[column_name]):
                    raise TypeError(f"A coluna '{column_name}' deve ser do tipo INTEGER.")
            elif expected_type == 'VARCHAR':
                if not pd.api.types.is_string_dtype(df[column_name]):
                    raise TypeError(f"A coluna '{column_name}' deve ser do tipo STRING.")
            elif expected_type == 'DATE':
                if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
                    raise TypeError(f"A coluna '{column_name}' deve ser do tipo DATE.")
            elif expected_type == 'TIME':
                if not pd.api.types.is_datetime64_any_dtype(
                        df[column_name].apply(lambda x: pd.Timestamp.combine(pd.Timestamp.today(), x))):
                    raise TypeError(f"A coluna '{column_name}' deve ser do tipo TIME.")
            elif expected_type == 'BOOLEAN':
                if not pd.api.types.is_bool_dtype(df[column_name]):
                    raise TypeError(f"A coluna '{column_name}' deve ser do tipo BOOLEAN.")

            # Verificação de valores nulos
            if not properties['nullable'] and df[column_name].isnull().any():
                raise ValueError(f"A coluna '{column_name}' não pode conter valores nulos.")

        return True


# Defina o modelo CustomPDFs
class CustomPDF(Base):
    __tablename__ = 'CustomPDFs'

    nome = Column(String, primary_key=True)

    def get_schema(self):
        schema = {}
        for column in self.__table__.columns:
            schema[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'default': column.default.arg if column.default else None,
            }
        return schema

    def validar_dataframe(self, df: pd.DataFrame):
        schema = self.get_schema()

        for column_name, properties in schema.items():
            if column_name not in df.columns:
                raise ValueError(f"A coluna '{column_name}' está ausente no DataFrame.")

            if not properties['nullable'] and df[column_name].isnull().any():
                raise ValueError(f"A coluna '{column_name}' não pode conter valores nulos.")

        return True


# Defina o modelo CustomPDFsValues
class CustomPDFValue(Base):
    __tablename__ = 'CustomPDFsValues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, ForeignKey('CustomPDFs.nome'), nullable=False)
    tipo = Column(String, nullable=False)
    valor = Column(String, nullable=False)

    # Relacionamento
    custom_pdf = relationship('CustomPDF', backref='values')

    def get_schema(self):
        schema = {}
        for column in self.__table__.columns:
            schema[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'default': column.default.arg if column.default else None,
            }
        return schema

    def validar_dataframe(self, df: pd.DataFrame):
        schema = self.get_schema()

        for column_name, properties in schema.items():
            if column_name not in df.columns:
                raise ValueError(f"A coluna '{column_name}' está ausente no DataFrame.")

            if column_name == 'id' and properties['primary_key']:
                continue  # Não precisamos validar o tipo de dado ou valores nulos para IDs autoincrementáveis

            if not properties['nullable'] and df[column_name].isnull().any():
                raise ValueError(f"A coluna '{column_name}' não pode conter valores nulos.")

        return True
