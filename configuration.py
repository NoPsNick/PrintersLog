# -*- coding: latin-1 -*-
import datetime
import json
import re


class Config:
    field_names = ["data", "user", "impressora", "est", "duplex", "escala_de_cinza"]

    def __init__(self, json_file='./jsons/config.json'):
        self.json_file = json_file
        self.read_configs()

    def read_configs(self):
        try:
            with open(self.json_file, 'r') as file:
                config = json.load(file)
                self._traduzir = config.get('_traduzir', {
                    "janeiro": "January",
                    "fevereiro": "February",
                    "março": "March",
                    "abril": "April",
                    "maio": "May",
                    "junho": "June",
                    "julho": "July",
                    "agosto": "August",
                    "setembro": "September",
                    "outubro": "October",
                    "novembro": "November",
                    "dezembro": "December"
                })
                self._traduzir_inverso = config.get('_traduzir_inverso', {v: k for k, v in self._traduzir.items()})
                self._default_months = config.get('_default_months', '')
                self._default_months_list = config.get('_default_months_list', [])
                self._default_months_list_to_show = config.get('_default_months_list_to_show', [])
                self._default_year = config.get('_default_year', datetime.date.today().year)
                self._default_years_list = config.get('_default_years_list', [[self._default_year]])
                self._tipo_de_db = config.get('_tipo_de_db', '')
                self._printers_path = config.get('_printers_path', '')
                self._filters = config.get('_filters', {})
                self._data_format = config.get('_data_format', '%d/%m/%Y')
        except FileNotFoundError:
            # Default values if config file does not exist
            self._traduzir = {
                "janeiro": "January",
                "fevereiro": "February",
                "março": "March",
                "abril": "April",
                "maio": "May",
                "junho": "June",
                "julho": "July",
                "agosto": "August",
                "setembro": "September",
                "outubro": "October",
                "novembro": "November",
                "dezembro": "December"
            }
            self._traduzir_inverso = {v.lower(): k.title() for k, v in self._traduzir.items()}
            self._default_months = ', '.join(self._traduzir_inverso.values())
            self._default_months_list = list(range(1, 13))
            self._default_months_list_to_show = list(range(1, 13))
            self._default_year = str(datetime.date.today().year)
            self._default_years_list = [[int(self._default_year)]]
            self._tipo_de_db = "test_db"
            self._printers_path = ".\\printers\\"
            self._filters = {field: {"include": [], "exclude": []} for field in self.field_names}
            self._filters["duplex"]["include"] = ["True", "False"]
            self._filters["escala_de_cinza"]["include"] = ["True", "False"]
            self._data_format = '%d/%m/%Y'
            self.save_config()

    def save_config(self):
        config = {
            '_traduzir': self._traduzir,
            '_traduzir_inverso': self._traduzir_inverso,
            '_default_months': self._default_months,
            '_default_months_list': self._default_months_list,
            '_default_months_list_to_show': self._default_months_list_to_show,
            '_default_year': self._default_year,
            '_default_years_list': self._default_years_list,
            '_tipo_de_db': self._tipo_de_db,
            '_printers_path': self._printers_path,
            '_filters': self._filters,
            '_data_format': self._data_format
        }
        with open(self.json_file, 'w') as file:
            json.dump(config, file, indent=4)

    def alter_filter(self, new_filter: dict[str, dict[str, set | list]]):
        self._filters = new_filter

    def translate(self, data):
        """Traduz a data para o formato adequado."""
        return re.sub('|'.join(self._traduzir.keys()),
                      lambda x: self._traduzir[x.group().lower()],
                      data,
                      flags=re.IGNORECASE)

    def translate_back(self, data):
        """Traduz a data de volta para o formato original."""
        return re.sub('|'.join(self._traduzir_inverso.keys()),
                      lambda x: self._traduzir_inverso[x.group().lower()],
                      data,
                      flags=re.IGNORECASE)

    def get_configs(self) -> dict:
        return {
            "_traduzir": self._traduzir,
            "_default_months": self._default_months,
            "_default_months_list": self._default_months_list,
            "_default_months_list_to_show": self._default_months_list_to_show,
            "_default_year": self._default_year,
            "_default_years_list": self._default_years_list,
            "_tipo_de_db": self._tipo_de_db,
            '_printers_path': self._printers_path,
            '_filters': self._filters,
            '_data_format': self._data_format
        }

    def get_filter(self) -> dict[str, dict[str, set | list]]:
        return self._filters

    def get_data_format(self):
        return str(self._data_format)


if __name__ == '__main__':
    # Config().save_config()
    pass
