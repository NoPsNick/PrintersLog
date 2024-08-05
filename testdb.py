# -*- coding: latin-1 -*-
import sqlite3

from configuration import Config
from models import Dados


class TestDB:
    def __init__(self, db_file):
        self.config = Config
        self.config.directory_check(db_file)
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
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
        self.conn.commit()

    def _documento_existe(self, principal, data, hora, user):
        self.cursor.execute("""
            SELECT 1 FROM Documentos WHERE Principal = ? AND Data = ? AND Hora = ? AND User = ?
        """, (principal, data, hora, user))
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

            self.conn.commit()

    def buscar_documentos(self):
        arquivos = []
        self.cursor.execute("SELECT * FROM Documentos")
        for arquivo in self.cursor.fetchall():
            arquivos.append(Dados(*arquivo).get_dictionary())
        return arquivos

    # def buscar_documento_por_arquivo(self, arquivo):
    #     self.cursor.execute("SELECT * FROM Documentos WHERE Arquivo=?", (arquivo,))
    #     return self.cursor.fetchone()
    #
    # def atualizar_documento(self, arquivo, novos_dados):
    #     self.cursor.execute("""
    #         UPDATE Documentos
    #         SET Principal=?, Data=?, Hora=?, User=?, Paginas=?, Copias=?,
    #             Impressora=?, Arquivo=?, Est=?, Duplex=?, Escala_de_cinza=?
    #         WHERE Arquivo=?
    #     """, (*novos_dados, arquivo))
    #     self.conn.commit()
    #
    # def deletar_documento(self, arquivo):
    #     self.cursor.execute("DELETE FROM Documentos WHERE Arquivo=?", (arquivo,))
    #     self.conn.commit()

    def fechar_conexao(self):
        self.conn.close()


# Exemplo de uso da classe DocumentoDB com a classe Dados
if __name__ == "__main__":
    db = TestDB('documentos.db')

    # Buscando todos os documentos e imprimindo-os
    documentos = db.buscar_documentos()
    print("Documentos na base de dados:")
    for documento in documentos:
        print(documento)

    # Fechando a conexão com o banco de dados
    db.fechar_conexao()
