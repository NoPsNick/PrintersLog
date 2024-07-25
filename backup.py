import os
import math
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from models import Dados


class Backup:
    """Classe para gerar backups em formato CSV de dados fornecidos."""

    def __init__(self, lista: List[Dados]):
        self.lista = lista

    def _criar_arq_e_pegar_a_data_atual(self, tipo: str) -> str:
        data = datetime.now().strftime('%d-%m-%Y')
        for dado in self.lista:
            filename = f".\\csvs\\{dado.principal}.csv" if tipo == 'csv' else f".\\csvs\\totals\\{dado.principal}_total_{data}.csv"
            with open(filename, "w") as csv:
                csv.write(f"Relatório feito na data: {data}\n")
                if tipo == 'csv':
                    csv.write(
                        "Data,Horario,Usuario,Paginas,Copias,Impressora,Arquivo,Tipo,Tamanho,Tipo de Impressao,Estacao,Duplex,Escala de Cinza\n")
                else:
                    csv.write("Usuario,Total\n")
        return data

    def gerar_csv(self) -> bool:
        """Gera arquivos CSV individuais para cada entrada na lista."""
        if not self.lista:
            return False

        data = self._criar_arq_e_pegar_a_data_atual(tipo="csv")

        for dado in self.lista:
            with open(f".\\csvs\\{dado.principal}.csv", "a") as csv:
                csv.write(
                    f"{dado.data},{dado.hora},{dado.user},{dado.paginas},{dado.copias},{dado.impressora},{dado.arquivo},{dado.est},{dado.duplex},{dado.escala_de_cinza}\n")

        return True

    def gerar_total(self) -> bool:
        """Gera um arquivo CSV contendo o total de páginas utilizadas por cada usuário."""
        if not self.lista:
            return False

        data = self._criar_arq_e_pegar_a_data_atual(tipo='total')
        totals, total = self.get_totals()

        for dado in totals.keys():
            with open(f".\\csvs\\totals\\{dado}_total_{data}.csv", "a") as csv:
                for pessoa, total_paginas in totals[dado].items():
                    csv.write(f"{pessoa},{total_paginas}\n")

        with open(f".\\csvs\\totals\\total_geral_{data}.csv", "w") as csv:
            csv.write(f"Relatório feito na data: {data}\nUsuario,Total\n")
            for pessoa, total_paginas in total.items():
                csv.write(f"{pessoa},{total_paginas}\n")

        return True

    def get_totals(self) -> Tuple[Optional[Dict[str, Dict[str, int]]], Optional[Dict[str, int]]]:
        """Calcula o total de páginas utilizadas por cada usuário."""
        if not self.lista:
            return None, None

        totals = {dado.principal: {dado.user: 0} for dado in self.lista}
        total = {dado.user: 0 for dado in self.lista}

        for dado in self.lista:
            paginas = math.ceil(int(dado.paginas) / 2) if dado.duplex else int(dado.paginas)
            total[dado.user] += paginas * int(dado.copias)
            totals[dado.principal][dado.user] += paginas * int(dado.copias)

        return totals, total
