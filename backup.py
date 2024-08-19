# -*- coding: latin-1 -*-
import datetime
import math
# Fiz alguns testes com esta bibliot�ca abaixo, mas ap�s ver que alguns problemas estavam ocorrendo, acabei n�o
# utilizando mais, deixei para refer�ncia, caso eu descubra o motivo, eu revejo
from typing import List, Dict, Tuple, Optional, Literal

from configuration import Config
from models import Dados


class Backup:
    """Classe para gerar backups em formato CSV de dados fornecidos."""

    def __init__(self, lista: List[Dados]):
        """
        Inicializa a classe de backup.
        :param lista: lista de Dados para opera��es de backup.
        """
        self.lista = lista
        self.config = Config()

    def _criar_arq_e_pegar_a_data_atual(self, tipo: Literal['csv', 'total']) -> str:
        """
        Cria o arquivo caso ele n�o exista e retorna a data.
        :param tipo: podendo ser 'csv' ou 'total', o csv ir� criar um csv contendo todas as informa��es e o total os totais de cada usu�rio.
        :return: data atual para nomea��o dos arquivos.
        """
        data = datetime.datetime.now().strftime('%d-%m-%Y')
        for dado in self.lista:
            filename = f".\\csvs\\{dado.principal}.csv" if tipo == 'csv' else f".\\csvs\\totals\\{dado.principal}_total_{data}.csv"
            arquivo = self.config.directory_check(filename)
            if not arquivo:
                with open(filename, "w") as csv:
                    if tipo == 'csv':
                        csv.write(
                            "principal,data,hora,user,paginas,copias,impressora,arquivo,est,"
                            "duplex,escala_de_cinza\n")
                    else:
                        csv.write("Usuario,Total\n")
        return data

    def gerar_csv(self) -> bool:
        """
        Gera arquivos CSV individuais para cada entrada na lista.
        :return: True caso tenha uma lista; False caso n�o tenha uma lista.
        """
        if not self.lista:
            return False

        self._criar_arq_e_pegar_a_data_atual(tipo="csv")
        for dado in self.lista:
            with open(f".\\csvs\\{dado.principal}.csv", "a") as csv:
                csv.write(
                    f"{dado.principal},{dado.data},{dado.hora},{dado.user},{dado.paginas},{dado.copias},"
                    f'{dado.impressora},"{dado.arquivo}",{dado.est},{dado.duplex},{dado.escala_de_cinza}\n')
        return True

    def gerar_total(self) -> bool:
        """
        Gera um arquivo CSV contendo o total de p�ginas utilizadas por cada usu�rio.
        :return: True caso tenha uma lista; False caso n�o tenha uma lista.
        """
        if not self.lista:
            return False

        data = self._criar_arq_e_pegar_a_data_atual(tipo='total')
        totals, total = self.get_totals()

        for dado in totals.keys():
            with open(f".\\csvs\\totals\\{dado}_total_{data}.csv", "a") as csv:
                for pessoa, total_paginas in totals[dado].items():
                    csv.write(f"{pessoa},{total_paginas}\n")

        with open(f".\\csvs\\totals\\total_geral_{data}.csv", "w") as csv:
            csv.write(f"Relat�rio feito na data: {data}\nUsuario,Total\n")
            for pessoa, total_paginas in total.items():
                csv.write(f"{pessoa},{total_paginas}\n")

        return True

    def get_totals(self) -> Tuple[Optional[Dict[str, Dict[str, int]]], Optional[Dict[str, int]]]:
        """
        Calcula o total de p�ginas utilizadas por cada usu�rio.
        :return: Tupla(totais, total); Totais � um dicion�rio com a chave sendo o nome do documento e o valor outro
        dicion�rio com o nome do usu�rio como chave e seu valor a quantidade de p�ginas utilizadas; Total � um
        dicion�rio com o nome do usu�rio como chave e seu valor a quantidade de p�ginas utilizadas.
        """
        if not self.lista:
            return None, None

        totals = {dado.principal: {dado.user: 0} for dado in self.lista}
        total = {dado.user: 0 for dado in self.lista}

        for dado in self.lista:
            paginas = math.ceil(int(dado.paginas) / 2) if dado.duplex else int(dado.paginas)
            total[dado.user] += paginas * int(dado.copias)
            totals[dado.principal][dado.user] += paginas * int(dado.copias)

        return totals, total
