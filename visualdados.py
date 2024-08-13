# -*- coding: latin-1 -*-
import ast
import os
from glob import glob

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from configuration import Config
from models import Dados, Documento, CustomPDF, CustomPDFValue, Base


class VisualDados:
    def __init__(self, dados: list[dict | pd.DataFrame] | pd.DataFrame = None):
        self.dados = dados or []
        self._valid = False
        self._type = None
        self.db_url = 'sqlite:///./dbs/banco_de_dados.db'
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.data_format = Config().get_data_format()

    def _create_session(self):
        """Cria e retorna uma nova sessão do SQLAlchemy."""
        return self.Session()

    def _validar(self, df: pd.DataFrame, tipo: str) -> bool:
        if isinstance(df, pd.DataFrame):
            if (tipo == "dados" and df.shape[1] == 12) or (tipo == "pdfs" and df.shape[1] == 4):
                self._type = tipo
                self._valid = True
                self.dados = df
                if self._type == 'dados':
                    self.dados.data = pd.to_datetime(self.dados.data, format=self.data_format)
                    self.dados.hora = pd.to_datetime(self.dados.hora, format="%H:%M:%S").dt.time
        else:
            self._type = None
            self._valid = False
        return self._valid

    def read_csvs(self) -> bool:
        if not isinstance(self.dados, pd.DataFrame):
            arquivos_csv = glob(os.path.join("./csvs/", "*.csv"))
            dataframes = [pd.read_csv(arquivo, encoding='latin-1') for arquivo in arquivos_csv]
            dados = pd.concat(dataframes, ignore_index=True)
            return self._validar(dados, "dados")
        return self._validar(self.dados, "dados")

    def criar_relatorio(self):
        if self._valid and self._type == "dados":
            self.dados.data = pd.to_datetime(self.dados.data, format=self.data_format)
            self.dados.hora = pd.to_datetime(self.dados.hora, format="%H:%M:%S").dt.time

            self.dados['total'] = np.where(
                self.dados.duplex,
                np.ceil(self.dados.paginas / 2) * self.dados.copias,
                self.dados.paginas * self.dados.copias
            )

            self.dados['data_usuario'] = (
                    self.dados.data.dt.strftime(self.data_format) + ' - ' + self.dados.user
            )

    def validate_dados(self) -> bool:
        if not isinstance(self.dados, pd.DataFrame):
            df = pd.DataFrame([dic.get_dictionary() for dic in self.dados])
            return self._validar(df, "dados")
        return self._validar(self.dados, "dados")

    def validate_custom_pdf(self, nome: str) -> bool:
        if not isinstance(self.dados, pd.DataFrame):
            df = pd.DataFrame([
                {'id': None, 'nome': nome, 'tipo': tipo, 'valor': str(valor)}
                for dic in self.dados for tipo, valor in dic.items()
            ])
            return self._validar(df, "pdfs")
        return self._validar(self.dados, "pdfs")

    def dataframes_para_dicionarios(self) -> list[dict | None]:
        if self._valid and isinstance(self.dados, pd.DataFrame):
            if self._type == "pdfs":
                return [{row['tipo']: dict(ast.literal_eval(row['valor']))} for _, row in self.dados.iterrows()]
            elif self._type == "dados":
                copia = self.dados.copy(deep=True)
                try:
                    copia = copia.loc[:, copia.columns != 'id']
                except KeyError:
                    pass
                return [Dados(**row).get_dictionary() for _, row in copia.iterrows()]
        return []

    def pegar_todos_os_nomes(self) -> list[str | None]:
        pegar = self.buscar_no_banco_de_dados("CustomPDFs")
        return [row for _, row in pegar.iterrows()] if not pegar.empty else []

    @staticmethod
    def create_combined_key(df: pd.DataFrame) -> pd.DataFrame:
        return (
                df['principal'].astype(str) + '_' +
                df['data'].astype(str) + '_' +
                df['hora'].astype(str) + '_' +
                df['user'].astype(str)
        )

    def pegar_documentos(self) -> list[dict | None]:
        self.dados = self.buscar_no_banco_de_dados("Documentos")
        self._validar(self.dados, "dados")
        return self.dataframes_para_dicionarios()

    def pegar_pdf_por_nome(self, nome: str) -> list[dict | None]:
        pdfs = self.buscar_no_banco_de_dados("CustomPDFs")
        valores = self.buscar_no_banco_de_dados("CustomPDFsValues")

        pdf_filtrado = pdfs[pdfs['nome'] == nome]
        df = valores[valores['nome'].isin(pdf_filtrado['nome'])]
        self._validar(df, "pdfs")
        return self.dataframes_para_dicionarios()

    def buscar_no_banco_de_dados(self, table_name: str) -> pd.DataFrame:
        Base.metadata.create_all(self.engine)
        with self._create_session() as session:
            try:
                if table_name == 'CustomPDFs':
                    retorno = session.query(CustomPDF).all()
                elif table_name == 'CustomPDFsValues':
                    retorno = session.query(CustomPDFValue).all()
                elif table_name == 'Documentos':
                    retorno = session.query(Documento).all()
                else:
                    raise ValueError(f"Tabela desconhecida: {table_name}")

                data = [obj.__dict__ for obj in retorno]
                for item in data:
                    item.pop('_sa_instance_state', None)

                df = pd.DataFrame(data)
                return df

            except SQLAlchemyError as e:
                raise e
            finally:
                session.close()

    def insert_new_data(self, table_name, data):
        dados = data.to_dict(orient='records')
        Base.metadata.create_all(self.engine)
        with self._create_session() as session:
            try:
                for record in dados:
                    if table_name == 'CustomPDFs':
                        adicao = CustomPDF(**record)
                    elif table_name == 'CustomPDFsValues':
                        adicao = CustomPDFValue(**record)
                    elif table_name == 'Documentos':
                        adicao = Documento(**record)
                    else:
                        raise ValueError(f"Tabela desconhecida: {table_name}")
                    session.add(adicao)

                session.commit()
            except SQLAlchemyError:
                session.rollback()
            finally:
                session.close()

    def remover_pdf(self, nome):
        with self._create_session() as session:
            try:
                # Primeiro remova os valores associados
                values = session.query(CustomPDFValue).filter_by(nome=nome).all()
                for value in values:
                    session.delete(value)

                # Agora remova o CustomPDF principal
                pdf = session.query(CustomPDF).filter_by(nome=nome).first()
                if pdf:
                    session.delete(pdf)

                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(e)
            finally:
                session.close()

    def remover_documento(self, principal):
        with self._create_session() as session:
            try:
                documentos = session.query(Documento).filter_by(principal=principal).all()
                for doc in documentos:
                    session.delete(doc)
                session.commit()
            except SQLAlchemyError:
                session.rollback()
            finally:
                session.close()

    def dados_to_db(self) -> bool:
        nome_da_tabela = "Documentos"
        self.validate_dados()
        if not self._valid and not self._type:
            return False

        existentes = self.buscar_no_banco_de_dados(nome_da_tabela)
        self.dados['chave_combinada'] = self.create_combined_key(self.dados)

        if not existentes.empty:
            existentes['chave_combinada'] = self.create_combined_key(existentes)
            novos_dados = self.dados[~self.dados['chave_combinada'].isin(existentes['chave_combinada'])].copy()
        else:
            novos_dados = self.dados.copy()

        novos_dados.drop(columns=['chave_combinada'], inplace=True)
        self.insert_new_data(nome_da_tabela, novos_dados)

        return not novos_dados.empty

    def custom_pdf_to_db(self, nome: str) -> bool:
        nome_da_tabela_principal = "CustomPDFs"
        nome_da_tabela_dos_valores = "CustomPDFsValues"
        self.validate_custom_pdf(nome)
        if not self._valid and not self._type:
            return False

        principais = self.buscar_no_banco_de_dados(nome_da_tabela_principal)

        novos_dados = self.dados.copy(deep=True)
        if not principais.empty:
            novos_nomes_existentes = novos_dados['nome'].drop_duplicates().loc[
                ~novos_dados['nome'].isin(principais['nome'])]

            if not novos_nomes_existentes.empty:
                novos_nomes_df = pd.DataFrame({'nome': novos_nomes_existentes})
                self.insert_new_data(nome_da_tabela_principal, novos_nomes_df)

            dados_para_inserir = novos_dados[novos_dados['nome'].isin(novos_nomes_existentes)]
        else:
            novos_nomes_df = pd.DataFrame({'nome': novos_dados['nome'].drop_duplicates()})
            self.insert_new_data(nome_da_tabela_principal, novos_nomes_df)
            dados_para_inserir = novos_dados.copy()

        if not dados_para_inserir.empty:
            self.insert_new_data(nome_da_tabela_dos_valores, dados_para_inserir)
        return not dados_para_inserir.empty


if __name__ == '__main__':
    pass
