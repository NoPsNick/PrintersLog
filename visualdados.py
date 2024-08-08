# -*- coding: latin-1 -*-
import ast
import os.path
from glob import glob

import pandas as pd
from sqlalchemy import create_engine

from configuration import Config
from models import Dados


class VisualDados:
    def __init__(self, dados=None):
        if dados is None:
            dados = []
        self._valid = False
        self._type = None
        self.dados = dados
        self.db_url = 'sqlite:///./dbs/banco_de_dados.db'
        self.data_format = Config().get_data_format()

    def _validar(self, dados: pd.DataFrame, type: str):
        if not dados.empty and type == "dados":
            if dados.shape[1] == 11:
                self._type = type
                self._valid = True
        elif not dados.empty and type == "pdfs":
            if dados.shape[1] == 3:
                self._type = type
                self._valid = True
        else:
            self._type = None
            self._valid = False
        return self._valid

    def validate_dados(self):
        if not isinstance(self.dados, pd.DataFrame):
            # Criar uma lista para armazenar as linhas do DataFrame
            linhas = []

            # Preencher a lista com as linhas do DataFrame
            for dic in self.dados:
                linhas.append(dic.get_dictionary())

            # Criar o DataFrame
            df = pd.DataFrame(linhas)
            if self._validar(df, "dados"):
                self.dados = df
        else:
            self._validar(self.dados, "dados")
        return self.dados

    def read_csvs(self):
        if not isinstance(self.dados, pd.DataFrame):
            caminho_dos_csvs = "./csvs/"
            arquivos_csv = glob(os.path.join(caminho_dos_csvs, "*.csv"))
            dataframes = []

            for arquivo in arquivos_csv:
                df = pd.read_csv(arquivo, encoding='latin-1')
                dataframes.append(df)

            dados = pd.concat(dataframes, ignore_index=True)
            if self._validar(dados, "dados"):
                self.dados = dados
        else:
            self._validar(self.dados, "dados")
        return self.dados

        # self.manipulate.data = pd.to_datetime(self.manipulate.data, format=self.data_format)
        # self.manipulate.hora = pd.to_datetime(self.manipulate.hora, format="%H:%M:%S").dt.time
        #
        # self.manipulate['total'] = np.where(self.manipulate.duplex,
        #                                     np.ceil(self.manipulate.paginas / 2) * self.manipulate.copias,
        #                                     self.manipulate.paginas * self.manipulate.copias)
        #
        # self.data_shape = self.manipulate.shape
        # self.nan_values = self.manipulate.isna().values
        # self.duplicated_rows = self.manipulate[self.manipulate.duplicated()]
        #
        # self.manipulate['data_usuario'] = (self.manipulate.data.dt.strftime(self.data_format)
        #                                    + ' - ' + self.manipulate.user)

    def validate_custom_pdf(self, nome: str):
        if not isinstance(self.dados, pd.DataFrame):
            # Criar uma lista para armazenar as linhas do DataFrame
            linhas = []

            # Preencher a lista com as linhas do DataFrame
            for dic in self.dados:
                for tipo, valor in dic.items():
                    linhas.append({'nome': nome, 'tipo': tipo, 'valor': str(valor)})

            # Criar o DataFrame
            df = pd.DataFrame(linhas)
            if self._validar(df, "pdfs"):
                self.dados = df
        else:
            self._validar(self.dados, "pdfs")
        return self.dados

    def dataframes_para_dicionarios(self):
        dicionarios = []
        if self._valid and self._type == "pdfs":
            for _, row in self.dados.iterrows():
                dicionario = {row.iloc[1]: dict(ast.literal_eval(row.iloc[2]))}
                dicionarios.append(dicionario)
        elif self._valid and self._type == "dados":
            for _, row in self.dados.iterrows():
                dicionario = Dados(**row).get_dictionary()
                dicionarios.append(dicionario)
        else:
            dicionarios = self.dados
        return dicionarios

    def pegar_todos_os_nomes(self):
        nomes = []
        pegar = self.buscar_no_banco_de_dados("CustomPDFs")
        if not pegar.empty:
            nomes.extend([row for _, row in pegar.iterrows()])
        return nomes

    @staticmethod
    def create_combined_key(df):
        return (df['principal'].astype(str) + '_' +
                df['data'].astype(str) + '_' +
                df['hora'].astype(str) + '_' +
                df['user'].astype(str))

    def pegar_documentos(self):
        dados = self.buscar_no_banco_de_dados("Documentos")
        self.dados = dados
        self._validar(self.dados, "dados")
        return self.dataframes_para_dicionarios()

    def pegar_pdf_por_nome(self, nome: str):
        pdfs = self.buscar_no_banco_de_dados("CustomPDFs")
        valores = self.buscar_no_banco_de_dados("CustomPDFsValues")

        # Filtra o dataframe pdfs para obter as linhas onde a coluna 'nome' é igual ao nome fornecido
        pdf_filtrado = pdfs[pdfs['nome'] == nome]

        # Filtra o dataframe valores para pegar apenas as linhas onde alguma coluna contém o valor de 'pdf_filtrado'
        df = valores[valores['nome'].isin(pdf_filtrado['nome'])]

        self.dados = df
        self._validar(self.dados, "pdfs")
        retorno = self.dataframes_para_dicionarios()
        return retorno

    def buscar_no_banco_de_dados(self, table_name, connection=None):
        if not connection:
            engine = create_engine(self.db_url)
            try:
                with engine.connect() as connection:
                    existentes = pd.read_sql_table(table_name, connection)
                    return existentes
            except ValueError as e:
                print(e)
                return pd.DataFrame()
        else:
            try:
                existentes = pd.read_sql_table(table_name, connection)
                return existentes
            except ValueError:
                return pd.DataFrame()

    def insert_new_data(self, connection, table_name, data):
        data.to_sql(name=table_name, con=connection, if_exists='append', index=False)

    def dados_to_db(self):
        nome_da_tabela = "Documentos"
        db_url = self.db_url
        engine = create_engine(db_url)
        if not self._valid and not self._type:
            self.dados = self.read_csvs()

        with engine.connect() as connection:
            existentes = self.buscar_no_banco_de_dados(nome_da_tabela, connection)

            self.dados['chave_combinada'] = self.create_combined_key(self.dados)
            if not existentes.empty:
                existentes['chave_combinada'] = self.create_combined_key(existentes)
                novos_dados = self.dados[~self.dados['chave_combinada'].isin(existentes['chave_combinada'])].copy()
            else:
                novos_dados = self.dados.copy()

            # Remover a coluna 'chave_combinada' antes de inserir os dados
            self.dados.drop(columns=['chave_combinada'], inplace=True)
            novos_dados.drop(columns=['chave_combinada'], inplace=True)

            self.insert_new_data(connection, nome_da_tabela, novos_dados)

        return not novos_dados.empty

    def custom_pdf_to_db(self, nome: str):
        nome_da_tabela_principal = "CustomPDFs"
        nome_da_tabela_dos_valores = "CustomPDFsValues"
        db_url = self.db_url
        engine = create_engine(db_url)
        if not self._valid and not self._type:
            self.dados = self.validate_custom_pdf(nome)

        with engine.connect() as connection:
            principais = self.buscar_no_banco_de_dados(nome_da_tabela_principal, connection)

            novos_dados = self.dados.copy(deep=True)
            if not principais.empty:
                novos_nomes = novos_dados['nome'].drop_duplicates()
                novos_nomes_existentes = novos_nomes[~novos_nomes.isin(principais['nome'])]

                if not novos_nomes_existentes.empty:
                    novos_nomes_df = pd.DataFrame({'nome': novos_nomes_existentes})
                    self.insert_new_data(connection, nome_da_tabela_principal, novos_nomes_df)

                dados_para_inserir = novos_dados[novos_dados['nome'].isin(novos_nomes_existentes)]
            else:
                novos_nomes = novos_dados['nome'].drop_duplicates()
                novos_nomes_df = pd.DataFrame({'nome': novos_nomes})
                self.insert_new_data(connection, nome_da_tabela_principal, novos_nomes_df)

                dados_para_inserir = novos_dados.copy()

            if not dados_para_inserir.empty:
                self.insert_new_data(connection, nome_da_tabela_dos_valores, dados_para_inserir)
        return not dados_para_inserir.empty


