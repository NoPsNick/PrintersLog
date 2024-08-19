# -*- coding: latin-1 -*-
import datetime
import math

from fpdf import FPDF
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from configuration import Config
from models import PDFs
from pdf_generator import PDFGenerator
from storage_manager import StorageManager
from visualdados import VisualPDFs

Builder.load_file("./telas/pdfscreen.kv", encoding='latin-1')


class PDFScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.botoes_to_enable_disable = []
        self.storage_manager = StorageManager()
        self.config = Config()
        self.formato_da_data = self.config.get_data_format()
        self.conteudo = {}
        self.pdf_generator = None

    def alterar_pdf_generator(self, conteudo, contents=None):
        self.config = Config()
        self.conteudo = conteudo
        allowed_globals = {
            "formatar_datas": self._formatar_datas,
            "truncate_text": self._truncate_text,
            "calcular_periodo": self._calcular_periodo,
            "pegar_totais": self.get_totals,
            "formato_da_data": self.formato_da_data,
        }
        self.pdf_generator = PDFGenerator(conteudo=self.conteudo, allowed_globals=allowed_globals)
        self.pdf_generator.contents = contents or []
        self.botoes_to_enable_disable = [self.ids.add_cell, self.ids.multicell, self.ids.salvar,
                                         self.ids.gerar]
        self.update_preview()

    def show_set_font_popup(self):
        content = BoxLayout(orientation='vertical')
        self.family_input = TextInput(hint_text='Family', multiline=False)
        self.style_input = TextInput(hint_text='Style', multiline=False)
        self.size_input = TextInput(hint_text='Size', multiline=False)
        add_button = Button(text='Add Font', on_release=self.add_font)
        content.add_widget(self.family_input)
        content.add_widget(self.style_input)
        content.add_widget(self.size_input)
        content.add_widget(add_button)

        self.popup = Popup(title='Set Font', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def add_font(self, instance):
        family = self.family_input.text or "Arial"
        style = self.style_input.text or "B"
        size = int(self.size_input.text) if self.size_input.text else 12

        self.pdf_generator.set_font(family=family, style=style, size=size)
        self.update_preview()
        self.popup.dismiss()

    def show_add_cell_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        self.w_input = TextInput(hint_text='Width', multiline=False)
        self.h_input = TextInput(hint_text='Height', multiline=False)
        self.txt_input = TextInput(hint_text='Text')
        self.border_input = TextInput(hint_text='Border', multiline=False)
        self.ln_input = TextInput(hint_text='Quebra de Linha(0 = não, 1 = sim):', multiline=False)
        self.align_input = TextInput(hint_text='Align', multiline=False)

        boxl = BoxLayout(orientation="horizontal", padding=[0, dp(5), 0, 0])
        add_button = Button(text='Add Cell', on_release=self.add_cell)
        back_button = Button(text='Voltar', on_release=self.go_back)
        boxl.add_widget(add_button)
        boxl.add_widget(back_button)

        content.add_widget(self.w_input)
        content.add_widget(self.h_input)
        content.add_widget(self.txt_input)
        content.add_widget(self.border_input)
        content.add_widget(self.ln_input)
        content.add_widget(self.align_input)

        content.add_widget(boxl)

        self.popup = Popup(title='Add Cell', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def add_cell(self, instance):
        w = float(self.w_input.text) if self.w_input.text else 0
        h = float(self.h_input.text) if self.h_input.text else 20
        txt = self.txt_input.text or ""
        border = int(self.border_input.text) if self.border_input.text else 1
        ln = int(self.ln_input.text) if self.ln_input.text else 0
        align = self.align_input.text or "C"

        self.pdf_generator.cell(w=w, h=h, txt=txt, border=border, ln=ln, align=align)
        self.update_preview()

    def show_add_multicell_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        self.w_input = TextInput(hint_text='Width', multiline=False)
        self.h_input = TextInput(hint_text='Height', multiline=False)
        self.txt_input = TextInput(hint_text='Text', multiline=True)
        self.border_input = TextInput(hint_text='Border', multiline=False)
        self.align_input = TextInput(hint_text='Align', multiline=False)

        boxl = BoxLayout(orientation="horizontal", padding=[0, dp(5), 0, 0])
        add_button = Button(text='Add MultiCell', on_release=self.add_multicell)
        back_button = Button(text='Voltar', on_release=self.go_back)
        boxl.add_widget(add_button)
        boxl.add_widget(back_button)

        content.add_widget(self.w_input)
        content.add_widget(self.h_input)
        content.add_widget(self.txt_input)
        content.add_widget(self.border_input)
        content.add_widget(self.align_input)
        content.add_widget(boxl)

        self.popup = Popup(title='Add MultiCell', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def add_multicell(self, instance):
        w = float(self.w_input.text) if self.w_input.text else 0
        h = float(self.h_input.text) if self.h_input.text else 20
        txt = self.txt_input.text or ""
        border = int(self.border_input.text) if self.border_input.text else 1
        align = self.align_input.text or "J"

        self.pdf_generator.multi_cell(w=w, h=h, txt=txt, border=border, align=align)
        self.update_preview()

    def pegar_pdf_padrao(self):
        for func in self.config.get_default_pdf_style():
            for method, params in func.items():
                if hasattr(self.pdf_generator, method):
                    method_func = getattr(self.pdf_generator, method)
                    if callable(method_func):
                        method_func(**params)
        self.update_preview()

    def pegar_pdf_popup(self):
        content = BoxLayout(padding=dp(5), orientation='vertical')

        sv = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True, pos_hint={"center_y": 0.5})

        custom_pdfs = self.get_customs()

        box = BoxLayout(orientation='vertical', size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        for custom_pdf in custom_pdfs:
            for nome in custom_pdf:
                button_del = Button(text='Remover PDF', size_hint_x=0.2)
                button_del.bind(on_release=lambda instance, name=nome: self.deletar_pdf_popup(name))
                line_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                label = Label(text=f"Nome: {nome}", size_hint_x=0.2)
                button = Button(text='Pegar PDF', size_hint_x=0.2)
                button.bind(on_release=lambda instance, name=nome: self.close_pegar_pdf_popup(name))
                line_box.add_widget(button_del)
                line_box.add_widget(label)
                line_box.add_widget(button)
                box.add_widget(line_box)

        sv.add_widget(box)
        content.add_widget(sv)

        self.nome_do_pdf_salvo = TextInput(hint_text='Nome do estilo de PDF', multiline=False, size_hint_y=0.2)
        save_button = Button(text='Buscar estilo de PDF', size_hint_y=0.2, on_release=self.get_pdf)
        content.add_widget(self.nome_do_pdf_salvo)
        content.add_widget(save_button)

        self.popup = Popup(title='Estilos de PDF salvos', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def close_pegar_pdf_popup(self, nome):
        self.popup.dismiss()
        self.get_custom(nome)
        self.update_preview()

    def deletar_pdf_popup(self, nome):
        self.popup.dismiss()
        content = BoxLayout(padding=10, orientation='vertical')
        sv = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True, pos_hint={"center_y": 0.5})
        if self.config.get_configs().get(
                "_tipo_de_db") == "test_db":
            visu = VisualPDFs()
            banco = visu.pegar_pdf_por_nome(nome)
            conteudo = [dado.get_dict_no_name_id() for dado in banco]
        else:
            all_pdfs = {key: value for dicionario in self.json_get() for key, value in dicionario.items()}
            conteudo = all_pdfs[nome]

        lista = [
            f"{key}: {value}" if key != "python_code" else f"{key}:\n>>>{self.pdf_generator.formatar(value['code'])}"
            for content in conteudo for key, value in content.items()]
        message = "\n".join(lista)
        msg_label = Label(
            text=f"(NÃO É POSSÍVEL REVERTER ESTA AÇÃO)Você realmente deseja deletar o seguinte estilo de PDF ({nome}):"
                 f"\n{message}",
            text_size=(self.width * 0.8, None),  # Define a largura do texto para que ele quebre automaticamente
            size_hint_y=None,  # Para permitir ajuste dinâmico da altura
            halign='left',
            valign='top'
        )
        msg_label.bind(
            width=lambda *x: msg_label.setter('text_size')(msg_label, (msg_label.width, None)),
            texture_size=lambda *x: msg_label.setter('height')(msg_label, msg_label.texture_size[1])
        )

        button_box = BoxLayout(size_hint_y=None, height=40)
        delete_button = Button(text='Deletar')
        delete_button.bind(on_release=lambda instance, name=nome: self.del_pdf(nome))
        close_button = Button(text='Fechar', on_release=self.go_back)
        sv.add_widget(msg_label)
        content.add_widget(sv)
        button_box.add_widget(delete_button)
        button_box.add_widget(close_button)
        content.add_widget(button_box)

        self.popup = Popup(title=f"Deletar estilo de PDF: {nome}", content=content, size_hint=(0.8, 0.6))
        self.popup.open()

    def get_pdf(self, instance):
        nome = self.nome_do_pdf_salvo.text
        if nome:
            pdf = self.get_custom(nome)
            self.popup.dismiss()
            if not pdf:
                self.show_msg_popup("Error", f"Não foi encontrado o estilo de PDF salvo com o nome: {nome}")
            self.update_preview()
        else:
            self.show_msg_popup("Error", f"Por favor, insira um nome.")

    def show_generate_popup(self):
        content = BoxLayout(orientation='vertical')
        self.filename_input = TextInput(hint_text='Nome do arquivo PDF', multiline=False)
        save_button = Button(text='Criar PDF', on_release=self.generate_pdf)
        content.add_widget(self.filename_input)
        content.add_widget(save_button)

        self.popup = Popup(title='Criar PDF', content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def generate_pdf(self, instance):
        filename = self.filename_input.text or "output.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        retorno = self.pdf_generator.generate_pdf(filename)
        self.popup.dismiss()
        if retorno["codigo"] == 200:
            self.show_msg_popup("Criado", f"Seu PDF foi criado com sucesso com o nome {filename}")
        else:
            self.show_msg_popup("Error", f"{retorno['codigo']}, mensagem: {retorno['msg']}")

        # Reiniciar classe do PDF, para que possa gerar novos PDFs.
        conteudo = self.pdf_generator.conteudo
        contents = self.pdf_generator.contents
        self.alterar_pdf_generator(conteudo=conteudo, contents=contents)

        self.update_preview()

    def show_style_save_popup(self):
        content = BoxLayout(orientation='vertical')
        self.nome = TextInput(hint_text='Nome do estilo do PDF', multiline=False)
        save_button = Button(text='Salvar estilo do PDF', on_release=self.style_save)
        content.add_widget(self.nome)
        content.add_widget(save_button)

        self.popup = Popup(title='Salvar estilo de PDF', content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def style_save(self, instance):
        nome = self.nome.text
        if nome:
            save = self.save(nome)
            self.popup.dismiss()
            if not save:
                self.show_msg_popup("Error", "Já existe um PDF salvo com este nome.")
        else:
            self.popup.dismiss()
            self.show_msg_popup("Error", "Escreva um nome para salvar o estilo de PDF.")

    def update_preview(self):
        preview = self.ids.preview
        lista = self.pdf_generator.content_to_str()
        preview.text = "\n".join(lista)
        if not lista:
            for botao in self.botoes_to_enable_disable:
                botao.disabled = True
            self.pdf_generator.primeira_font = False
        else:
            for botao in self.botoes_to_enable_disable:
                botao.disabled = False

    def show_code_screen(self):
        content = BoxLayout(orientation='vertical')

        self.code_input = TextInput(hint_text='Coloque seu código python aqui', multiline=True, size_hint_y=0.8)

        boxl = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        self.run_button = Button(text='Adicionar código', on_release=self.python_code)
        self.back_button = Button(text='Fechar', on_release=self.go_back)

        boxl.add_widget(self.run_button)
        boxl.add_widget(self.back_button)

        content.add_widget(self.code_input)
        content.add_widget(boxl)

        self.popup = Popup(title='Configure Code', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def python_code(self, instance):
        additions = self.code_input.text
        if additions:
            self.pdf_generator.python_code(code=additions)
            self.update_preview()

    def remover(self):
        self.pdf_generator.remover()
        self.update_preview()

    def copy_text(self, *args):
        """
        Clipboard.copy(label.text): Usa o módulo Clipboard para copiar o texto do Label para a área de transferência.
        on_touch_down: Adiciona um evento de toque ao Label que chama a função copy_text quando o Label é clicado.
        collide_point: Verifica se o ponto de toque está dentro dos limites do Label para garantir que o toque foi
        feito sobre o texto.
        """
        if args[1].collide_point(*args[2].pos):
            Clipboard.copy("\n".join(self.pdf_generator.contet_to_copy()))

    def show_msg_popup(self, tipo, message):
        content = BoxLayout(padding=10, orientation='vertical')
        sv = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True, pos_hint={"center_y": 0.5})

        msg_label = Label(
            text=message,
            text_size=(self.width * 0.8, None),  # Define a largura do texto para que ele quebre automaticamente
            size_hint_y=None,  # Para permitir ajuste dinâmico da altura
            halign='left',
            valign='top'
        )
        msg_label.bind(
            width=lambda *x: msg_label.setter('text_size')(msg_label, (msg_label.width, None)),
            texture_size=lambda *x: msg_label.setter('height')(msg_label, msg_label.texture_size[1])
        )

        button_box = BoxLayout(size_hint_y=None, height=40)
        close_button = Button(text='Fechar', on_release=self.go_back)
        sv.add_widget(msg_label)
        content.add_widget(sv)
        button_box.add_widget(close_button)
        content.add_widget(button_box)

        self.popup = Popup(title=tipo, content=content, size_hint=(0.8, 0.6))
        self.popup.open()

    def go_back(self, instance):
        if self.popup:
            self.popup.dismiss()

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

    def save(self, nome: str) -> bool:
        """
        Salva ou em formato json ou no banco de dados o estilo de PDF.
        :param nome: Nome em formato de string para o salvamento do estilo de PDF.
        :return: Função de salvamento.
        """
        return self.json_save(nome) if self.config.get_configs().get(
            "_tipo_de_db") != "test_db" else self.db_save(nome)

    def json_save(self, nome: str) -> bool:
        """
        Salva o estilo de PDF caso não tenha algum com o nome recebido em formato JSON.
        :param nome: Nome em formato de string para o salvamento do estilo de PDF.
        :return: bool(True) caso salve em formato JSON; bool(False) caso exista algum com o nome.
        """
        if not self.check_if_name(nome):
            custom_pdfs = self.json_get()
            custom_pdfs.append({nome: self.pdf_generator.contents})
            self.storage_manager.save_data("custom_pdfs", custom_pdfs)
            return True
        return False

    def db_save(self, nome: str) -> bool:
        """
        Salva o estilo de PDF caso não tenha algum com o nome recebido no Banco de Dados.
        :param nome: Nome em formato de string para o salvamento do estilo de PDF.
        :return: bool(True) caso efetue o salvamento no Banco de Dados; bool(False) caso exista algum com o nome.
        """
        pdfs = [PDFs(nome=str(nome), tipo=str(chave), valor=str(valor)) for pdfs in self.pdf_generator.contents
                for chave, valor in pdfs.items()]
        visu = VisualPDFs(dados=pdfs)
        retorno = visu.custom_pdf_to_db()
        return retorno

    def get_customs(self) -> list[dict[str, list[dict]]]:
        """
        Faz a busca de todos os estilos de PDF ou em JSON ou no Banco de Dados.
        :return: Lista dos estilos de PDF.
        """
        return self.json_get() if self.config.get_configs().get(
            "_tipo_de_db") != "test_db" else self.db_get()

    def json_get(self) -> list:
        """
        Pegar todos os estilos de PDF salvos em JSON.
        :return: Lista de estilos de PDF salvos em JSON.
        """
        lista = [pdf for pdf in self.storage_manager.load_data("custom_pdfs")] or []
        all_pdfs = [{key.lower(): value} for dicionario in lista for key, value in dicionario.items()]
        return all_pdfs

    @staticmethod
    def db_get() -> list:
        """
        Pegar todos os estilos de PDF salvos no Banco de Dados.
        :return: Lista de estilso de PDF salvos no banco de Dados.
        """
        visu = VisualPDFs()
        custom_pdfs = visu.pegar_todos_os_nomes() or []
        return custom_pdfs

    def get_custom(self, nome: str) -> bool:
        """
        Retorna se foi possível pegar o estilo de PDF salvo pelo nome ou em JSON ou no Banco de Dados.
        :param nome: Nome em formato de string do estilo de PDF salvo.
        :return: bool(True) caso foi possível obter o estilo de PDF; bool(False) caso não tenha sido possível obter o
        estilo de PDF.
        """
        return self.get_custom_json(nome) if self.config.get_configs().get("_tipo_de_db"
                                                                           ) != "test_db" else self.get_custom_db(nome)

    def get_custom_json(self, nome: str) -> bool:
        """
        Pega o estilo de PDF salvo pelo nome no formato JSON e o adiciona no conteúdo de criação de PDF do gerador de
        PDF.
        :param nome: Nome em formato de string do estilo de PDF salvo.
        :return: bool(True) caso foi possível obter o estilo de PDF; bool(False) caso não tenha sido possível obter o
        estilo de PDF.
        """
        custom_pdfs = self.json_get()
        nome = nome.lower()
        if custom_pdfs and self.check_if_name(nome):
            all_pdfs = {key.lower(): value for dicionario in custom_pdfs for key, value in dicionario.items()}
            self.pdf_generator.contents.extend(all_pdfs[nome])
            return True
        else:
            return False

    def get_custom_db(self, nome: str) -> bool:
        """
        Pega o estilo de PDF salvo pelo nome no Banco de Dados e o adiciona no conteúdo de criação de PDF do gerador de
        PDF.
        :param nome: Nome em formato de string do estilo de PDF salvo.
        :return: bool(True) caso foi possível obter o estilo de PDF; bool(False) caso não tenha sido possível obter o
        estilo de PDF.
        """
        visu = VisualPDFs()
        custom_db = visu.pegar_pdf_por_nome(nome=nome)
        conteudo = [pdf.get_dict_no_name_id() for pdf in custom_db]
        if conteudo:
            self.pdf_generator.contents.extend(conteudo)
            return True
        return False

    def check_if_name(self, nome: str) -> bool:
        """
        Verifica se já existe um PDF salvo em formato JSON.
        :param nome: Nome em formato de string do estilo de PDF salvo.
        :return: bool(True) caso exista este nome salvo; bool(False) caso não exista este nome salvo.
        """
        custom_pdfs = self.json_get()
        existing_names = {key.lower() for dicionario in custom_pdfs for key in dicionario}
        return nome.lower() in existing_names

    def del_pdf(self, nome):
        self.popup.dismiss()
        self.del_pdf_json(nome) if self.config.get_configs().get(
            "_tipo_de_db") != "test_db" else self.del_pdf_db(nome)
        self.update_preview()

    @staticmethod
    def del_pdf_db(nome):
        visu = VisualPDFs()
        visu.del_pdf(nome)

    def del_pdf_json(self, nome):
        custom_pdfs = self.json_get()
        nome = nome.lower()
        all_pdfs = [dicionario for dicionario in custom_pdfs for key in dicionario.keys() if key != nome]
        self.storage_manager.save_data("custom_pdfs", all_pdfs)
