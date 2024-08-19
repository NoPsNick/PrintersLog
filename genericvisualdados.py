# -*- coding: latin-1 -*-
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Base


class GenericVisualDados:
    """
    Classe para visualização e manipulação de dados, podendo também inserí-los ou pegar-los em um banco de dados.
    """

    def __init__(self, dados_classe, shape,
                 dados: list[dict | pd.DataFrame | object] | pd.DataFrame = None,
                 db_url: str = 'sqlite:///./dbs/banco_de_dados.db'):
        """
        Inicializador da classe, sendo necessário uma classe dos dados e seu formato(shape) em DataFrame do pandas.
        :param dados_classe: Classe do dado que será visualizado/manipulado.
        :param shape: Formato do DataFrame pandas, para ver basta criar um DataFrame e usar o atributo '.shape' e pegar
        o segundo número(df.shape[1]), onde df seria o dataframe criado.
        :param dados: Lista de objetos da classe informada, ou Lista de DataFrames do panda, ou Lista de dicionários e
        ou apenas um DataFrame.
        :param db_url: Url do banco de dados, caso não informado, irá utilizar o sqlite no diretório
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
        Cria a sessão para manipulação/inserção de dados no Banco de Dados.
        :return: A sessão aberta.
        """
        return self.Session()

    def validar(self, df: pd.DataFrame) -> bool:
        """
        Recebe um DataFrame do pandas para validação.
        :param df: DataFrame do pandas.
        :return: bool(True) se foi validado; bool(False) caso haja algum problema com o parâmetro df.
        """
        if isinstance(df, pd.DataFrame) and df.shape[1] == self.expected_shape:
            self.valid = True
            self.dados = df
        else:
            self.valid = False
        return self.valid

    def validate(self) -> bool:
        """
        Fazer a validação do parâmetro dados da classe, caso não seja um DataFrame, transformá-lo em DataFrame.
        :return: Função de validar com o DataFrame criado apartir do parâmetro dados da classe ou caso já seja um
        DataFrame a Função de validar com o próprio parâmetro dados da classe.
        """
        if not isinstance(self.dados, pd.DataFrame):
            df = pd.DataFrame([dado.__dict__ for dado in self.dados])
            return self.validar(df)
        else:
            return self.validar(self.dados)

    def buscar_no_banco_de_dados(self, db_class) -> pd.DataFrame:
        """
        Fazer a busca de todos os dados no Banco de Dados da Classe Base de Banco de Dados ORM.
        :param db_class: A classe Base de Banco de Dados que será pesquisada.
        :return: DataFrame pandas.
        :raise SQLAlchemyError: Caso haja algum problema de estruturação.
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
        Inserir novo dado no Banco de Dados através da Classe Base de Banco de Dados.
        :param data: Dado que será inserido no Banco de Dados.
        :param db_class: Classe Base do Banco de Dados.
        :raise SQLAlchemyError: Caso haja algum problema de estruturação.
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
        Fazer a remoção de algum dado que seja de um Campo do Banco de Dados através da Classe Base de Banco de Dados.
        :param field_name: Nome do Campo que será verificado para a remoção.
        :param value: O Valor que deseja remover.
        :param db_class: Classe Base de Banco de Dados.
        :raise SQLAlchemyError: Caso haja algum problema de estruturação.
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
        Transforma o DataFrame em uma lista de objetos do parâmetro dados_classe.
        :return: Lista de objetos do parâmetro dados_classe.
        """
        if self.valid and isinstance(self.dados, pd.DataFrame):
            return [self.dados_classe(**row) for _, row in self.dados.iterrows()]
        return []

    def close(self):
        """
        Fechar a sessão e a engine de manipulação do Banco de Dados.
        """
        self.Session.remove()
        self.engine.dispose()


if __name__ == '__main__':
    pass
