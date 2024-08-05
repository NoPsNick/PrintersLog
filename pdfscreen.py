# -*- coding: latin-1 -*-
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from configuration import Config
from pdf_generator import PDFGenerator

Builder.load_file("pdfscreen.kv", encoding='latin-1')


class PDFScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.lista = []
        self.filtro = []
        self.pdf_generator = PDFGenerator(self.lista, self.filtro)

    def change(self, lista, filtro):
        self.lista = lista
        self.filtro = filtro
        self.pdf_generator = PDFGenerator(self.lista, self.filtro)

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
        family = self.family_input.text or "Times"
        style = self.style_input.text or "B"
        size = int(self.size_input.text) if self.size_input.text else 12

        self.pdf_generator.set_font(family=family, style=style, size=size)
        self.update_preview()
        self.popup.dismiss()

    def show_add_cell_popup(self):
        content = BoxLayout(orientation='vertical')
        self.w_input = TextInput(hint_text='Width', multiline=False)
        self.h_input = TextInput(hint_text='Height', multiline=False)
        self.txt_input = TextInput(hint_text='Text')
        self.border_input = TextInput(hint_text='Border', multiline=False)
        self.ln_input = TextInput(hint_text='Ln', multiline=False)
        self.align_input = TextInput(hint_text='Align', multiline=False)
        add_button = Button(text='Add Cell', on_release=self.add_cell)
        content.add_widget(self.w_input)
        content.add_widget(self.h_input)
        content.add_widget(self.txt_input)
        content.add_widget(self.border_input)
        content.add_widget(self.ln_input)
        content.add_widget(self.align_input)
        content.add_widget(add_button)

        self.popup = Popup(title='Add Cell', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def add_cell(self, instance):
        w = float(self.w_input.text) if self.w_input.text else 0
        h = float(self.h_input.text) if self.h_input.text else 80
        txt = self.txt_input.text or ""
        border = int(self.border_input.text) if self.border_input.text else 1
        ln = int(self.ln_input.text) if self.ln_input.text else 0
        align = self.align_input.text or "C"

        self.pdf_generator.cell(w=w, h=h, txt=txt, border=border, ln=ln, align=align)
        self.update_preview()
        self.popup.dismiss()

    def show_add_multicell_popup(self):
        content = BoxLayout(orientation='vertical')
        self.w_input = TextInput(hint_text='Width', multiline=False)
        self.h_input = TextInput(hint_text='Height', multiline=False)
        self.txt_input = TextInput(hint_text='Text')
        self.border_input = TextInput(hint_text='Border', multiline=False)
        self.align_input = TextInput(hint_text='Align', multiline=False)
        add_button = Button(text='Add MultiCell', on_release=self.add_multicell)
        content.add_widget(self.w_input)
        content.add_widget(self.h_input)
        content.add_widget(self.txt_input)
        content.add_widget(self.border_input)
        content.add_widget(self.align_input)
        content.add_widget(add_button)

        self.popup = Popup(title='Add MultiCell', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def add_multicell(self, instance):
        w = float(self.w_input.text) if self.w_input.text else 0
        h = float(self.h_input.text) if self.h_input.text else 80
        txt = self.txt_input.text or ""
        border = int(self.border_input.text) if self.border_input.text else 1
        align = self.align_input.text or "J"

        self.pdf_generator.multicell(w=w, h=h, txt=txt, border=border, align=align)
        self.update_preview()
        self.popup.dismiss()

    def pegar_pdf_padrao(self):
        for func in self.config.get_default_pdf_style():
            for method, params in func.items():
                if hasattr(self.pdf_generator, method):
                    method_func = getattr(self.pdf_generator, method)
                    if callable(method_func):
                        method_func(**params)
        self.update_preview()

    def pegar_pdf_popup(self):
        content = BoxLayout(orientation='vertical')
        self.nome_do_pdf_salvo = TextInput(hint_text='Nome do estilo de PDF', multiline=False)
        save_button = Button(text='Buscar estilo de PDF', on_release=self.get_pdf)
        content.add_widget(self.nome_do_pdf_salvo)
        content.add_widget(save_button)

        self.popup = Popup(title='Estilos de PDF salvos', content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def get_pdf(self, instance):
        nome = self.nome_do_pdf_salvo.text
        if not self.pdf_generator.get_custom(nome):
            self.popup.dismiss()
            self.show_msg_popup("Error", f"Não foi encontrado o estilo de PDF salvo com o nome: {nome}")
        else:
            self.update_preview()
            self.popup.dismiss()

    def show_save_popup(self):
        content = BoxLayout(orientation='vertical')
        self.filename_input = TextInput(hint_text='Nome do arquivo PDF', multiline=False)
        save_button = Button(text='Criar PDF', on_release=self.save_pdf)
        content.add_widget(self.filename_input)
        content.add_widget(save_button)

        self.popup = Popup(title='Criar PDF', content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def save_pdf(self, instance):
        filename = self.filename_input.text or "output.pdf"
        retorno = self.pdf_generator.save_pdf(filename)
        if retorno["codigo"] == 200:
            self.popup.dismiss()
            self.show_msg_popup("Criado", f"Seu PDF foi criado com sucesso com o nome {filename}")
        else:
            self.popup.dismiss()
            self.show_msg_popup("Error", f"{retorno['codigo']}, mensagem: {retorno['msg']}")

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
        if self.pdf_generator.json_save(nome):
            self.popup.dismiss()
        else:
            self.popup.dismiss()
            self.show_msg_popup("Error", "Já existe um PDF salvo com este nome.")

    def update_preview(self):
        self.preview = self.ids.preview
        self.preview.text = "\n".join(self.pdf_generator.content_to_str())

    def show_config_code_screen(self):
        content = BoxLayout(orientation='vertical')
        self.code_input = TextInput(hint_text='Coloque seu código python aqui', multiline=True, size_hint_y=0.8)
        self.run_button = Button(text='Adicionar código', on_release=self.python_code)
        self.back_button = Button(text='Voltar', on_release=self.go_back)
        content.add_widget(self.code_input)
        content.add_widget(self.run_button)
        content.add_widget(self.back_button)

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

    @staticmethod
    def copy_text(*args):
        """
            Clipboard.copy(label.text): Usa o módulo Clipboard para copiar o texto do Label para a área de transferência.
            on_touch_down: Adiciona um evento de toque ao Label que chama a função copy_text quando o Label é clicado.
            collide_point: Verifica se o ponto de toque está dentro dos limites do Label para garantir que o toque foi feito sobre o texto.
        """
        if args[1].collide_point(*args[2].pos):
            Clipboard.copy(args[1].text)

            if args[1].collide_point(*args[2].pos):
                Clipboard.copy(args[1].text)

    def show_msg_popup(self, type, message):
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
        close_button = Button(text='Fechar', on_release=self.close_msg_popup)
        sv.add_widget(msg_label)
        content.add_widget(sv)
        button_box.add_widget(close_button)
        content.add_widget(button_box)

        self.msg_popup = Popup(title=type, content=content, size_hint=(0.8, 0.6))
        self.msg_popup.open()

    def close_msg_popup(self, instance):
        self.msg_popup.dismiss()

    def go_back(self, instance):
        self.popup.dismiss()
