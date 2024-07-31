# -*- coding: latin-1 -*-
import calendar
import datetime
import re

from dateutil.rrule import rrule, MONTHLY
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from configuration import Config

Builder.load_file("configscreen.kv", encoding='latin-1')


class ConfigScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.configs = self.config.get_configs()
        self.dicionario = {}
        self.db_types = {'TestDB': 'test_db',
                         'Desativado': 'disabled'}

    def on_pre_enter(self, *args):
        self.get_configs()
        self.dicionario = {}

    def get_configs(self):
        self.config.read_configs()
        self.configs = self.config.get_configs()
        if self.configs['_tipo_de_db'] == 'test_db':
            self.ids.db_testdb.state = 'down'
            self.ids.db_disabled.state = 'normal'
        else:
            self.ids.db_testdb.state = 'normal'
            self.ids.db_disabled.state = 'down'
        self.ids.printer_path_input.text = self.configs['_printers_path']
        self.ids.year.text = str(self.configs['_default_year'])
        self.ids.month.text = str(self.configs['_default_months_list_to_show']).replace("[", "").replace("]", "")
        self.ids.chave.text, self.ids.valor.text = '', ''
        self.dicionario = {}

    def save_db_type(self):
        if self.ids.db_testdb.state == 'down':
            db_type = self.db_types['TestDB']
        elif self.ids.db_disabled.state == 'down':
            db_type = self.db_types['Desativado']
        else:
            db_type = self.db_types['Desativado']
        self.config._tipo_de_db = db_type
        self.config.save_config()
        self.get_configs()

    def save_printers_path(self):
        printer_path = self.ids.printer_path_input.text
        self.config._printers_path = printer_path
        self.config.save_config()
        self.get_configs()

    def add_translation(self):
        chave = self.ids.chave.text.strip()
        valor = self.ids.valor.text.strip()

        # Verifica se ambos chave e valor são não vazios
        if chave and valor:
            # Atualiza o dicionário, garantindo que a chave esteja em minúsculas e o valor em título
            self.dicionario[chave.lower()] = valor.title()
        self.ids.chave.text, self.ids.valor.text = '', ''
        self.get_configs()

    def save_additions_on_translate(self):
        dicionario = self.configs['_traduzir']
        for key, value in self.dicionario.items():
            dicionario[key] = value
        self.config._traduzir = dicionario
        self.config.save_config()
        self.get_configs()

    def save_month_year(self):
        # Meses
        month = self.ids.month.text.strip().replace(" ", "")
        month = self.ids.month.text.replace(" ", "") if month != "0" else "1-12"
        todos = re.split(r',', month)

        pegar_meses = [re.findall(r'\b\d+\b', cada) for cada in todos]
        meses_set, to_show = set(), []
        ano = datetime.date.today().year
        for lis in pegar_meses:
            if len(lis) == 2:
                str_dt = datetime.date(int(ano), int(lis[0]), 1)
                end_dt = datetime.date(int(ano), int(lis[1]), 1)
                lista = [dt.month for dt in rrule(MONTHLY, dtstart=str_dt, until=end_dt)]
                meses_set.update(lista)
                to_show.extend(lista)
            elif len(lis) == 1:
                meses_set.add(int(lis[0]))
                to_show.append(int(lis[0]))

        meses_ordenados = sorted(meses_set)
        meses = [self.config.translate_back(calendar.month_name[numero]) for numero in meses_ordenados]
        months_list = [numero for numero in meses_ordenados]
        months_list_to_show = ", ".join(map(str, months_list))
        months = ", ".join(meses)

        self.config._default_months = months
        self.config._default_months_list = months_list
        self.config._default_months_list_to_show = months_list_to_show

        # Anos
        texto = self.ids.year.text.strip().replace(" ", "")
        anos = re.split(",", texto)
        pegar_anos = [re.findall(r'\b\d+\b', cada) for cada in anos]

        anos_set, novo = set(), []

        for lis in pegar_anos:
            if len(lis) == 2:
                intervalo_anos = range(int(lis[0]), int(lis[1]) + 1)
                anos_set.update(intervalo_anos)
                novo.extend(intervalo_anos)
            elif len(lis) == 1:
                ano = int(lis[0])
                anos_set.add(ano)
                novo.append(ano)

        anos_ordenados = sorted(anos_set)
        years_to_show = ", ".join(map(str, anos_ordenados))
        years_list = [[ano] for ano in anos_ordenados]
        self.config._default_year = years_to_show
        self.config._default_years_list = years_list
        self.config.save_config()
        self.get_configs()
