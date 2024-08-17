# -*- coding: latin-1 -*-
import os
from glob import glob

import numpy as np
import pandas as pd

from configuration import Config
from genericvisualdados import GenericVisualDados
from models import Dados, Documento, PDFs, CustomPDF, CustomPDFValue


class VisualDocumentos:
    """
        Classe responsável pela manipulação de dados de documentos.

        Attributes:
        ----------
        visual_dados : GenericVisualDados
            Instância da classe genérica de visualização de dados.
    """

    def __init__(self, dados: list[dict | pd.DataFrame | Dados] | pd.DataFrame = None):
        self.visual_dados = GenericVisualDados(Dados, shape=12, dados=dados)
        self.db_info = {'db_class': Documento}
        self.data_format = Config().get_data_format()

    def criar_relatorio(self):
        if self.visual_dados.valid:
            self.visual_dados.dados['total'] = np.where(
                self.visual_dados.dados.duplex,
                np.ceil(self.visual_dados.dados.paginas / 2) * self.visual_dados.dados.copias,
                self.visual_dados.dados.paginas * self.visual_dados.dados.copias
            )

            self.visual_dados.dados['data_usuario'] = (
                    self.visual_dados.dados.data.dt.strftime(
                        self.data_format) + ' - ' + self.visual_dados.dados.user
            )

    def buscar_documentos(self) -> pd.DataFrame:
        return self.visual_dados.buscar_no_banco_de_dados(self.db_info['db_class'])

    def pegar_documentos(self) -> list[Dados | None]:
        dados = self.buscar_documentos()
        self.visual_dados.validar(dados)
        return self.visual_dados.dataframes_para_classes()

    def pegar_documentos_por_nome(self, principal) -> list[Dados | None]:
        docs = self.buscar_documentos()
        try:
            documentos = docs[docs['principal'] == principal]
            self.visual_dados.validar(documentos)
        except KeyError:
            return []
        return self.visual_dados.dataframes_para_classes()

    def insert_documentos(self, data: pd.DataFrame):
        data['data'] = pd.to_datetime(data['data'], format=self.data_format)
        data['hora'] = pd.to_datetime(data['hora'], format="%H:%M:%S").dt.time
        data['paginas'] = pd.to_numeric(data['paginas'])
        data['copias'] = pd.to_numeric(data['copias'])
        if self.db_info['db_class']().validar_dataframe(data):
            self.visual_dados.insert_new_data(data, db_class=self.db_info['db_class'])

    def read_csvs(self) -> bool:
        if not isinstance(self.visual_dados.dados, pd.DataFrame):
            arquivos_csv = glob(os.path.join("./csvs/", "*.csv"))
            dataframes = [pd.read_csv(arquivo, encoding='latin-1') for arquivo in arquivos_csv]
            dados = pd.concat(dataframes, ignore_index=True)
            return self.visual_dados.validar(dados)
        return self.visual_dados.validar(self.visual_dados.dados)

    @staticmethod
    def create_combined_key(df: pd.DataFrame) -> pd.DataFrame:
        return (
                df['principal'].astype(str) + '_' +
                df['data'].astype(str) + '_' +
                df['hora'].astype(str) + '_' +
                df['user'].astype(str)
        )

    def del_documento(self, principal):
        self.visual_dados.remove_data(field_name="principal", value=principal, db_class=self.db_info['db_class'])

    def dados_to_db(self) -> bool:
        self.visual_dados.validate()
        if not self.visual_dados.valid:
            return False
        else:
            self.visual_dados.dados['data'] = pd.to_datetime(self.visual_dados.dados['data']
                                                             , format=self.data_format)
            self.visual_dados.dados['hora'] = pd.to_datetime(self.visual_dados.dados['hora'],
                                                             format="%H:%M:%S").dt.time

        existentes = self.buscar_documentos()
        self.visual_dados.dados['chave_combinada'] = self.create_combined_key(self.visual_dados.dados)

        if not existentes.empty:
            existentes['chave_combinada'] = self.create_combined_key(existentes)
            novos_dados = self.visual_dados.dados[
                ~self.visual_dados.dados['chave_combinada'].isin(existentes['chave_combinada'])].copy()
        else:
            novos_dados = self.visual_dados.dados.copy()

        novos_dados.drop(columns=['chave_combinada'], inplace=True)
        if not novos_dados.empty:
            self.insert_documentos(data=novos_dados)

        return not novos_dados.empty


