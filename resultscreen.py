# -*- coding: latin-1 -*-
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from backup import Backup
from configuration import Config
from leitura import Leitura
from storage_manager import StorageManager
from testdb import TestDB

Builder.load_file("resultscreen.kv", encoding='latin-1')


class ResultScreen(Screen):
    """Tela que exibe os resultados processados."""
    recycleView = ObjectProperty(None)
    msg_str = StringProperty("")
    msg_col = ColorProperty((1, 0, 0))
    printers_root = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.configs = self.config.get_configs()
        self.dados = None
        self.clicado = False
        self.default_root = self.configs.get('_printers_path')
        self.printers_root = self.default_root
        self.BL = BoxLayout(size_hint=(1, 0.1))
        self.backup_button_csv = Button(text="Criar CSVs", font_size=dp(12), size_hint=(1, 1))
        self.backup_button_json = Button(text="Salvar em JSON", font_size=dp(12), size_hint=(1, 1))
        self.backup_button_bd = Button(text="Salvar no Banco de Dados", font_size=dp(11), size_hint=(1, 1))
        self.BL.add_widget(self.backup_button_json)
        self.BL.add_widget(self.backup_button_csv)
        self.BL.add_widget(self.backup_button_bd)

    def on_enter(self, *args):
        self.msg_str = ""
        self.msg_col = (1, 0, 0)
        self.config.read_configs()
        self.configs = self.config.get_configs()
        self.default_root = self.configs.get('_printers_path')
        self.printers_root = self.default_root

    def msg_change(self, msg: str = "", col: tuple = (1, 0, 0)):
        """Altera a mensagem e sua cor."""
        self.msg_str = str(msg)
        self.msg_col = col

    def on_printers_root_validate(self, widget):
        """Valida e configura o caminho da raiz das impressoras."""
        self.printers_root = widget.text or self.default_root
        widget.text = self.printers_root

    def result(self):
        """Manipula a exibição dos resultados."""
        self.dados = Leitura(root=self.printers_root).processar_arquivos()
        if self.dados:
            self.msg_change()
            if not self.clicado:
                self.show_data()
                self.backup_button_csv.bind(on_press=self.csv)
                self.backup_button_json.bind(on_press=self.json)
                self.backup_button_bd.bind(on_press=self.bd)
                self.ids.boxlayout_principal.add_widget(self.BL)
                self.clicado = True
            else:
                self.show_data()
        else:
            self.recycleView.data = []

    def show_data(self):
        """Exibe os dados no RecycleView."""
        self.recycleView.data = [dado.get_dictionary() for dado in self.dados]

    def csv(self, widget):
        """Cria backup em CSV."""
        if self.dados:
            Backup(lista=self.dados).gerar_csv()
            Backup(lista=self.dados).gerar_total()
            self.msg_change("Csvs criados com sucesso.", (0, 1, 0, .5))
        else:
            self.msg_change("Não foi possível encontrar dados para salvar.")

    def json(self, widget):
        """Cria backup em JSON."""
        if self.dados:
            dados = [dado.get_dictionary() for dado in self.dados]
            StorageManager().save_data("dados", dados)
            self.msg_change("Backup em JSON criado com sucesso.", (0, 1, 0, .5))
        else:
            self.msg_change("Não foi possível encontrar dados para salvar.")

    def bd(self, widget):
        """Cria backup no Banco de Dados."""
        modo = self.configs["_tipo_de_db"]
        if modo == "test_db" and self.dados:
            bd = TestDB('./dbs/banco_de_dados.db')
            bd.inserir_documentos(dados=self.dados)
            bd.fechar_conexao()
            self.msg_change("Backup salvo no Banco de Dados com sucesso.", (0, 1, 0, .5))
        else:
            self.msg_change(f"Não foi possível salvar os dados no banco de dados, "
                            f"pois ele se encontra no tipo de banco de dados: {modo}.")
