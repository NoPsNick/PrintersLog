# -*- coding: latin-1 -*-
import datetime
import json


class Config:
    def __init__(self, json_file='config.json'):
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

    def _translate(self, months) -> list:
        meses_lista = [mes.strip().lower() for mes in months.split(",")]
        return [self._traduzir.get(mes, 'Mês desconhecido') for mes in meses_lista]

    def _get_show_list(self) -> list:
        return [datetime.datetime.strptime(month, '%B').month for month in self._default_months_list]

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
