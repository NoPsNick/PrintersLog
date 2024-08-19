# -*- coding: latin-1 -*-
import datetime
import math
import re
from typing import Literal, Union

from fpdf import FPDF


class PDFGenerator:
    """
    Gerador de PDFs dinâmicos.
    """

    def __init__(self, conteudo: dict,
                 orientation: Literal["portrait", "p", "P", "landscape", "l", "L"] = "portrait",
                 unit: str = "pt",
                 format: Union[Literal["a3", "A3", "a4", "A4", "a5", "A5", "letter", "Letter", "legal", "Legal"], tuple[
                     float, float]] = "A4",
                 allowed_globals: dict = None):
        """
        Inicializador da classe.
        :param conteudo: Dicionário, onde a chave é o nome que deseja ter e o valor os dados que podem ser acessados.
        :param orientation: Tipo do PDF.
        :param unit: Tamanho das letras.
        :param format: Formato da folha.
        :param allowed_globals: CUIDADO! Dicionário contendo funções que poderão ser utilizadas ao tentar executar
        códigos python do usuário. Aviso: utilize com cuidado, pois dar funções do python que possam comprometer a
        aplicação poderá causar danos irreversíveis. As padrões serão: o conteúdo, math para utilizar funções de
        matemática, datetime para datas, pdf para manipular o PDF, set_font para setar a fonte, cell para adiconar uma
        célula e multi_cell para adicionar uma célula que pode ter mais de uma linha.
        """
        self.conteudo = conteudo
        self.pdf = FPDF(orientation=orientation, unit=unit, format=format)
        self.pdf.add_page()
        self.contents = []
        self.primeira_font = False
        default_allowed = {
            "conteudo": self.conteudo,
            "math": math,
            "datetime": datetime,
            "pdf": self.pdf,
            "set_font": self.set_font,
            "cell": self.cell,
            "multi_cell": self.multi_cell
        }
        default_allowed.update(allowed_globals or {})
        self.allowed_globals = default_allowed

    def set_font(self, family: str = "Arial", style: Literal[
        "B", "I", "U", "BU", "UB", "BI", "IB", "IU", "UI", "BIU", "BUI", "IBU", "IUB", "UBI", "UIB"] = "",
                 size: int = 12) -> None:
        """
        Setar a fonte da escrita dentro do PDF nas linhas seguintes e também permitir outras funções caso seja a
        primeira vez usando.
        :param family: Família da fonte.
        :param style: Estilo da fonte.
        :param size: Tamanho da fonte.
        """
        self.contents.append({"set_font": {"family": family, "style": style, "size": size}})
        self.primeira_font = True

    def cell(self, w: float = 0, h: float = 20, txt: str = "", border: Union[Literal[0, 1], bool, str, int] = 0,
             ln: Union[int, Literal[0, 1]] = 0, align: str = "C") -> None:
        """
        Adicionar uma célula no PDF.
        :param w: Tamanho da largura da célula.
        :param h: Tamanho da altura da célula.
        :param txt: Texto dentro da célula.
        :param border: Se terá borda ou não.
        :param ln: Se será a última célula da linha.
        :param align: Alinhamento do texto.
        """
        self.contents.append({"cell": {"w": w, "h": h, "txt": txt, "border": border, "ln": ln, "align": align}})

    def multi_cell(self, w: float, h: float = 20, txt: str = "", border: Union[Literal[0, 1], bool, str, int] = 0,
                   align: str = "J") -> None:
        """
        Adicionar uma célula múltipla no PDF.
        Age igual uma célula, porém ela irá para a próxima linha caso a largura da célula exceda o limite da largura do
        PDF e as próximas células sempre serão na próxima linha.
        :param w: Tamanho da largura de célula.
        :param h: Tamanho da altura da célula.
        :param txt: Texto dentro da célula.
        :param border: Se terá borda ou não.
        :param align: Alinhamento do texto.
        """
        self.contents.append({"multi_cell": {"w": w, "h": h, "txt": txt, "border": border, "align": align}})

    def python_code(self, code: str = "") -> None:
        """
        Adicionar uma codificação em formato PYTHON.
        :param code: Código em formato PYTHON.
        """
        self.contents.append({"python_code": {"code": code}})

    def execute_contents(self) -> dict[str, int | str]:
        """
        Criar o PDF através do conteúdo da classe.
        :return: Dicionário contendo duas chaves e dois valores, a primeira chave será 'codigo' e seu valor um número,
        a segunda chave será 'msg' e seu valor a mensagem.
        Código: 200 Mensagem: A solicitação foi bem-sucedida
        Código: 400 Mensagem: A solicitação é inválida ou malformada.
        Código: 406 Mensagem: Erro ao tentar executar alguma função ou código.
        Código: 404 Mensagem: Não encontrado.
        """
        retorno = {"codigo": 200, "msg": "A solicitação foi bem-sucedida."}
        for command in self.contents:
            for method, params in command.items():
                if hasattr(self.pdf, method):
                    try:
                        method_func = getattr(self.pdf, method)
                        if callable(method_func):
                            method_func(**params)
                        else:
                            retorno = {"codigo": 400, "msg": "A solicitação é inválida ou malformada."}
                    except Exception as e:
                        retorno = {"codigo": 406, "msg": f"O seguinte erro ocorreu durante a tentativa de usar a"
                                                         f"função {str(method)} com os parâmetros {str(params)}:"
                                                         f" {e}"}
                elif method == "python_code":
                    run = self.execute_user_code(params["code"])
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
        """
        Irá gerar o PDF com o nome dado.
        :param filename: Nome que será gerado
        :return: Dicionário contendo o codigo e a msg ao tentar gerar o pdf.
        """
        tentativa = self.execute_contents()
        if tentativa["codigo"] == 200:
            try:
                self.pdf.output(filename)
            except Exception as e:
                tentativa = {"codigo": 404, "msg": str(e)}
        return tentativa

    @staticmethod
    def formatar(raw_text: str) -> str:
        """
        Formata o texto para visualização.
        :param raw_text: Texto que será formatado.
        :return: Texto formatado.
        """
        return "\n>>>".join(line.replace("\t", "    ") for line in raw_text.split('\n'))

    @staticmethod
    def formatar_to_copy(raw_text: str) -> str:
        """
        Formata o texto de código python para que consiga colar e executá-lo em forma de código.
        :param raw_text: Texto que será formatado.
        :return: Texto formatado.
        """
        return "\n".join(line.replace("\t", "    ") for line in raw_text.split('\n'))

    @staticmethod
    def format_other_types(raw_text: dict) -> str:
        """
        Formata o texto que não é de código python, porém para que seja possível colar e executá-lo como um código
        python.
        :param raw_text: Dicionário com a chave sendo o comando e o valor as entradas.
        :return: str Texto formatado.
        """
        lista = []
        for key, value in raw_text.items():
            if isinstance(value, (float, int)):
                lista.append(f"{key} = {value}")
            else:
                lista.append(f"{key} = '{value}'")
        text = ", ".join(lista)
        return text.replace('"', '')

    def content_to_str(self) -> list[str]:
        """
        Transforma o conteúdo do PDF em uma lista de Strings.
        :return: Lista de strings.
        """
        lista = [f"{key}: {value}" if key != "python_code" else f"{key}:\n>>>{self.formatar(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def contet_to_copy(self) -> list[str]:
        """
        Transforma o conteúdo em uma lista de Strings que seja possível colar para ser executado como código python.
        :return: Lista de strings.
        """
        lista = [f"{key}({(self.format_other_types(value))})"
                 if key != "python_code" else f"{self.formatar_to_copy(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def is_first_command_set_font(self, code: str) -> bool:
        """
        Verifica entre os comandos set_font, cell e multi_cell, o set_font foi utilizado primeiro.
        :param code: Código do usuário em formato de string
        :return: bool(True) caso não tenha nenhum comando ou o set_font é o primeiro; bool(False) caso tenha comandos e
        o set_font não é o primeiro.
        """
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
        """
        Verifica e executa o código python em formato de string do usuário.
        :param user_code: Código em string
        :return: 'Erro ao executar o código: Adicione um set_font() no começo' caso não tenha um set_font no começo;
        'True' caso o código foi executado com sucesso; 'Erro ao executar o código: (excessão)' caso aconteça algum
        erro ao tentar executar o código.
        """
        if not self.primeira_font:
            if not self.is_first_command_set_font(user_code):
                return "Erro ao executar o código: Adicione um set_font() no começo"

        try:
            exec(user_code, self.allowed_globals)
            return "True"
        except Exception as e:
            return f"Erro ao executar o código: {e}"

    def remover(self) -> None:
        """
        Remove caso tenha a última adição do estilo de PDF sendo gerado.
        """
        if self.contents:
            self.contents.pop()