if __name__ == '__main__':
    dicionarios = [{'set_font': {'family': 'Times', 'style': 'B', 'size': 12}},
                   {'cell': {'w': 0, 'h': 80, 'txt': '', 'border': 1, 'ln': 0, 'align': 'C'}},
                   {'set_font': {'family': 'Times', 'style': 'B', 'size': 12}},
                   {'cell': {'w': 0, 'h': 80, 'txt': '', 'border': 1, 'ln': 0, 'align': 'C'}},
                   {'multicell': {'w': 0, 'h': 80, 'txt': '', 'border': 1, 'align': 'J'}},
                   {'multicell': {'w': 0, 'h': 80, 'txt': '', 'border': 1, 'align': 'J'}},
                   {'python_code': {'code': 'teste = "teste"\nprint(teste)\n#'}},
                   {'python_code': {'code': 'test = 150'}},
                   {'python_code': {'code': 'test = 155'}}, {'set_font': {'family': 'Times', 'style': 'B', 'size': 12}},
                   {'cell': {'w': 0, 'h': 80, 'txt': '', 'border': 1, 'ln': 0, 'align': 'C'}}]

    lista_de_dicionarios = [
        {'principal': 'primeiro.html', 'data': '05/06/2023', 'hora': '09:39:38', 'user': 'jovem', 'paginas': 7,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Pagina de teste (210mm x 297mm), 226kb, XPS',
         'est': 'DESKTOP-K9QUCDT', 'duplex': True, 'escala_de_cinza': False},
        {'principal': 'primeiro.html', 'data': '05/06/2023', 'hora': '09:39:54', 'user': 'jovem', 'paginas': 1,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Pagina de teste (210mm x 297mm), 226kb, XPS',
         'est': 'DESKTOP-K9QUCDT', 'duplex': False, 'escala_de_cinza': False},
        {'principal': 'primeiro.html', 'data': '05/06/2023', 'hora': '09:42:41', 'user': 'jovem', 'paginas': 1,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Pagina de teste (210mm x 297mm), 226kb, XPS',
         'est': 'DESKTOP-K9QUCDT', 'duplex': False, 'escala_de_cinza': True},
        {'principal': 'quarto.html', 'data': '25/07/2023', 'hora': '11:00:00', 'user': 'Usuario', 'paginas': 10,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Apresentacao (210mm x 297mm), 500kb, PDF',
         'est': 'DESKTOP-67890', 'duplex': True, 'escala_de_cinza': True},
        {'principal': 'quarto.html', 'data': '25/07/2023', 'hora': '11:05:00', 'user': 'Usuario', 'paginas': 3,
         'copias': 2, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Apresentacao (210mm x 297mm), 150kb, PDF',
         'est': 'DESKTOP-67890', 'duplex': False, 'escala_de_cinza': False},
        {'principal': 'quarto.html', 'data': '25/07/2023', 'hora': '11:10:00', 'user': 'Usuario', 'paginas': 6,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Apresentacao (210mm x 297mm), 300kb, PDF',
         'est': 'DESKTOP-67890', 'duplex': True, 'escala_de_cinza': True},
        {'principal': 'segundo.htm', 'data': '05/06/2023', 'hora': '09:39:38', 'user': 'Usuario', 'paginas': 7,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Pagina de teste (210mm x 297mm), 226kb, XPS',
         'est': 'DESKTOP-K9QUCDT', 'duplex': True, 'escala_de_cinza': True},
        {'principal': 'segundo.htm', 'data': '05/06/2023', 'hora': '09:39:54', 'user': 'Usuario', 'paginas': 1,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Pagina de teste (210mm x 297mm), 226kb, XPS',
         'est': 'DESKTOP-K9QUCDT', 'duplex': False, 'escala_de_cinza': False},
        {'principal': 'segundo.htm', 'data': '05/06/2023', 'hora': '09:42:41', 'user': 'Usuario', 'paginas': 1,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Pagina de teste (210mm x 297mm), 226kb, XPS',
         'est': 'DESKTOP-K9QUCDT', 'duplex': False, 'escala_de_cinza': False},
        {'principal': 'terceiro.html', 'data': '05/07/2023', 'hora': '10:00:00', 'user': 'jovem', 'paginas': 8,
         'copias': 2, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Relatorio de vendas (210mm x 297mm), 300kb, PDF',
         'est': 'DESKTOP-12345', 'duplex': False, 'escala_de_cinza': True},
        {'principal': 'terceiro.html', 'data': '05/07/2023', 'hora': '10:05:00', 'user': 'jovem', 'paginas': 5,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Relatorio de vendas (210mm x 297mm), 200kb, PDF',
         'est': 'DESKTOP-12345', 'duplex': True, 'escala_de_cinza': False},
        {'principal': 'terceiro.html', 'data': '05/07/2023', 'hora': '10:10:00', 'user': 'jovem', 'paginas': 2,
         'copias': 1, 'impressora': 'Microsoft Print to PDF',
         'arquivo': 'Relatorio de vendas (210mm x 297mm), 100kb, PDF',
         'est': 'DESKTOP-12345', 'duplex': False, 'escala_de_cinza': False}]

    dados = [Dados(**dicionario) for dicionario in lista_de_dicionarios]
    visu = VisualDados(dados)
    visu.validate_dados()
    lista = visu.dataframes_para_dicionarios()

    # plt.figure(figsize=(12, 6))
    # ax = sns.barplot(data=visu.dados,
    #                  x='data_usuario',
    #                  y='total')
    #
    # ax.set(xlabel='Data e Usuário', ylabel='Total')
