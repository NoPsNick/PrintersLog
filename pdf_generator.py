# -*- coding: latin-1 -*-
import datetime
import math
from typing import Dict, Tuple, Optional, Literal

from fpdf import FPDF

from configuration import Config
from storage_manager import StorageManager


class PDFGenerator:
    def __init__(self, lista: list, filtros: list, orientation: Literal[
        "", "portrait", "p", "P", "landscape", "l", "L"] = "portrait",
                 unit: str = "pt",
                 format: Literal["", "a3", "A3", "a4", "A4", "a5", "A5", "letter", "Letter", "legal", "Legal"] | tuple[
                     float, float] = "A4"):
        self.lista = lista
        self.filtros = filtros
        self.config = Config()
        self.formato_da_data = self.config.get_data_format()
        self.storage_manager = StorageManager()
        self.pdf = FPDF(orientation=orientation, unit=unit, format=format)
        self.pdf.add_page()
        self.contents = []
        self.custom_pdfs = self.json_get()

    def set_font(self, family: str = "Times", style: Literal[
        "", "B", "I", "U", "BU", "UB", "BI", "IB", "IU", "UI", "BIU", "BUI", "IBU", "IUB", "UBI", "UIB"] = "",
                 size: int = 12):
        self.contents.append({"set_font": {"family": family, "style": style, "size": size}})

    def cell(self, w: float = 0, h: float = 80, txt: str = "", border: Literal[0, 1] | bool | str = 0,
             ln: int | Literal["DEPRECATED"] = "DEPRECATED", align: str = "C"):
        self.contents.append({"cell": {"w": w, "h": h, "txt": txt, "border": border, "ln": ln, "align": align}})

    def multicell(self, w: float, h: float = 80, txt: str = "", border: Literal[0, 1] | bool | str = 0,
                  align: str = "J"):
        self.contents.append({"multi_cell": {"w": w, "h": h, "txt": txt, "border": border, "align": align}})

    def python_code(self, type: str = "python_code", code: str = ""):
        self.contents.append({type: {"code": code}})

    def execute_contents(self):
        retorno = {"codigo": 200, "msg": "A solicitação foi bem-sucedida"}
        for command in self.contents:
            for method, params in command.items():
                if hasattr(self.pdf, method):
                    method_func = getattr(self.pdf, method)
                    if callable(method_func):
                        method_func(**params)
                    else:
                        retorno = {"codigo": 400, "msg": "A solicitação é inválida ou malformada."}
                elif method == "python_code":
                    if not self.run_user_code(params["code"]):
                        retorno = {"codigo": 406,
                                   "msg": f"O recurso solicitado ({params['code']}) não foi encontrado ou não é um recurso PYTHON."}
        return retorno

    def save_pdf(self, filename):
        tentativa = self.execute_contents()
        if tentativa["codigo"] == 200:
            try:
                self.pdf.output(filename)
            except OSError as e:
                tentativa = {"codigo": 404, "msg": e}
        return tentativa  # Execute all commands before saving

    @staticmethod
    def formatar(raw_text):
        structured_text = ""
        indent_level = 0
        for line in raw_text.split('\n'):
            structured_text += line.replace("\t", "    ") + "\n"
        return structured_text

    def content_to_str(self):
        lista = [f"{key}: {value}" if key != "python_code" else f"{key}: {self.formatar(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def execute_user_code(self, user_code: str):
        allowed_globals = {
            "lista": self.lista,
            "math": math,
            "datetime": datetime,
            "formatar_datas": self._formatar_datas,
            "truncate_text": self._truncate_text,
            "calcular_periodo": self._calcular_periodo,
            "pegar_totais": self.get_totals,
            "pdf": self.pdf,
            "formato": self.formato_da_data,
            "filtros": self.filtros,
            "set_font": self.set_font,
            "cell": self.cell,
            "multicell": self.multicell
        }

        try:
            exec(user_code, allowed_globals)
            return "True"
        except Exception as e:
            return f"Erro ao executar o código do usuário: {e}"

    def get_totals(self) -> Tuple[Optional[Dict[str, Dict[str, int]]], Optional[Dict[str, int]]]:
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
        datas_convertidas = list(set([datetime.datetime.strptime(
            self.config.translate(data.data), self.formato_da_data) for data in self.lista]))
        datas_convertidas.sort()
        primeira_data = datas_convertidas[0]
        ultima_data = datas_convertidas[-1]
        diferenca_dias = (ultima_data - primeira_data).days + 1

        return primeira_data.strftime(self.formato_da_data), ultima_data.strftime(
            self.formato_da_data), diferenca_dias

    def _formatar_datas(self):
        datas = list(set([(datetime.datetime.strptime(
            self.config.translate(data.data), self.formato_da_data)).strftime(self.formato_da_data)
                          for data in self.lista]))
        if len(datas) == 0:
            return ""
        elif len(datas) == 1:
            return f"{datas[0]}"
        else:
            return ", ".join(datas[:-1]) + " e " + datas[-1]

    def run_user_code(self, code):
        result = self.execute_user_code(code)
        if result != "True":
            return False
        return True

    def json_save(self, name):
        if not self.check_if_name(name):
            custom_pdfs = self.json_get()
            custom_pdfs.append({name: self.contents})
            self.storage_manager.save_data("custom_pdfs", custom_pdfs)
            return True
        else:
            return False

    def json_get(self):
        custom_pdfs = self.storage_manager.load_data("custom_pdfs") or {}
        return list(custom_pdf for custom_pdf in custom_pdfs)

    def get_custom(self, name):
        custom_pdfs = self.json_get()
        name = name.lower()
        if custom_pdfs and self.check_if_name(name):
            all_pdfs = {key.lower(): value for dicionario in custom_pdfs for key, value in dicionario.items()}
            self.contents = all_pdfs[name]
            return True
        else:
            return False

    def check_if_name(self, name):
        custom_pdfs = self.json_get()
        existing_names = {key.lower() for dicionario in custom_pdfs for key in dicionario}
        return name.lower() in existing_names

    def remover(self):
        if self.contents:
            del self.contents[-1]
