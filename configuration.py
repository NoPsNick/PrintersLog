# -*- coding: latin-1 -*-
import datetime
import json
import re


class Config:
    def __init__(self, json_file='./jsons/config.json'):
        self.json_file = json_file
        try:
            with open(self.json_file, 'r') as file:
                config = json.load(file)
                self._traduzir = config.get('_traduzir', {})
                self._default_months = config.get('_default_months', '')
                self._default_months_list = config.get('_default_months_list', [])
                self._default_months_list_to_show = config.get('_default_months_list_to_show', [])
                self._default_year = config.get('_default_year', datetime.date.today().year)
                self._default_years_list = config.get('_default_years_list', [[self._default_year]])
                self._tipo_de_db = config.get('_tipo_de_db', '')
                self._printers_path = config.get('_printers_path', '')
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
            self._default_months = ', '.join(self._traduzir.values())
            self._default_months_list = list(self._traduzir.values())
            self._default_months_list_to_show = list(range(1, 13))
            self._default_year = str(datetime.date.today().year)
            self._default_years_list = [[int(self._default_year)]]
            self._tipo_de_db = "test_db"
            self._printers_path = ".\\printers\\"
            self.save_config()

    def save_config(self):
        config = {
            '_traduzir': self._traduzir,
            '_default_months': self._default_months,
            '_default_months_list': self._default_months_list,
            '_default_months_list_to_show': self._default_months_list_to_show,
            '_default_year': self._default_year,
            '_default_years_list': self._default_years_list,
            '_tipo_de_db': self._tipo_de_db,
            '_printers_path': self._printers_path
        }
        with open(self.json_file, 'w') as file:
            json.dump(config, file, indent=4)

    def translate(self, data):
        """Traduz a data para o formato adequado."""
        return re.sub('|'.join(self._traduzir.keys()),
                      lambda x: self._traduzir[x.group().lower()],
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
            '_printers_path': self._printers_path
        }


if __name__ == '__main__':
    # Config().save_config()
    pass
