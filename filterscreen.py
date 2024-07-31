# -*- coding: latin-1 -*-
from datetime import datetime, timedelta

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from configuration import Config

Builder.load_file("filterscreen.kv", encoding='latin-1')


class FilterScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.filtro = self.config.get_filter()
        self.booleanos = {True: ["Sim", "Yes", "S", "Y"],
                          False: ["Nao", "Não", "No", "N"]}

    def on_pre_enter(self, *args):
        self.change_texts()

    def change_texts(self):
        self.config.read_configs()
        self.filtro = self.config.get_filter()
        self.ids.data_input.text = self.formatar_filtro('data')
        self.ids.usuario_input.text = self.formatar_filtro('user')
        self.ids.impressora_input.text = self.formatar_filtro('impressora')
        self.ids.estacao_input.text = self.formatar_filtro('est')
        self.ids.duplex_true.active = True if str(True) in self.filtro.get('duplex')["include"] else False
        self.ids.duplex_false.active = True if str(False) in self.filtro.get('duplex')["include"] else False
        self.ids.escala_true.active = True if str(True) in self.filtro.get('escala_de_cinza')["include"] else False
        self.ids.escala_false.active = True if str(False) in self.filtro.get('escala_de_cinza')["include"] else False

    def filter_results(self, *inputs):
        field_names = ["data", "user", "impressora", "est", "duplex", "escala_de_cinza"]
        filters: dict[str, dict[str, set | list]] = {field: {"include": set(), "exclude": set()} for field
                                                     in
                                                     field_names}

        for field, input_text in zip(field_names, inputs):
            if field in ["duplex", "escala_de_cinza"]:
                # For boolean fields, handle True, False, or both
                include_true = input_text.get('True', False)
                include_false = input_text.get('False', False)
                if include_true:
                    filters[field]["include"].add("True")
                else:
                    filters[field]["exclude"].add("True")
                if include_false:
                    filters[field]["include"].add("False")
                else:
                    filters[field]["exclude"].add("False")
            elif field in ["data"]:
                if input_text.split():
                    include, exclude = self.gerar_datas_multiplos_intervalos(input_text)
                    filters[field]["include"] = include
                    filters[field]["exclude"] = exclude
            else:
                words = [word.strip() for word in input_text.split(',')]
                for word in words:
                    if word:
                        if word.startswith('-'):
                            filters[field]["exclude"].add(word.lstrip('-'))
                        else:
                            filters[field]["include"].add(word)

        for field in field_names:
            # Remove duplicates, giving preference to exclude list
            filters[field]["include"] -= filters[field]["exclude"]
            # Convert sets to None if empty
            filters[field]["include"] = list(filters[field]["include"]) if filters[field]["include"] else []
            filters[field]["exclude"] = list(filters[field]["exclude"]) if filters[field]["exclude"] else []

        self.config.alter_filter(filters)
        self.config.save_config()
        self.change_texts()

    def gerar_datas_multiplos_intervalos(self, data_str):
        try:
            intervalos = data_str.split(',')
            include = set()
            exclude = set()

            for intervalo in intervalos:
                intervalo = intervalo.strip()
                if intervalo.startswith('-'):
                    intervalo = intervalo[1:]
                    target_set = exclude
                else:
                    target_set = include

                if '-' in intervalo:
                    start_date_str, end_date_str = intervalo.split('-')
                    start_date = datetime.strptime(start_date_str.strip(), self.config.get_data_format())
                    end_date = datetime.strptime(end_date_str.strip(), self.config.get_data_format())

                    delta = end_date - start_date
                    datas = {(start_date + timedelta(days=i)).strftime(self.config.get_data_format()) for i in
                             range(delta.days + 1)}
                    target_set.update(datas)
                else:
                    # Trata data única
                    date = datetime.strptime(intervalo, self.config.get_data_format()).strftime(
                        self.config.get_data_format())
                    target_set.add(date)
        except ValueError:
            include, exclude = set(), set()
        return include, exclude

    def formatar_filtro(self, chave):
        include = self.filtro[chave]['include']
        exclude = self.filtro[chave]['exclude']
        include_str = ",".join(include)
        exclude_str = ",-".join(exclude)
        if include and exclude:
            return include_str + ",-" + exclude_str
        if not include and exclude:
            return "-" + exclude_str
        else:
            return include_str + exclude_str
