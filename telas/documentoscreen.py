# -*- coding: latin-1 -*-
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from bordered_boxlayout import BorderedBoxLayout
from configuration import Config
from visualdados import VisualDocumentos

Builder.load_file("./telas/documentoscreen.kv", encoding='latin-1')


class DocWidget(RecycleDataViewBehavior, BorderedBoxLayout):
    text = StringProperty()
    documento = StringProperty()


class DocumentoScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.docview = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.update_list()

    def del_documento(self, key):
        self.popup.dismiss()
        visu = VisualDocumentos()
        visu.del_documento(principal=key)
        self.update_list()

    def on_button_delete(self, principal):
        visu = VisualDocumentos()
        banco = visu.pegar_documentos_por_nome(principal=principal)
        conteudo = [str(dado.get_dictionary_to_show()).replace("{", "").replace("}", "") for dado in banco]
        if conteudo:
            self.open_popup_delete(conteudo=conteudo, principal=principal)

    def open_popup_delete(self, conteudo, principal):
        content = BoxLayout(padding=10, orientation='vertical')
        sv = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True, pos_hint={"center_y": 0.5})

        message = "\n".join(conteudo)
        msg_label = Label(
            text=f"(NÃO É POSSÍVEL REVERTER ESTA AÇÃO)\nVocê realmente deseja deletar os dados do documento:"
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
        delete_button.bind(on_release=lambda instance, name=principal: self.del_documento(principal))
        close_button = Button(text='Fechar', on_release=self.go_back)
        sv.add_widget(msg_label)
        content.add_widget(sv)
        button_box.add_widget(delete_button)
        button_box.add_widget(close_button)
        content.add_widget(button_box)

        self.popup = Popup(title=f"Deletar Dados do Documento: {principal}", content=content, size_hint=(0.8, 0.6))
        self.popup.open()

    def update_list(self):
        visu = VisualDocumentos()
        lista = visu.pegar_documentos()
        documento = set([doc.principal for doc in lista])

        documentos = [{'text': documento} for documento in documento]

        self.docview.data = documentos

    def go_back(self, instance):
        if self.popup:
            self.popup.dismiss()