class VisualPDFs:
    """
            Classe responsável pela manipulação de dados de estilos de PDF.

            Attributes:
            ----------
            visual_dados : GenericVisualDados
                Instância da classe genérica de visualização de dados.
    """
    def __init__(self, dados: list[dict | pd.DataFrame | PDFs] | pd.DataFrame = None):
        self.visual_dados = GenericVisualDados(PDFs, shape=4, dados=dados)
        self.db_info = {'nomes': CustomPDF, 'valores': CustomPDFValue}

    def buscar_custom_pdfs_nomes(self) -> pd.DataFrame:
        return self.visual_dados.buscar_no_banco_de_dados(db_class=self.db_info['nomes'])

    def buscar_custom_pdf_values(self) -> pd.DataFrame:
        return self.visual_dados.buscar_no_banco_de_dados(db_class=self.db_info['valores'])

    def pegar_todos_os_nomes(self) -> list[str] | list:
        nomes = self.buscar_custom_pdfs_nomes()
        return [str(row) for _, row in nomes.iterrows()] if not nomes.empty else []

    def pegar_pdf_por_nome(self, nome) -> list[PDFs] | list[None]:
        pdfs = self.buscar_custom_pdfs_nomes()
        valores = self.buscar_custom_pdf_values()
        try:
            pdf_filtrado = pdfs[pdfs['nome'] == nome]
            df = valores[valores['nome'].isin(pdf_filtrado['nome'])]
            self.visual_dados.validar(df)
        except KeyError:
            return []
        return self.visual_dados.dataframes_para_classes()

    def insert_pdf_nome(self, data: pd.DataFrame):
        if self.db_info['nomes']().validar_dataframe(data):
            self.visual_dados.insert_new_data(data, db_class=self.db_info['nomes'])

    def insert_custom_pdf_values(self, data: pd.DataFrame):
        if self.db_info['valores']().validar_dataframe(data):
            self.visual_dados.insert_new_data(data, db_class=self.db_info['valores'])

    def del_pdf(self, nome):
        self.visual_dados.remove_data(field_name="nome", value=nome, db_class=self.db_info['valores'])
        self.visual_dados.remove_data(field_name="nome", value=nome, db_class=self.db_info['nomes'])

    def custom_pdf_to_db(self) -> bool:
        self.visual_dados.validate()
        if not self.visual_dados.valid:
            return False

        principais = self.buscar_custom_pdfs_nomes()

        novos_dados = self.visual_dados.dados.copy(deep=True)
        if not principais.empty:
            novos_nomes_existentes = novos_dados['nome'].drop_duplicates().loc[
                ~novos_dados['nome'].isin(principais['nome'])]

            if not novos_nomes_existentes.empty:
                novos_nomes_df = pd.DataFrame({'nome': novos_nomes_existentes})
                self.insert_pdf_nome(data=novos_nomes_df)

            dados_para_inserir = novos_dados[novos_dados['nome'].isin(novos_nomes_existentes)]
        else:
            novos_nomes_df = pd.DataFrame({'nome': novos_dados['nome'].drop_duplicates()})
            self.insert_pdf_nome(data=novos_nomes_df)
            dados_para_inserir = novos_dados.copy()

        if not dados_para_inserir.empty:
            self.insert_custom_pdf_values(data=dados_para_inserir)
        return not dados_para_inserir.empty
