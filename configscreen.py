# -*- coding: latin-1 -*-
import calendar
import datetime
import re

from dateutil.rrule import rrule, MONTHLY
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
        self.ids.year.text = str(self.configs['_default_year'])
        self.ids.month.text = str(self.configs['_default_months_list_to_show']).replace("[", "").replace("]", "")
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

    def add_translation(self):
        chave = self.ids.chave.text.strip().lower()
        valor = self.ids.valor.text.strip().title()

        if chave and valor:
            self.dicionario[chave] = valor
        self.ids.chave.text = ''
        self.ids.valor.text = ''
        self.get_configs()

    def save_additions_on_translate(self):
        traducoes = self.configs['_traduzir']
        traducoes.update(self.dicionario)
        self.config.alter_translations(traducoes)
        self.config.save_config()
        self.get_configs()

    def save_month_year(self):
        self._save_months()
        self._save_years()
        self.config.save_config()
        self.get_configs()

    def _save_months(self):
        month_text = self.ids.month.text.strip().replace(" ", "")
        months_list_to_show = self._parse_months(month_text)
        months = ", ".join(self.config.translate_back(calendar.month_name[num]) for num in months_list_to_show)
        self.config._default_months = months
        self.config._default_months_list = months_list_to_show
        self.config._default_months_list_to_show = ", ".join(map(str, months_list_to_show))

    def _parse_months(self, month_text):
        month_text = month_text if month_text != "0" else "1-12"
        month_ranges = re.split(r',', month_text)
        months_set = set()
        for range_text in month_ranges:
            month_range = re.findall(r'\b\d+\b', range_text)
            if len(month_range) == 2:
                try:
                    str_dt = datetime.date(int(self.ano), int(month_range[0]), 1)
                    end_dt = datetime.date(int(self.ano), int(month_range[1]), 1)
                except ValueError:
                    str_dt = datetime.date(int(self.ano), int(month_range[0]), 1)
                    end_dt = datetime.date(int(self.ano), int(12), 1)
                lista = [dt.month for dt in rrule(MONTHLY, dtstart=str_dt, until=end_dt)]
                months_set.update(lista)
            elif len(month_range) == 1:
                months_set.add(int(month_range[0]))
        return sorted(months_set)

    def _save_years(self):
        years_list = self._parse_years()
        self.config._default_year = ", ".join(map(str, years_list))
        self.config._default_years_list = [[year] for year in years_list]

    def _parse_years(self):
        year_text = self.ids.year.text.strip().replace(" ", "")
        year_ranges = re.split(",", year_text)
        years_set = set()
        for range_text in year_ranges:
            year_range = re.findall(r'\b\d+\b', range_text)
            if len(year_range) == 2:
                start_year, end_year = map(int, year_range)
                years_set.update(range(start_year, end_year + 1))
            elif len(year_range) == 1:
                years_set.add(int(year_range[0]))
        return sorted(years_set)
