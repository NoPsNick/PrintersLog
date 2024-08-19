# -*- coding: latin-1 -*-
import datetime
import math
import re
from typing import Literal, Union

from fpdf import FPDF


class PDFGenerator:
    """
    Gerador de PDFs din�micos.
    """

    def __init__(self, conteudo: dict,
                 orientation: Literal["portrait", "p", "P", "landscape", "l", "L"] = "portrait",
                 unit: str = "pt",
                 format: Union[Literal["a3", "A3", "a4", "A4", "a5", "A5", "letter", "Letter", "legal", "Legal"], tuple[
                     float, float]] = "A4",
                 allowed_globals: dict = None):
        """
        Inicializador da classe.
        :param conteudo: Dicion�rio, onde a chave � o nome que deseja ter e o valor os dados que podem ser acessados.
        :param orientation: Tipo do PDF.
        :param unit: Tamanho das letras.
        :param format: Formato da folha.
        :param allowed_globals: CUIDADO! Dicion�rio contendo fun��es que poder�o ser utilizadas ao tentar executar
        c�digos python do usu�rio. Aviso: utilize com cuidado, pois dar fun��es do python que possam comprometer a
        aplica��o poder� causar danos irrevers�veis. As padr�es ser�o: o conte�do, math para utilizar fun��es de
        matem�tica, datetime para datas, pdf para manipular o PDF, set_font para setar a fonte, cell para adiconar uma
        c�lula e multi_cell para adicionar uma c�lula que pode ter mais de uma linha.
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
        Setar a fonte da escrita dentro do PDF nas linhas seguintes e tamb�m permitir outras fun��es caso seja a
        primeira vez usando.
        :param family: Fam�lia da fonte.
        :param style: Estilo da fonte.
        :param size: Tamanho da fonte.
        """
        self.contents.append({"set_font": {"family": family, "style": style, "size": size}})
        self.primeira_font = True

    def cell(self, w: float = 0, h: float = 20, txt: str = "", border: Union[Literal[0, 1], bool, str, int] = 0,
             ln: Union[int, Literal[0, 1]] = 0, align: str = "C") -> None:
        """
        Adicionar uma c�lula no PDF.
        :param w: Tamanho da largura da c�lula.
        :param h: Tamanho da altura da c�lula.
        :param txt: Texto dentro da c�lula.
        :param border: Se ter� borda ou n�o.
        :param ln: Se ser� a �ltima c�lula da linha.
        :param align: Alinhamento do texto.
        """
        self.contents.append({"cell": {"w": w, "h": h, "txt": txt, "border": border, "ln": ln, "align": align}})

    def multi_cell(self, w: float, h: float = 20, txt: str = "", border: Union[Literal[0, 1], bool, str, int] = 0,
                   align: str = "J") -> None:
        """
        Adicionar uma c�lula m�ltipla no PDF.
        Age igual uma c�lula, por�m ela ir� para a pr�xima linha caso a largura da c�lula exceda o limite da largura do
        PDF e as pr�ximas c�lulas sempre ser�o na pr�xima linha.
        :param w: Tamanho da largura de c�lula.
        :param h: Tamanho da altura da c�lula.
        :param txt: Texto dentro da c�lula.
        :param border: Se ter� borda ou n�o.
        :param align: Alinhamento do texto.
        """
        self.contents.append({"multi_cell": {"w": w, "h": h, "txt": txt, "border": border, "align": align}})

    def python_code(self, code: str = "") -> None:
        """
        Adicionar uma codifica��o em formato PYTHON.
        :param code: C�digo em formato PYTHON.
        """
        self.contents.append({"python_code": {"code": code}})

    def execute_contents(self) -> dict[str, int | str]:
        """
        Criar o PDF atrav�s do conte�do da classe.
        :return: Dicion�rio contendo duas chaves e dois valores, a primeira chave ser� 'codigo' e seu valor um n�mero,
        a segunda chave ser� 'msg' e seu valor a mensagem.
        C�digo: 200 Mensagem: A solicita��o foi bem-sucedida
        C�digo: 400 Mensagem: A solicita��o � inv�lida ou malformada.
        C�digo: 406 Mensagem: Erro ao tentar executar alguma fun��o ou c�digo.
        C�digo: 404 Mensagem: N�o encontrado.
        """
        retorno = {"codigo": 200, "msg": "A solicita��o foi bem-sucedida."}
        for command in self.contents:
            for method, params in command.items():
                if hasattr(self.pdf, method):
                    try:
                        method_func = getattr(self.pdf, method)
                        if callable(method_func):
                            method_func(**params)
                        else:
                            retorno = {"codigo": 400, "msg": "A solicita��o � inv�lida ou malformada."}
                    except Exception as e:
                        retorno = {"codigo": 406, "msg": f"O seguinte erro ocorreu durante a tentativa de usar a"
                                                         f"fun��o {str(method)} com os par�metros {str(params)}:"
                                                         f" {e}"}
                elif method == "python_code":
                    run = self.execute_user_code(params["code"])
                    if run != "True":
                        retorno = {"codigo": 406,
                                   "msg": f"O recurso solicitado ({params['code']}) n�o foi encontrado ou n�o � um "
                                          f"recurso PYTHON."
                                          f" {run}"}
                else:
                    return {"codigo": 404, "msg": f"N�o foi poss�vel executar a fun��o "
                                                  f"{method} com os comandos {params}."}
        return retorno

    def generate_pdf(self, filename: str) -> dict[str, int | str]:
        """
        Ir� gerar o PDF com o nome dado.
        :param filename: Nome que ser� gerado
        :return: Dicion�rio contendo o codigo e a msg ao tentar gerar o pdf.
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
        Formata o texto para visualiza��o.
        :param raw_text: Texto que ser� formatado.
        :return: Texto formatado.
        """
        return "\n>>>".join(line.replace("\t", "    ") for line in raw_text.split('\n'))

    @staticmethod
    def formatar_to_copy(raw_text: str) -> str:
        """
        Formata o texto de c�digo python para que consiga colar e execut�-lo em forma de c�digo.
        :param raw_text: Texto que ser� formatado.
        :return: Texto formatado.
        """
        return "\n".join(line.replace("\t", "    ") for line in raw_text.split('\n'))

    @staticmethod
    def format_other_types(raw_text: dict) -> str:
        """
        Formata o texto que n�o � de c�digo python, por�m para que seja poss�vel colar e execut�-lo como um c�digo
        python.
        :param raw_text: Dicion�rio com a chave sendo o comando e o valor as entradas.
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
        Transforma o conte�do do PDF em uma lista de Strings.
        :return: Lista de strings.
        """
        lista = [f"{key}: {value}" if key != "python_code" else f"{key}:\n>>>{self.formatar(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def contet_to_copy(self) -> list[str]:
        """
        Transforma o conte�do em uma lista de Strings que seja poss�vel colar para ser executado como c�digo python.
        :return: Lista de strings.
        """
        lista = [f"{key}({(self.format_other_types(value))})"
                 if key != "python_code" else f"{self.formatar_to_copy(value['code'])}"
                 for content in self.contents for key, value in content.items()]
        return lista

    def is_first_command_set_font(self, code: str) -> bool:
        """
        Verifica entre os comandos set_font, cell e multi_cell, o set_font foi utilizado primeiro.
        :param code: C�digo do usu�rio em formato de string
        :return: bool(True) caso n�o tenha nenhum comando ou o set_font � o primeiro; bool(False) caso tenha comandos e
        o set_font n�o � o primeiro.
        """
        if not self.primeira_font:
            # Remove poss�veis coment�rios e espa�os em branco extras
            code = re.sub(r'#.*', '', code)
            code = code.strip()

            # Encontra todos os comandos `pdf.` no c�digo
            commands = re.findall(r'\b(set_font|cell|multi_cell)\(', code)

            if not commands:
                return True

            # Verifica se o primeiro comando � pdf.set_font
            self.primeira_font = commands[0].startswith('set_font')
        return self.primeira_font

    def execute_user_code(self, user_code: str) -> str:
        """
        Verifica e executa o c�digo python em formato de string do usu�rio.
        :param user_code: C�digo em string
        :return: 'Erro ao executar o c�digo: Adicione um set_font() no come�o' caso n�o tenha um set_font no come�o;
        'True' caso o c�digo foi executado com sucesso; 'Erro ao executar o c�digo: (excess�o)' caso aconte�a algum
        erro ao tentar executar o c�digo.
        """
        if not self.primeira_font:
            if not self.is_first_command_set_font(user_code):
                return "Erro ao executar o c�digo: Adicione um set_font() no come�o"

        try:
            exec(user_code, self.allowed_globals)
            return "True"
        except Exception as e:
            return f"Erro ao executar o c�digo: {e}"

    def remover(self) -> None:
        """
        Remove caso tenha a �ltima adi��o do estilo de PDF sendo gerado.
        """
        if self.contents:
            self.contents.pop()
