# -*- coding: latin-1 -*-
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Base


class GenericVisualDados:
    """
    Classe para visualiza��o e manipula��o de dados, podendo tamb�m inser�-los ou pegar-los em um banco de dados.
    """

    def __init__(self, dados_classe, shape,
                 dados: list[dict | pd.DataFrame | object] | pd.DataFrame = None,
                 db_url: str = 'sqlite:///./dbs/banco_de_dados.db'):
        """
        Inicializador da classe, sendo necess�rio uma classe dos dados e seu formato(shape) em DataFrame do pandas.
        :param dados_classe: Classe do dado que ser� visualizado/manipulado.
        :param shape: Formato do DataFrame pandas, para ver basta criar um DataFrame e usar o atributo '.shape' e pegar
        o segundo n�mero(df.shape[1]), onde df seria o dataframe criado.
        :param dados: Lista de objetos da classe informada, ou Lista de DataFrames do panda, ou Lista de dicion�rios e
        ou apenas um DataFrame.
        :param db_url: Url do banco de dados, caso n�o informado, ir� utilizar o sqlite no diret�rio
        './dbs/banco_de_dados.db'.
        """
        self.dados_classe = dados_classe
        self.expected_shape = shape
        self.dados = dados or []
        self.valid = False
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def _create_session(self) -> any:
        """
        Cria a sess�o para manipula��o/inser��o de dados no Banco de Dados.
        :return: A sess�o aberta.
        """
        return self.Session()

    def validar(self, df: pd.DataFrame) -> bool:
        """
        Recebe um DataFrame do pandas para valida��o.
        :param df: DataFrame do pandas.
        :return: bool(True) se foi validado; bool(False) caso haja algum problema com o par�metro df.
        """
        if isinstance(df, pd.DataFrame) and df.shape[1] == self.expected_shape:
            self.valid = True
            self.dados = df
        else:
            self.valid = False
        return self.valid

    def validate(self) -> bool:
        """
        Fazer a valida��o do par�metro dados da classe, caso n�o seja um DataFrame, transform�-lo em DataFrame.
        :return: Fun��o de validar com o DataFrame criado apartir do par�metro dados da classe ou caso j� seja um
        DataFrame a Fun��o de validar com o pr�prio par�metro dados da classe.
        """
        if not isinstance(self.dados, pd.DataFrame):
            df = pd.DataFrame([dado.__dict__ for dado in self.dados])
            return self.validar(df)
        else:
            return self.validar(self.dados)

    def buscar_no_banco_de_dados(self, db_class) -> pd.DataFrame:
        """
        Fazer a busca de todos os dados no Banco de Dados da Classe Base de Banco de Dados ORM.
        :param db_class: A classe Base de Banco de Dados que ser� pesquisada.
        :return: DataFrame pandas.
        :raise SQLAlchemyError: Caso haja algum problema de estrutura��o.
        """
        Base.metadata.create_all(self.engine)
        with self._create_session() as session:
            try:
                retorno = session.query(db_class).all()
                data = [obj.__dict__ for obj in retorno]
                for item in data:
                    item.pop('_sa_instance_state', None)
                df = pd.DataFrame(data)
                return df
            except SQLAlchemyError as e:
                raise e
            finally:
                self.close()

    def insert_new_data(self, data: pd.DataFrame, db_class) -> None:
        """
        Inserir novo dado no Banco de Dados atrav�s da Classe Base de Banco de Dados.
        :param data: Dado que ser� inserido no Banco de Dados.
        :param db_class: Classe Base do Banco de Dados.
        :raise SQLAlchemyError: Caso haja algum problema de estrutura��o.
        """
        registros = data.to_dict(orient='records')
        Base.metadata.create_all(self.engine)
        with self._create_session() as session:
            try:
                for record in registros:
                    novo_registro = db_class(**record)
                    session.add(novo_registro)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                raise e
            finally:
                self.close()

    def remove_data(self, field_name, value, db_class) -> None:
        """
        Fazer a remo��o de algum dado que seja de um Campo do Banco de Dados atrav�s da Classe Base de Banco de Dados.
        :param field_name: Nome do Campo que ser� verificado para a remo��o.
        :param value: O Valor que deseja remover.
        :param db_class: Classe Base de Banco de Dados.
        :raise SQLAlchemyError: Caso haja algum problema de estrutura��o.
        """
        with self._create_session() as session:
            try:
                registros = session.query(db_class).filter_by(**{field_name: value}).all()
                for registro in registros:
                    session.delete(registro)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                raise e
            finally:
                self.close()

    def dataframes_para_classes(self) -> list[object | None]:
        """
        Transforma o DataFrame em uma lista de objetos do par�metro dados_classe.
        :return: Lista de objetos do par�metro dados_classe.
        """
        if self.valid and isinstance(self.dados, pd.DataFrame):
            return [self.dados_classe(**row) for _, row in self.dados.iterrows()]
        return []

    def close(self):
        """
        Fechar a sess�o e a engine de manipula��o do Banco de Dados.
        """
        self.Session.remove()
        self.engine.dispose()


if __name__ == '__main__':
    pass
