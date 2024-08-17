# -*- coding: latin-1 -*-
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Base


class GenericVisualDados:
    def __init__(self, dados_classe, shape,
                 dados: list[dict | pd.DataFrame | object] | pd.DataFrame = None):
        self.dados_classe = dados_classe
        self.expected_shape = shape
        self.dados = dados or []
        self.valid = False
        self.db_url = 'sqlite:///./dbs/banco_de_dados.db'
        self.engine = create_engine(self.db_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def _create_session(self):
        return self.Session()

    def validar(self, df: pd.DataFrame) -> bool:
        if isinstance(df, pd.DataFrame) and df.shape[1] == self.expected_shape:
            self.valid = True
            self.dados = df
        else:
            self.valid = False
        return self.valid

    def validate(self):
        if not isinstance(self.dados, pd.DataFrame):
            df = pd.DataFrame([dado.__dict__ for dado in self.dados])
            return self.validar(df)
        else:
            return self.validar(self.dados)

    def buscar_no_banco_de_dados(self, db_class) -> pd.DataFrame:
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
    def insert_new_data(self, data: pd.DataFrame, db_class):
        registros = data.to_dict(orient='records')
        Base.metadata.create_all(self.engine)
        with self._create_session() as session:
            try:
                for record in registros:
                    novo_registro = db_class(**record)
                    session.add(novo_registro)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                self.close()

    def remove_data(self, field_name, value, db_class):
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
        if self.valid and isinstance(self.dados, pd.DataFrame):
            return [self.dados_classe(**row) for _, row in self.dados.iterrows()]
        return []

    def close(self):
        self.Session.remove()
        self.engine.dispose()

if __name__ == '__main__':
    pass
