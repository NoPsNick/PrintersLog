# -*- coding: latin-1 -*-
import datetime
import math
# Fiz alguns testes com esta bibliotéca abaixo, mas após ver que alguns problemas estavam ocorrendo, acabei não
# utilizando mais, deixei para referência, caso eu descubra o motivo, eu revejo
from typing import List, Dict, Tuple, Optional

from fpdf import FPDF

from configuration import Config
from models import Dados


class Backup:
    """Classe para gerar backups em formato CSV de dados fornecidos."""

    def __init__(self, lista: List[Dados]):
        self.lista = lista
        self.config = Config()

    def _criar_arq_e_pegar_a_data_atual(self, tipo: str) -> str:
        data = datetime.datetime.now().strftime('%d-%m-%Y')
        for dado in self.lista:
            filename = f".\\csvs\\{dado.principal}.csv" if tipo == 'csv' else f".\\csvs\\totals\\{dado.principal}_total_{data}.csv"
            self.config.directory_check(filename)
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

        self._criar_arq_e_pegar_a_data_atual(tipo="csv")

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

    @staticmethod
    def _truncate_text(pdf, text: str, max_width: int):
        max_width = max_width - 5
        ellipsis = "..."
        text_width = pdf.get_string_width(text)
        ellipsis_width = pdf.get_string_width(ellipsis)

        if text_width <= max_width:
            return text
        else:
            while text_width + ellipsis_width > max_width:
                text = text[:-1]
                text_width = pdf.get_string_width(text)
            return text + ellipsis

    def _calcular_periodo(self):
        # Converte strings de datas em objetos datetime
        datas_convertidas = list(set([datetime.datetime.strptime(
            self.config.translate(data.data), self.config.get_data_format()) for data in self.lista]))

        # Ordena as datas
        datas_convertidas.sort()

        # Obtém a primeira e a última data
        primeira_data = datas_convertidas[0]
        ultima_data = datas_convertidas[-1]

        # Calcula a diferença em dias entre a primeira e a última data
        diferenca_dias = (ultima_data - primeira_data).days + 1

        return primeira_data.strftime(self.config.get_data_format()), ultima_data.strftime(
            self.config.get_data_format()), diferenca_dias

    def _formatar_datas(self):
        # Pega as datas da lista sem duplicatas, também transformando-as em outro formato
        datas = list(set([(datetime.datetime.strptime(
            self.config.translate(data.data), self.config.get_data_format())).strftime(self.config.get_data_format())
                          for data in self.lista]))
        if len(datas) == 0:
            datas_formatadas = ""
            return datas_formatadas
        elif len(datas) == 1:
            datas_formatadas = f"{datas[0]}"
            return datas_formatadas
        else:
            datas_formatadas = ", ".join(datas[:-1]) + " e " + datas[-1]
            return datas_formatadas

    def to_pdf(self, filtros: dict = None):
        data = datetime.date.today()
        pdf = FPDF(orientation="P", unit="pt", format="A4")
        pdf.add_page()
        pdf.set_font(family="Times", style="B", size=24)
        pdf.cell(w=0, h=80, txt="Relatório das impressões", border=1, ln=1, align="C")
        # Data da criação do relatório
        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=200, h=20, txt="Data da criação do relatório: ", border=1)
        pdf.set_font(family="Times", style="", size=12)
        pdf.cell(w=0, h=20, txt=data.strftime(self.config.get_data_format()), border=1, ln=1)
        pdf.cell(w=0, h=5, txt="", border=0, ln=1)
        # Datas que estiveram no relatório
        datas_formatadas = self._formatar_datas()
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=100, h=15, txt="Datas do relatório: ", border=1)
        pdf.set_font(family="Times", style="", size=7)
        pdf.multi_cell(w=0, h=15, txt=str(datas_formatadas), border=1)
        pdf.cell(w=0, h=5, txt="", border=0, ln=1)
        # Primeira, última data e quantos dias entre elas
        primeira_data, ultima_data, diferenca_dias = self._calcular_periodo()
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=200, h=20, txt="Primeira Data e Última Data: ", border=1)
        pdf.set_font(family="Times", style="", size=7)
        pdf.cell(w=0, h=20, txt=str(" e ".join([primeira_data, ultima_data])), border=1, ln=1)
        pdf.cell(w=0, h=5, txt="", border=0, ln=1)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=200, h=20, txt="Quantidade de dias do relatório: ", border=1)
        pdf.set_font(family="Times", style="", size=7)
        pdf.cell(w=0, h=20, txt=str(diferenca_dias), border=1, ln=1)
        pdf.cell(w=0, h=5, txt="", border=0, ln=1)
        # Cabeçalho
        pdf.set_font(family="Times", style="B", size=7)
        pdf.cell(w=60, h=10, txt="Data", border=1)
        pdf.cell(w=60, h=10, txt="Usuário", border=1)
        pdf.cell(w=20, h=10, txt="Pág", border=1)
        pdf.cell(w=20, h=10, txt="Cóp", border=1)
        pdf.cell(w=20, h=10, txt="Dup", border=1)
        pdf.cell(w=25, h=10, txt="Total", border=1)
        pdf.cell(w=0, h=10, txt="Impressora, arquivo impresso, estação, escala de cinza e nome do log", border=1, ln=1)
        # Dados
        total = 0
        for dado in self.lista:
            paginas = math.ceil(int(dado.paginas) / 2) if dado.duplex else int(dado.paginas)
            total += paginas * int(dado.copias)
            pdf.set_font(family="Times", style="B", size=6)
            data_atual = dado.data
            pdf.cell(w=60, h=10, txt=str(data_atual + " " + dado.hora), border=1)
            pdf.cell(w=60, h=10, txt=str(dado.user), border=1)
            pdf.cell(w=20, h=10, txt=str(dado.paginas), border=1)
            pdf.cell(w=20, h=10, txt=str(dado.copias), border=1)
            pdf.set_font(family="Times", style="B", size=5)
            duplex, escala_de_cinza = "Sim" if dado.duplex else "Não", "Com Escala de Cinza" if dado.escala_de_cinza else "Normal"
            pdf.cell(w=20, h=10, txt=duplex, border=1)
            pdf.set_font(family="Times", style="B", size=7)
            pdf.cell(w=25, h=10, txt=str(total), border=1)
            pdf.set_font(family="Times", style="B", size=4)
            text = dado.impressora + ", " + dado.arquivo + ", " + dado.est + ", " + escala_de_cinza + " e " + dado.principal
            impressora_arquivo_est = self._truncate_text(pdf, str(text), 1000)
            pdf.multi_cell(w=0, h=10, txt=str(impressora_arquivo_est), border=1)
        # Cabeçalho
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=90, h=20, txt="Total de folhas: ", border=1)
        # Total de folhas
        pdf.cell(w=0, h=20, txt=str(total), border=1, ln=1)
        # Cabeçalho
        pdf.cell(w=0, h=5, txt="", border=0, ln=1)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.cell(w=60, h=20, txt="Usuário", border=1)
        pdf.cell(w=0, h=20, txt="Total", border=1, ln=1)
        # Total dos usuários
        totais, total = self.get_totals()
        for user in total.keys():
            pdf.set_font(family="Times", style="B", size=7)
            pdf.cell(w=60, h=20, txt=str(user), border=1)
            pdf.cell(w=0, h=20, txt=str(total[user]), border=1, ln=1)
        # Filtros
        if filtros:
            pdf.cell(w=0, h=5, txt="", border=0, ln=1)
            # Cabeçalho
            pdf.set_font(family="Times", style="B", size=7)
            pdf.cell(w=75, h=10, txt="Filtros utilizados:", border=1)
            texto = ""
            for field, rules in filtros.items():
                includes = ",".join(rules.get('include', []))
                excludes = ",".join(f"-{item}" for item in rules.get('exclude', []))
                campo = f"{field}: {includes}{',' if includes and excludes else ''}{excludes}"
                if includes or excludes:  # Adiciona campo apenas se há conteúdo a ser adicionado
                    texto = f"{texto}, {campo}" if texto else campo
            pdf.set_font(family="Times", style="B", size=5)
            pdf.cell(w=0, h=10, txt=texto, border=1, ln=1)
        diretorio = f"./pdfs/{data.strftime('%d-%m-%Y')}.pdf"
        self.config.directory_check(diretorio)
        pdf.output(name=diretorio)
