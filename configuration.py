# -*- coding: latin-1 -*-
import copy
import json
import os
import re
from datetime import datetime, timedelta


class Config:
    """
    Classe para configura��o do aplicativo principal.
    """
    field_names = ["data", "user", "impressora", "est", "duplex", "escala_de_cinza"]

    def __init__(self, json_file='./jsons/config.json'):
        self.json_file = json_file
        self.estilo_padrao = [
            {
                "python_code": {
                    "code": "pdf.set_font(family=\"Times\", style=\"B\", size=24)\ndata = datetime.date.today("
                            ")\npdf.cell(w=0, h=80, txt=\"Relat\u00f3rio das impress\u00f5es\", border=1,"
                            "ln=1, align=\"C\")\n# Data da cria\u00e7\u00e3o do relat\u00f3rio\npdf.set_font("
                            "family=\"Times\", style=\"B\", size=14)\npdf.cell(w=200, h=20, txt=\"Data da "
                            "cria\u00e7\u00e3o do relat\u00f3rio: \", border=1)\npdf.set_font(family=\"Times\", "
                            "style=\"\", size=12)\npdf.cell(w=0, h=20, txt=data.strftime(formato_da_data), "
                            "border=1, ln=1)\npdf.cell(w=0, h=5, txt=\"\", border=0, ln=1)\n# Datas que estiveram "
                            "no relat\u00f3rio\ndatas_formatadas = formatar_datas()\npdf.set_font("
                            "family=\"Times\", style=\"B\", size=12)\npdf.cell(w=100, h=15, txt=\"Datas do "
                            "relat\u00f3rio: \", border=1)\npdf.set_font(family=\"Times\", style=\"\", "
                            "size=7)\npdf.multi_cell(w=0, h=15, txt=str(datas_formatadas), border=1)\npdf.cell("
                            "w=0, h=5, txt=\"\", border=0, ln=1)\n# Primeira, \u00faltima data e quantos dias "
                            "entre elas\nprimeira_data, ultima_data, diferenca_dias = calcular_periodo("
                            ")\npdf.set_font(family=\"Times\", style=\"B\", size=12)\npdf.cell(w=200, h=20, "
                            "txt=\"Primeira Data e \u00daltima Data: \", border=1)\npdf.set_font("
                            "family=\"Times\", style=\"\", size=7)\npdf.cell(w=0, h=20, txt=str(\" e \".join(["
                            "primeira_data, ultima_data])), border=1, ln=1)\npdf.cell(w=0, h=5, txt=\"\", "
                            "border=0, ln=1)\npdf.set_font(family=\"Times\", style=\"B\", size=12)\npdf.cell("
                            "w=200, h=20, txt=\"Quantidade de dias do relat\u00f3rio: \", "
                            "border=1)\npdf.set_font(family=\"Times\", style=\"\", size=7)\npdf.cell(w=0, h=20, "
                            "txt=str(diferenca_dias), border=1, ln=1)\npdf.cell(w=0, h=5, txt=\"\", border=0, "
                            "ln=1)\n# Cabe\u00e7alho\npdf.set_font(family=\"Times\", style=\"B\", "
                            "size=7)\npdf.cell(w=60, h=10, txt=\"Data\", border=1)\npdf.cell(w=60, h=10, "
                            "txt=\"Usu\u00e1rio\", border=1)\npdf.cell(w=20, h=10, txt=\"P\u00e1g\", "
                            "border=1)\npdf.cell(w=20, h=10, txt=\"C\u00f3p\", border=1)\npdf.cell(w=20, h=10, "
                            "txt=\"Dup\", border=1)\npdf.cell(w=25, h=10, txt=\"Total\", border=1)\npdf.cell(w=0, "
                            "h=10, txt=\"Impressora, arquivo impresso, esta\u00e7\u00e3o, escala de cinza e nome "
                            "do log\", border=1, ln=1)\n# Dados\ntotal = 0\nfor dado in conteudo['lista']:\n    "
                            "paginas ="
                            "math.ceil(int(dado.paginas) / 2) if dado.duplex else int(dado.paginas)\n    total += "
                            "paginas * int(dado.copias)\n    pdf.set_font(family=\"Times\", style=\"B\", "
                            "size=6)\n    data_atual = dado.data\n    pdf.cell(w=60, h=10, txt=str(data_atual + "
                            "\" \" + dado.hora), border=1)\n    pdf.cell(w=60, h=10, txt=str(dado.user), "
                            "border=1)\n    pdf.cell(w=20, h=10, txt=str(dado.paginas), border=1)\n    pdf.cell("
                            "w=20, h=10, txt=str(dado.copias), border=1)\n    pdf.set_font(family=\"Times\", "
                            "style=\"B\", size=5)\n    duplex, escala_de_cinza = \"Sim\" if dado.duplex else "
                            "\"N\u00e3o\", \"Com Escala de Cinza\" if dado.escala_de_cinza else \"Normal\"\n    "
                            "pdf.cell(w=20, h=10, txt=duplex, border=1)\n    pdf.set_font(family=\"Times\", "
                            "style=\"B\", size=7)\n    pdf.cell(w=25, h=10, txt=str(total), border=1)\n    "
                            "pdf.set_font(family=\"Times\", style=\"B\", size=4)\n    text = dado.impressora + "
                            "\", \" + dado.arquivo + \", \" + dado.est + \", \" + escala_de_cinza + \" e \" + "
                            "dado.principal\n    impressora_arquivo_est = truncate_text(pdf, str(text), "
                            "1000)\n    pdf.multi_cell(w=0, h=10, txt=str(impressora_arquivo_est), border=1)\n# "
                            "Cabe\u00e7alho\npdf.set_font(family=\"Times\", style=\"B\", size=12)\npdf.cell(w=90, "
                            "h=20, txt=\"Total de folhas: \", border=1)\n# Total de folhas\npdf.cell(w=0, h=20, "
                            "txt=str(total), border=1, ln=1)\n# Cabe\u00e7alho\npdf.cell(w=0, h=5, txt=\"\", "
                            "border=0, ln=1)\npdf.set_font(family=\"Times\", style=\"B\", size=12)\npdf.cell("
                            "w=60, h=20, txt=\"Usu\u00e1rio\", border=1)\npdf.cell(w=0, h=20, txt=\"Total\", "
                            "border=1, ln=1)\n# Total dos usu\u00e1rios\ntotais, total = pegar_totais()\nfor user "
                            "in total.keys():\n    pdf.set_font(family=\"Times\", style=\"B\", size=7)\n    "
                            "pdf.cell(w=60, h=20, txt=str(user), border=1)\n    pdf.cell(w=0, h=20, "
                            "txt=str(total[user]), border=1, ln=1)\n# Filtros\nif conteudo['filtros']:\n    pdf.cell("
                            "w=0,"
                            "h=5, txt=\"\", border=0, ln=1)\n    # Cabe\u00e7alho\n    pdf.set_font("
                            "family=\"Times\", style=\"B\", size=7)\n    pdf.cell(w=75, h=10, txt=\"Filtros "
                            "utilizados:\", border=1)\n    texto = \"\"\n    for field, rules in conteudo["
                            "'filtros'].items("
                            "):\n        includes = \",\".join(rules.get('include', []))\n        excludes = \","
                            "\".join(f\"-{item}\" for item in rules.get('exclude', []))\n        campo = f\"{"
                            "field}: {includes}{',' if includes and excludes else ''}{excludes}\"\n        if "
                            "includes or excludes:  # Adiciona campo apenas se h\u00e1 conte\u00fado a ser "
                            "adicionado\n            texto = f\"{texto}, {campo}\" if texto else campo\n    "
                            "pdf.set_font(family=\"Times\", style=\"B\", size=5)\n    pdf.multi_cell(w=0, h=10, "
                            "txt=texto, border=1)"
                }
            }
        ]
        self.read_configs()

    def read_configs(self) -> None:
        """
        Ler o documento 'cofing.json' e extra�r suas informa��es de configura��es do aplicativo, caso ele n�o exista,
        setar as configura��es padr�es e salva-las usando a fun��o 'save_configs'.
        """
        try:
            with open(self.json_file, 'r') as file:
                config = json.load(file)
                self._traduzir = config.get('_traduzir', {
                    "janeiro": "January",
                    "fevereiro": "February",
                    "mar�o": "March",
                    "abril": "April",
                    "maio": "May",
                    "junho": "June",
                    "julho": "July",
                    "agosto": "August",
                    "setembro": "September",
                    "outubro": "October",
                    "novembro": "November",
                    "dezembro": "December"
                })
                self._traduzir_inverso = config.get('_traduzir_inverso', {v.lower(): k.title()
                                                                          for k, v in self._traduzir.items()})
                self._tipo_de_db = config.get('_tipo_de_db', '')
                self._printers_path = config.get('_printers_path', '')
                self._filters = config.get('_filters', {})
                self._data_format = config.get('_data_format', '%d/%m/%Y')
                self._default_pdf_style = config.get('_default_pdf_style', self.estilo_padrao)
        except FileNotFoundError:
            # Default values if config file does not exist
            self._traduzir = {
                "janeiro": "January",
                "fevereiro": "February",
                "mar�o": "March",
                "abril": "April",
                "maio": "May",
                "junho": "June",
                "julho": "July",
                "agosto": "August",
                "setembro": "September",
                "outubro": "October",
                "novembro": "November",
                "dezembro": "December"
            }
            self._traduzir_inverso = {v.lower(): k.title() for k, v in self._traduzir.items()}
            self._tipo_de_db = "test_db"
            self._printers_path = ".\\printers\\"
            self._filters = {field: {"include": [], "exclude": []} for field in self.field_names}
            self._filters["duplex"]["include"] = ["True", "False"]
            self._filters["escala_de_cinza"]["include"] = ["True", "False"]
            self._data_format = '%d/%m/%Y'
            self._default_pdf_style = self.estilo_padrao
            self.save_config()

    def save_config(self) -> None:
        """
        Salvar os par�metros da classe no arquivo 'config.json', em caso dele n�o existir, ele ser� criado atrav�s da
        fun��o 'directory_check'.
        """
        config = {
            '_traduzir': self._traduzir,
            '_traduzir_inverso': self._traduzir_inverso,
            '_tipo_de_db': self._tipo_de_db,
            '_printers_path': self._printers_path,
            '_filters': self._filters,
            '_data_format': self._data_format,
            '_default_pdf_style': self._default_pdf_style
        }
        self.directory_check(self.json_file)
        with open(self.json_file, 'w') as file:
            json.dump(config, file, indent=4)

    def alter_filter(self, new_filter: dict[str, dict[str, set | list]]) -> None:
        """
        Altera os filtros da configura��o.
        :param new_filter: Dicion�rio contendo os filtros.
        """
        self._filters = new_filter

    def translate(self, data) -> str:
        """
        Traduz a data para o formato adequado.
        :param data: Data que ser� traduzida.
        :return: Data traduzida.
        """
        return re.sub('|'.join(self._traduzir.keys()),
                      lambda x: self._traduzir[x.group().lower()],
                      data,
                      flags=re.IGNORECASE)

    def translate_back(self, data) -> str:
        """
        Traduz a data de volta para o formato original.
        :param data: Data que j� foi traduzida.
        :return: Data no formato original.
        """
        return re.sub('|'.join(self._traduzir_inverso.keys()),
                      lambda x: self._traduzir_inverso[x.group().lower()],
                      data,
                      flags=re.IGNORECASE)

    def get_configs(self) -> dict:
        """
        Retorna os par�metros da classe.
        :return: retorna o dicion�rio para tradu��es, o tipo do banco de dados, o caminho padr�o dos logs para leitura,
        os filtros, e o formato padr�o de data.
        """
        return {
            "_traduzir": self._traduzir,
            "_tipo_de_db": self._tipo_de_db,
            '_printers_path': self._printers_path,
            '_filters': self._filters,
            '_data_format': self._data_format
        }

    def get_default_pdf_style(self) -> list:
        """
        Retorna os estilo de PDF padr�o.
        :return: Uma lista contendo v�rios dicion�rio para montagem do estilo de PDF padr�o.
        """
        return self._default_pdf_style

    def alter_translations(self, new_translations: dict) -> None:
        """
        AVISO! N�O UTILIZAR CASO N�O NECESS�RIO, POIS AFETA A APLICA��O INTEIRA.
        Altera o dicion�rio de tradu��es para caso esteja ocorrendo problemas de localiza��o.
        :param new_translations: Dicion�rio novo de tradu��es.
        """
        self._traduzir = new_translations
        self._traduzir_inverso = {v.lower(): k.title() for k, v in self._traduzir.items()}

    def get_filter(self) -> dict[str, dict[str, set | list]]:
        """
        Pegar os filtros. Include seriam todos que voc� deseja pegar e os Exclude os que N�O quer pegar.
        :return: Dicion�rio de Include e Exclude de cada filtro.
        """
        return self._filters

    def _format_date_ranges(self, dates: dict[str, dict[str, set | list]]) -> list[str]:
        """
        Recebe o filtro das datas Include ou Exclude e o retorna compactado.
        :param dates: Dicion�rio contendo o Include ou Exclude das datas para compactar-lo.
        :return: Lista de strings.
        """
        if not dates:
            return []

        dates = sorted([datetime.strptime(date, self._data_format) for date in dates])
        grouped_dates = []
        temp_group = [dates[0]]

        for i in range(1, len(dates)):
            if dates[i] == dates[i - 1] + timedelta(days=1):
                temp_group.append(dates[i])
            else:
                grouped_dates.append(temp_group)
                temp_group = [dates[i]]
        grouped_dates.append(temp_group)

        result = []
        for group in grouped_dates:
            if len(group) == 1:
                result.append(f"{group[0].strftime(self._data_format)}")
            else:
                result.append(f"{group[0].strftime(self._data_format)} at� {group[-1].strftime(self._data_format)}")

        return result

    def get_show_filter(self) -> dict[str, dict[str, set | list]]:
        """
        Devolve todos os dicion�rios, por�m com o das datas compactadas.
        :return: Dicion�rio com os filtros da data compactados.
        """
        dicionario = copy.deepcopy(self._filters)
        datas_include = dicionario['data']['include']
        datas_exclude = dicionario['data']['exclude']

        include_ranges = self._format_date_ranges(datas_include)
        exclude_ranges = self._format_date_ranges(datas_exclude)

        dicionario['data']['include'] = include_ranges
        dicionario['data']['exclude'] = exclude_ranges

        return dicionario

    def get_data_format(self) -> str:
        return str(self._data_format)

    @staticmethod
    def directory_check(directory) -> bool:
        """
        Ir� checar se existe o diret�rio, ir� cri�-lo caso n�o exista,
        :param directory: Caminho do diret�rio(arquivo, pasta...), ser� criado caso n�o exista.
        :return: bool(True): Caso o diret�rio exista; bool(False): Caso o diret�rio n�o exista.
        """
        directory = os.path.dirname(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
            return False
        return True


if __name__ == '__main__':
    # Config().save_config()
    pass
