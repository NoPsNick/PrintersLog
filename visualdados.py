# -*- coding: latin-1 -*-
import pandas as pd
from pandas import Series

from configuration import Config
from genericvisualdados import GenericVisualDados
from models import Dados, Documento, PDFs, CustomPDF, CustomPDFValue


class VisualDocumentos:
    """
        Classe responsável pela manipulação de dados do tipo Dados.
    """

    def __init__(self, dados: list[dict | pd.DataFrame | Dados] | pd.DataFrame = None):
        """
        Inicializador da classe.
        :param dados: Lista de dicionários, lista de DataFrames, lista de Dados ou apenas um DataFrame.
        """
        self.visual_dados = GenericVisualDados(Dados, shape=12, dados=dados)
        # Classe base do Banco de Dados.
        self.db_info = {'db_class': Documento}
        self.data_format = Config().get_data_format()

    # def criar_relatorio(self):
    #     if self.visual_dados.valid:
    #         self.visual_dados.dados['total'] = np.where(
    #             self.visual_dados.dados.duplex,
    #             np.ceil(self.visual_dados.dados.paginas / 2) * self.visual_dados.dados.copias,
    #             self.visual_dados.dados.paginas * self.visual_dados.dados.copias
    #         )
    #
    #         self.visual_dados.dados['data_usuario'] = (
    #                 self.visual_dados.dados.data.dt.strftime(
    #                 self.data_format) + ' - ' + self.visual_dados.dados.user
    #         )

    def buscar_documentos(self) -> pd.DataFrame:
        """
        Fazer a busca de todos os Dados no Banco de Dados utilizando a classe Base de Banco de Dados.
        :return: DataFrame pandas.
        """
        return self.visual_dados.buscar_no_banco_de_dados(self.db_info['db_class'])

    def pegar_documentos(self) -> list[Dados | None]:
        """
        Pegar todos os documentos salvos no Banco de Dados.
        :return: Lista de Dados.
        """
        dados = self.buscar_documentos()
        self.visual_dados.validar(dados)
        return self.visual_dados.dataframes_para_classes()

    def pegar_documentos_por_nome(self, principal) -> list[Dados | None]:
        """
        Pegar o documentos através do atributo principal.
        :param principal: Atributo para busca.
        :return: Lista de Dados.
        """
        docs = self.buscar_documentos()
        try:
            documentos = docs[docs['principal'] == principal]
            self.visual_dados.validar(documentos)
        except KeyError:
            return []
        return self.visual_dados.dataframes_para_classes()

    def insert_documentos(self, data: pd.DataFrame) -> None:
        """
        Inserir Dados no formato de DataFrame do pandas.
        :param data: Dados no formato de DataFrame pandas que serão inseridos.
        """
        data['data'] = pd.to_datetime(data['data'], format=self.data_format)
        data['hora'] = pd.to_datetime(data['hora'], format="%H:%M:%S").dt.time
        data['paginas'] = pd.to_numeric(data['paginas'])
        data['copias'] = pd.to_numeric(data['copias'])
        if self.db_info['db_class']().validar_dataframe(data):
            self.visual_dados.insert_new_data(data, db_class=self.db_info['db_class'])

    # def read_csvs(self) -> bool:
    #     if not isinstance(self.visual_dados.dados, pd.DataFrame):
    #         arquivos_csv = glob(os.path.join("./csvs/", "*.csv"))
    #         dataframes = [pd.read_csv(arquivo, encoding='latin-1') for arquivo in arquivos_csv]
    #         dados = pd.concat(dataframes, ignore_index=True)
    #         return self.visual_dados.validar(dados)
    #     return self.visual_dados.validar(self.visual_dados.dados)

    @staticmethod
    def create_combined_key(df: pd.DataFrame) -> pd.DataFrame:
        """
        Combinação de chaves para verificação de repetições dentro do Banco de Dados.
        :param df: DataFrame pandas que terá a chave combinada.
        :return: Adição da chave combinada no DataFrame pandas.
        """
        return (
                df['principal'].astype(str) + '_' +
                df['data'].astype(str) + '_' +
                df['hora'].astype(str) + '_' +
                df['user'].astype(str)
        )

    def del_documento(self, principal) -> None:
        """
        Remoção de Dados do Banco de Dados.
        :param principal: Atributo principal do documento que será removido.
        """
        self.visual_dados.remove_data(field_name="principal", value=principal, db_class=self.db_info['db_class'])

    def dados_to_db(self) -> bool:
        """
        Inserção de todos os Dados do parâmetro da classe 'dados' no Banco de Dados fazendo a sua validação e verificando
        repetições.
        :return: bool(True) Caso algum Dado tenha sido inserido com sucesso; bool(False) Caso nenhum Dado tenha sido
        inserido.
        """
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
            Classe responsável pela manipulação de dados do tipo PDF.
    """
    def __init__(self, dados: list[dict | pd.DataFrame | PDFs] | pd.DataFrame = None):
        """
        Inicializador da classe.
        :param dados: Lista de dicionários, lista de DataFrames, lista de PDFs ou apenas um DataFrame.
        """
        self.visual_dados = GenericVisualDados(PDFs, shape=4, dados=dados)
        # Classes bases do Banco de Dados
        self.db_info = {'nomes': CustomPDF, 'valores': CustomPDFValue}

    def buscar_custom_pdfs_nomes(self) -> pd.DataFrame:
        """
        Fazer a busca de todos os nomes dos estilos de PDF no Banco de Dados utilizando a classe Base de Banco de Dados.
        :return: DataFrame pandas.
        """
        return self.visual_dados.buscar_no_banco_de_dados(db_class=self.db_info['nomes'])

    def buscar_custom_pdf_values(self) -> pd.DataFrame:
        """
        Fazer a busca de todos os valores dos estilos de PDF no Banco de Dados utilizando a classe Base de Banco de
        Dados.
        :return: DataFrame pandas.
        """
        return self.visual_dados.buscar_no_banco_de_dados(db_class=self.db_info['valores'])

    def pegar_todos_os_nomes(self) -> list[Series]:
        """
        Pegar todos os nomes dos estilos de PDF em formato de Series do pandas.
        :return: Lista de Series pandas.
        """
        nomes = self.buscar_custom_pdfs_nomes()
        return [row for _, row in nomes.iterrows()] if not nomes.empty else []

    def pegar_pdf_por_nome(self, nome) -> list[PDFs | None]:
        """
        Pegar estilo de PDF através do nome.
        :param nome: Atributo nome para busca.
        :return: Lista de PDFs.
        """
        pdfs = self.buscar_custom_pdfs_nomes()
        valores = self.buscar_custom_pdf_values()
        try:
            pdf_filtrado = pdfs[pdfs['nome'] == nome]
            df = valores[valores['nome'].isin(pdf_filtrado['nome'])]
            self.visual_dados.validar(df)
        except KeyError:
            return []
        return self.visual_dados.dataframes_para_classes()

    def insert_pdf_nome(self, data: pd.DataFrame) -> None:
        """
        Inserir nome dos estilos de PDF no formato de DataFrame do pandas.
        :param data: Nomes do estilo de PDF em formato de DataFrame que será inserido.
        """
        if self.db_info['nomes']().validar_dataframe(data):
            self.visual_dados.insert_new_data(data, db_class=self.db_info['nomes'])

    def insert_custom_pdf_values(self, data: pd.DataFrame) -> None:
        """
        Inserir valores dos estilos de PDF no formato de DataFrame do pandas.
        :param data: Valores do estilo de PDF em formato de DataFrame que será inserido.
        """
        if self.db_info['valores']().validar_dataframe(data):
            self.visual_dados.insert_new_data(data, db_class=self.db_info['valores'])

    def del_pdf(self, nome) -> None:
        """
        Remoção de estilos de PDF do Banco de Dados.
        :param nome: Nome do PDF que será removido.
        """
        self.visual_dados.remove_data(field_name="nome", value=nome, db_class=self.db_info['valores'])
        self.visual_dados.remove_data(field_name="nome", value=nome, db_class=self.db_info['nomes'])

    def custom_pdf_to_db(self) -> bool:
        """
        Inserção de todos os estilos de PDF do parâmetro da classe 'dados' no Banco de Dados fazendo a sua validação e
        verificando repetições.
        :return: bool(True) Caso algum PDF tenha sido inserido com sucesso; bool(False) Caso nenhum PDF tenha sido
        inserido.
        """
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
