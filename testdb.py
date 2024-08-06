# -*- coding: latin-1 -*-
import ast
import sqlite3

from configuration import Config
from models import Dados


class TestDB:
    def __init__(self, db_file):
        self.config = Config
        self.config.directory_check(db_file)
        self.con = sqlite3.connect(db_file)
        self.cursor = self.con.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Documentos (
                Principal TEXT,
                Data DATE,
                Hora TIME,
                User TEXT,
                Paginas INTEGER,
                Copias INTEGER,
                Impressora TEXT,
                Arquivo TEXT,
                Est TEXT,
                Duplex BOOLEAN,
                Escala_de_cinza BOOLEAN
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CustomPDFs (
                Nome TEXT PRIMARY KEY
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CustomPDFsValues (
                Nome TEXT,
                Tipo TEXT,
                Valor TEXT,
                FOREIGN KEY (Nome) REFERENCES CustomPDFs (Nome)
            )
        """)
        self.con.commit()

    def _documento_existe(self, principal, data, hora, user) -> bool:
        self.cursor.execute("""
            SELECT 1 FROM Documentos WHERE Principal = ? AND Data = ? AND Hora = ? AND User = ?
        """, (principal, data, hora, user))
        return self.cursor.fetchone() is not None

    def custompdf_existe(self, nome) -> bool:
        self.cursor.execute("SELECT 1 FROM CustomPDFs WHERE Nome = ?", (nome,))
        return self.cursor.fetchone() is not None

    def inserir_documentos(self, dados: list):
        for dado in dados:
            if self._documento_existe(dado.principal, dado.data, dado.hora, dado.user):
                continue

            self.cursor.execute("""
                        INSERT INTO Documentos (Principal, Data, Hora, User, Paginas, Copias,
                                                Impressora, Arquivo, Est, Duplex, Escala_de_cinza)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (dado.principal, dado.data, dado.hora, dado.user, dado.paginas, dado.copias,
                          dado.impressora, dado.arquivo, dado.est, dado.duplex, dado.escala_de_cinza))

            self.con.commit()

    def inserir_custompdfs(self, nome: str, pdfs: list):
        if not self.custompdf_existe(nome):
            self.cursor.execute("""
                    INSERT INTO CustomPDFs (Nome)
                    VALUES (?)
            """, (nome,))
            for dicionario in pdfs:
                for key, value in dicionario.items():
                    self.cursor.execute("""
                           INSERT INTO CustomPDFsValues (Nome, Tipo, Valor)
                           VALUES (?, ?, ?)
                    """, (nome, str(key), str(value)))
            self.con.commit()
            return True
        else:
            return False

    def buscar_documentos(self) -> list[Dados]:
        arquivos = []
        self.cursor.execute("SELECT * FROM Documentos")
        for arquivo in self.cursor.fetchall():
            arquivos.append(Dados(*arquivo).get_dictionary())
        return arquivos

    def obter_nomes(self) -> list[str]:
        self.cursor.execute("SELECT Nome FROM CustomPDFs")
        nomes = [row[0] for row in self.cursor.fetchall()]
        return nomes

    def obter_valores_por_nome(self, nome: str) -> list[dict]:
        self.cursor.execute("SELECT Tipo, Valor FROM CustomPDFsValues WHERE Nome = ?", (nome,))
        valores = [{row[0]: dict(ast.literal_eval(row[1]))} for row in self.cursor.fetchall()]
        return valores

    def obter_todos_os_nomes_e_valores(self) -> list[dict[str, list[dict]]]:
        nomes = self.obter_nomes()
        resultado = []

        for nome in nomes:
            valores = self.obter_valores_por_nome(nome)
            resultado.append({nome: valores})

        return resultado

    def fechar_conexao(self):
        self.con.close()


if __name__ == "__main__":
    db = TestDB('./dbs/banco_de_dados.db')

    print(db.obter_valores_por_nome('teste'))
