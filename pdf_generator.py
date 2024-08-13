# -*- coding: latin-1 -*-
import datetime
import math
import re
from typing import Literal, Union

from fpdf import FPDF

from configuration import Config
from storage_manager import StorageManager
from visualdados import VisualDados


class PDFGenerator:
    def __init__(self, conteudo: dict, orientation: Literal[
        "portrait", "p", "P", "landscape", "l", "L"] = "portrait",
                 unit: str = "pt",
                 format: Union[Literal["a3", "A3", "a4", "A4", "a5", "A5", "letter", "Letter", "legal", "Legal"], tuple[
                     float, float]] = "A4"):
        self.conteudo = conteudo
        self.config = Config()
        self.formato_da_data = self.config.get_data_format()
        self.storage_manager = StorageManager()
        self.pdf = FPDF(orientation=orientation, unit=unit, format=format)
        self.pdf.add_page()
        self.contents = []
        self.primeira_font = False

    def set_font(self, family: str = "Times", style: Literal[
        "B", "I", "U", "BU", "UB", "BI", "IB", "IU", "UI", "BIU", "BUI", "IBU", "IUB", "UBI", "UIB"] = "",
                 size: int = 12):
        self.contents.append({"set_font": {"family": family, "style": style, "size": size}})
        self.primeira_font = True

    def cell(self, w: float = 0, h: float = 20, txt: str = "", border: Union[Literal[0, 1], bool, str, int] = 0,
             ln: Union[int, Literal[0, 1]] = 0, align: str = "C"):
        self.contents.append({"cell": {"w": w, "h": h, "txt": txt, "border": border, "ln": ln, "align": align}})

    def multi_cell(self, w: float, h: float = 20, txt: str = "", border: Union[Literal[0, 1], bool, str, int] = 0,
                   align: str = "J"):
        self.contents.append({"multi_cell": {"w": w, "h": h, "txt": txt, "border": border, "align": align}})

    def python_code(self, type: str = "python_code", code: str = ""):
        self.contents.append({type: {"code": code}})

    def execute_contents(self) -> dict[str, int | str]:
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
                    run = self.run_user_code(params["code"])
                    if run != "True":
                        retorno = {"codigo": 406,
                                   "msg": f"O recurso solicitado ({params['code']}) não foi encontrado ou não é um "
                                          f"recurso PYTHON."
                                          f" {run}"}
                else:
                    return {"codigo": 404, "msg": f"Não foi possível executar a função "
                                                  f"{method} com os comandos {params}."}
        return retorno

    def generate_pdf(self, filename: str) -> dict[str, int | str]:
        tentativa = self.execute_contents()
        if tentativa["codigo"] == 200:
            try:
                self.pdf.output(filename)
            except Exception as e:
                tentativa = {"codigo": 404, "msg": str(e)}
        return tentativa

    @staticmethod
    def formatar(raw_text: str) -> str:
        return "\n>>>".join(line.replace("\t", "    ") for line in raw_text.split('\n'))

    @staticmethod
    def formatar_to_copy(raw_text: str) -> str:
        return "\n".join(line.replace("\t", "    ") for line in raw_text.split('\n'))

    @staticmethod
    def format_other_types(raw_text: dict) -> str:
        lista = []
        for key, value in raw_text.items():
            if isinstance(value, (float, int)):
                lista.append(f"{key} = {value}")
            else:
                lista.append(f"{key} = '{value}'")
        text = ", ".join(lista)
        return text.replace('"', '')

    def content_to_str(self) -> list[str]:
        lista = [f"{key}: {value}" if key != "python_code" else f"{key}:\n>>>{self.formatar(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def contet_to_copy(self) -> list[str]:
        lista = [f"{key}({(self.format_other_types(value))})"
                 if key != "python_code" else f"{self.formatar_to_copy(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def is_first_command_set_font(self, code):
        if not self.primeira_font:
            # Remove possíveis comentários e espaços em branco extras
            code = re.sub(r'#.*', '', code)
            code = code.strip()

            # Encontra todos os comandos `pdf.` no código
            commands = re.findall(r'\b(set_font|cell|multi_cell)\(', code)

            if not commands:
                return True

            # Verifica se o primeiro comando é pdf.set_font
            self.primeira_font = commands[0].startswith('set_font')
        return self.primeira_font

    def execute_user_code(self, user_code: str) -> str:
        allowed_globals = {
            "conteudo": self.conteudo,
            "math": math,
            "datetime": datetime,
            "formatar_datas": self._formatar_datas,
            "truncate_text": self._truncate_text,
            "calcular_periodo": self._calcular_periodo,
            "pegar_totais": self.get_totals,
            "pdf": self.pdf,
            "formato_da_data": self.formato_da_data,
            "set_font": self.set_font,
            "cell": self.cell,
            "multi_cell": self.multi_cell
        }

        if not self.primeira_font:
            if not self.is_first_command_set_font(user_code):
                return "Erro ao executar o código: Adicione um set_font() no começo"

        try:
            exec(user_code, allowed_globals)
            return "True"
        except Exception as e:
            return f"Erro ao executar o código: {e}"

    def run_user_code(self, code: str) -> str:
        result = self.execute_user_code(code)
        return result

    def save(self, nome: str) -> bool:
        return self.json_save(nome) if self.config.get_configs().get(
            "_tipo_de_db") != "test_db" else self.db_save(nome)

    def json_save(self, nome: str) -> bool:
        if not self.check_if_name(nome):
            custom_pdfs = self.json_get()
            custom_pdfs.append({nome: self.contents})
            self.storage_manager.save_data("custom_pdfs", custom_pdfs)
            return True
        return False

    def db_save(self, nome: str) -> bool:
        visu = VisualDados(dados=self.contents)
        retorno = visu.custom_pdf_to_db(nome=nome)
        return retorno

    def get_customs(self) -> list[dict[str, list[dict]]]:
        return self.json_get() if self.config.get_configs().get(
            "_tipo_de_db") != "test_db" else self.db_get()

    def json_get(self) -> list[dict[str, list[dict]]]:
        return self.storage_manager.load_data("custom_pdfs") or []

    @staticmethod
    def db_get() -> list:
        visu = VisualDados()
        custom_pdfs = visu.pegar_todos_os_nomes()
        return custom_pdfs

    def get_custom(self, nome: str) -> bool:
        return self.get_custom_json(nome) if self.config.get_configs().get("_tipo_de_db"
                                                                           ) != "test_db" else self.get_custom_db(nome)

    def get_custom_json(self, nome: str) -> bool:
        custom_pdfs = self.json_get()
        nome = nome.lower()
        if custom_pdfs and self.check_if_name(nome):
            all_pdfs = {key.lower(): value for dicionario in custom_pdfs for key, value in dicionario.items()}
            self.contents = all_pdfs[nome]
            return True
        else:
            return False

    def get_custom_db(self, nome: str) -> bool:
        visu = VisualDados()
        custom_db = visu.pegar_pdf_por_nome(nome=nome)
        if custom_db:
            self.contents.extend(custom_db)
            return True
        return False

    def check_if_name(self, nome: str) -> bool:
        custom_pdfs = self.json_get()
        existing_names = {key.lower() for dicionario in custom_pdfs for key in dicionario}
        return nome.lower() in existing_names

    def remover(self):
        if self.contents:
            self.contents.pop()

    def get_totals(self) -> tuple[dict[str, dict[str, int]] | None, dict[str, int] | None]:
        if not self.conteudo['lista']:
            return None, None

        totals = {dado.principal: {dado.user: 0} for dado in self.conteudo['lista']}
        total = {dado.user: 0 for dado in self.conteudo['lista']}

        for dado in self.conteudo['lista']:
            paginas = math.ceil(int(dado.paginas) / 2) if dado.duplex else int(dado.paginas)
            total[dado.user] += paginas * int(dado.copias)
            totals[dado.principal][dado.user] += paginas * int(dado.copias)

        return totals, total

    @staticmethod
    def _truncate_text(pdf: FPDF, text: str, max_width: int) -> str:
        max_width -= 5
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

    def _calcular_periodo(self) -> tuple[str, str, int]:
        datas_convertidas = sorted(set(
            datetime.datetime.strptime(self.config.translate(data.data), self.formato_da_data) for data in
            self.conteudo['lista']))
        primeira_data = datas_convertidas[0]
        ultima_data = datas_convertidas[-1]
        diferenca_dias = (ultima_data - primeira_data).days + 1

        return primeira_data.strftime(self.formato_da_data), ultima_data.strftime(self.formato_da_data), diferenca_dias

    def _formatar_datas(self) -> str:
        datas = sorted(set(
            (datetime.datetime.strptime(self.config.translate(data.data), self.formato_da_data)).strftime(
                self.formato_da_data) for data in self.conteudo['lista']))
        if not datas:
            return ""
        elif len(datas) == 1:
            return datas[0]
        else:
            return ", ".join(datas[:-1]) + " e " + datas[-1]
