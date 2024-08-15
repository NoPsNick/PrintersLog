# -*- coding: latin-1 -*-
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from configuration import Config
from models import Base


class GenericVisualDados:
    def __init__(self, dados_classe, shape, tipo,
                 dados: list[dict | pd.DataFrame | object] | pd.DataFrame = None):
        self.dados_classe = dados_classe
        self.expected_shape = shape
        self.type = tipo
        self.dados = dados or []
        self.valid = False
        self.db_url = 'sqlite:///./dbs/banco_de_dados.db'
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.data_format = Config().get_data_format()

    def _create_session(self):
        return self.Session()

    def validar(self, df: pd.DataFrame, db_class) -> bool:
        if isinstance(df, pd.DataFrame) and df.shape[1] == self.expected_shape:
            self.valid = True
            self.dados = df
        else:
            self.valid = False
        return self.valid

    def validate(self, db_class):
        if not isinstance(self.dados, pd.DataFrame):
            df = pd.DataFrame([dado.__dict__ for dado in self.dados])
            return self.validar(df, db_class)
        else:
            return self.validar(self.dados, db_class)

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
                session.close()

    def insert_new_data(self, data: pd.DataFrame, db_class):
        registros = data.to_dict(orient='records')
        Base.metadata.create_all(self.engine)
        with self._create_session() as session:
            try:
                for record in registros:
                    # Convertendo a coluna 'data' para datetime.date
                    if 'data' in record and isinstance(record['data'], str):
                        record['data'] = datetime.strptime(record['data'], self.data_format).date()
                    # Convertendo a coluna 'hora' para datetime.time
                    if 'hora' in record and isinstance(record['hora'], str):
                        record['hora'] = datetime.strptime(record['hora'], "%H:%M:%S").time()

                    novo_registro = db_class(**record)
                    session.add(novo_registro)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

    def remove_data(self, field_name, value, db_class):
        with self._create_session() as session:
            try:
                registros = session.query(db_class).filter_by(**{field_name: value}).all()
                for registro in registros:
                    session.delete(registro)
                session.commit()
            except SQLAlchemyError:
                session.rollback()
            finally:
                session.close()

    def dataframes_para_classes(self) -> list[object | None]:
        if self.valid and isinstance(self.dados, pd.DataFrame):
            return [self.dados_classe(**row) for _, row in self.dados.iterrows()]
        return []


if __name__ == '__main__':
    pass
