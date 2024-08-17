# -*- coding: latin-1 -*-
import datetime

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from configuration import Config

Builder.load_file("configscreen.kv", encoding='latin-1')

# Constantes
DB_TYPES = {'TestDB': 'test_db', 'Desativado': 'disabled'}


class ConfigScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.configs = self.config.get_configs()
        self.dicionario = {}
        self.ano = datetime.date.today().year

    def on_pre_enter(self, *args):
        self.get_configs()

    def get_configs(self):
        self.config.read_configs()
        self.configs = self.config.get_configs()
        self._update_db_state()
        self._update_inputs()

    def _update_db_state(self):
        db_type = self.configs['_tipo_de_db']
        self.ids.db_testdb.state = 'down' if db_type == DB_TYPES['TestDB'] else 'normal'
        self.ids.db_disabled.state = 'down' if db_type == DB_TYPES['Desativado'] else 'normal'

    def _update_inputs(self):
        self.ids.printer_path_input.text = self.configs['_printers_path']
        self.ids.chave.text = ''
        self.ids.valor.text = ''
        self.dicionario = {}

    def save_db_type(self):
        db_type = self._determine_db_type()
        self.config._tipo_de_db = db_type
        self.config.save_config()
        self.get_configs()

    def _determine_db_type(self):
        if self.ids.db_testdb.state == 'down':
            return DB_TYPES['TestDB']
        return DB_TYPES['Desativado']

    def save_printers_path(self):
        self.config._printers_path = self.ids.printer_path_input.text
        self.config.save_config()
        self.get_configs()

    def save_additions_on_translate(self):
        chave = self.ids.chave.text.strip().lower()
        valor = self.ids.valor.text.strip().title()

        if chave and valor:
            self.dicionario[chave] = valor

        traducoes = self.configs['_traduzir']
        traducoes.update(self.dicionario)
        self.config.alter_translations(traducoes)
        self.config.save_config()
        self.get_configs()
