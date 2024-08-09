# -*- coding: latin-1 -*-
import ast
import os
from glob import glob

import pandas as pd
from sqlalchemy import create_engine

from configuration import Config
from models import Dados


class VisualDados:
    def __init__(self, dados: list[dict | pd.DataFrame] | pd.DataFrame = None):
        self.dados = dados or []
        self._valid = False
        self._type = None
        self.db_url = 'sqlite:///./dbs/banco_de_dados.db'
        self.engine = create_engine(self.db_url)
        self.data_format = Config().get_data_format()

    def _validar(self, df: pd.DataFrame, tipo: str) -> bool:
        if isinstance(df, pd.DataFrame):
            if (tipo == "dados" and df.shape[1] == 11) or (tipo == "pdfs" and df.shape[1] == 3):
                self._type = tipo
                self._valid = True
                self.dados = df
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

    def validate_dados(self) -> bool:
        if not isinstance(self.dados, pd.DataFrame):
            # Converte lista de objetos Dados em DataFrame
            df = pd.DataFrame([dic.get_dictionary() for dic in self.dados])
            return self._validar(df, "dados")
        return self._validar(self.dados, "dados")

    def validate_custom_pdf(self, nome: str) -> bool:
        if not isinstance(self.dados, pd.DataFrame):
            # Converte lista de dicionários em DataFrame
            df = pd.DataFrame([{'nome': nome, 'tipo': tipo, 'valor': str(valor)}
                               for dic in self.dados for tipo, valor in dic.items()])
            return self._validar(df, "pdfs")
        return self._validar(self.dados, "pdfs")

    def dataframes_para_dicionarios(self) -> list[dict | None]:
        if self._valid and isinstance(self.dados, pd.DataFrame):
            if self._type == "pdfs":
                return [{row.iloc[1]: dict(ast.literal_eval(row.iloc[2]))} for _, row in self.dados.iterrows()]
            elif self._type == "dados":
                return [Dados(**row).get_dictionary() for _, row in self.dados.iterrows()]
        return []

    def pegar_todos_os_nomes(self) -> list[str | None]:
        pegar = self.buscar_no_banco_de_dados("CustomPDFs")
        return [row for _, row in pegar.iterrows()] if not pegar.empty else []

    @staticmethod
    def create_combined_key(df: pd.DataFrame) -> pd.DataFrame:
        return (df['principal'].astype(str) + '_' +
                df['data'].astype(str) + '_' +
                df['hora'].astype(str) + '_' +
                df['user'].astype(str))

    def pegar_documentos(self) -> list[dict | None]:
        self.dados = self.buscar_no_banco_de_dados("Documentos")
        self._validar(self.dados, "dados")
        return self.dataframes_para_dicionarios()

    def pegar_pdf_por_nome(self, nome: str) -> list[dict | None]:
        pdfs = self.buscar_no_banco_de_dados("CustomPDFs")
        valores = self.buscar_no_banco_de_dados("CustomPDFsValues")

        # Filtra o dataframe pdfs para obter as linhas onde a coluna 'nome' é igual ao nome fornecido
        pdf_filtrado = pdfs[pdfs['nome'] == nome]

        # Filtra o dataframe valores para pegar apenas as linhas onde alguma coluna contém o valor de 'pdf_filtrado'
        df = valores[valores['nome'].isin(pdf_filtrado['nome'])]

        self.dados = df
        self._validar(self.dados, "pdfs")
        return self.dataframes_para_dicionarios()

    def buscar_no_banco_de_dados(self, table_name: str) -> pd.DataFrame:
        with self.engine.connect() as connection:
            try:
                return pd.read_sql_table(table_name, connection)
            except ValueError:
                return pd.DataFrame()

    def insert_new_data(self, table_name, data):
        with self.engine.connect() as connection:
            data.to_sql(name=table_name, con=connection, if_exists='append', index=False)

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

        # Remover a coluna 'chave_combinada' antes de inserir os dados
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
    # plt.figure(figsize=(12, 6))
    # ax = sns.barplot(data=visu.dados,
    #                  x='data_usuario',
    #                  y='total')
    #
    # ax.set(xlabel='Data e Usuário', ylabel='Total')
    pass
