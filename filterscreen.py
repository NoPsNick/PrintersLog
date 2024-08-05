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
        """Lê as configurações e atualiza os textos dos inputs."""
        self.config.read_configs()
        self.filtro = self.config.get_filter()
        self._update_inputs()

    def _update_inputs(self):
        """Atualiza os inputs da tela com base nas configurações atuais."""
        self.ids.data_input.text = self._formatar_filtro('data')
        self.ids.usuario_input.text = self._formatar_filtro('user')
        self.ids.impressora_input.text = self._formatar_filtro('impressora')
        self.ids.estacao_input.text = self._formatar_filtro('est')
        self.ids.duplex_true.active = self._is_active('duplex', True)
        self.ids.duplex_false.active = self._is_active('duplex', False)
        self.ids.escala_true.active = self._is_active('escala_de_cinza', True)
        self.ids.escala_false.active = self._is_active('escala_de_cinza', False)

    def _is_active(self, field, value):
        """Verifica se um valor booleano está incluído nas configurações do filtro."""
        return str(value) in self.filtro.get(field, {}).get("include", [])

    def filter_results(self, *inputs):
        """Filtra os resultados com base nos inputs fornecidos e salva as configurações."""
        filters = self._initialize_filters()
        self._populate_filters(filters, inputs)
        self._finalize_filters(filters)
        self.config.alter_filter(filters)
        self.config.save_config()
        self.change_texts()

    def _initialize_filters(self):
        """Inicializa o dicionário de filtros."""
        field_names = self.config.field_names
        return {field: {"include": set(), "exclude": set()} for field in field_names}

    def _populate_filters(self, filters, inputs):
        """Popula os filtros com os valores dos inputs."""
        field_names = self.config.field_names
        for field, input_text in zip(field_names, inputs):
            if field in ["duplex", "escala_de_cinza"]:
                self._handle_boolean_field(filters, field, input_text)
            elif field == "data":
                self._handle_date_field(filters, field, input_text)
            else:
                self._handle_text_field(filters, field, input_text)

    def _handle_boolean_field(self, filters, field, input_text):
        """Manipula os campos booleanos, adicionando valores de inclusão e exclusão."""
        include_true = input_text.get('True', False)
        include_false = input_text.get('False', False)
        self._update_filter(filters[field], include_true, "True")
        self._update_filter(filters[field], include_false, "False")

    @staticmethod
    def _update_filter(filter_dict, include, value):
        """Atualiza o dicionário de filtros com base no valor booleano fornecido."""
        if include:
            filter_dict["include"].add(value)
        else:
            filter_dict["exclude"].add(value)

    def _handle_date_field(self, filters, field, input_text):
        """Manipula o campo de data, gerando intervalos de datas para inclusão e exclusão."""
        if input_text.split():
            include, exclude = self.gerar_datas_multiplos_intervalos(input_text)
            filters[field]["include"] = include
            filters[field]["exclude"] = exclude

    @staticmethod
    def _handle_text_field(filters, field, input_text):
        """Manipula os campos de texto, adicionando palavras aos filtros de inclusão e exclusão."""
        words = [word.strip() for word in input_text.split(',')]
        for word in words:
            if word:
                if word.startswith('-'):
                    filters[field]["exclude"].add(word.lstrip('-'))
                else:
                    filters[field]["include"].add(word)

    @staticmethod
    def _finalize_filters(filters):
        """Finaliza os filtros, removendo duplicatas e convertendo sets vazios para listas."""
        for field, filter_dict in filters.items():
            filter_dict["include"] -= filter_dict["exclude"]
            filter_dict["include"] = list(filter_dict["include"]) if filter_dict["include"] else []
            filter_dict["exclude"] = list(filter_dict["exclude"]) if filter_dict["exclude"] else []

    def gerar_datas_multiplos_intervalos(self, data_str):
        """
        Gera múltiplos intervalos de datas a partir de uma string de entrada.
        Como, caso a entrada seja 01/01/2020-05/01/2020, ele devolve 01/01/2020,02/01/2020,03/01/2020,04/01/2020,05/01/2020.
        Caso tenha datas com - no começo, irá adicionar aos excluídos, como, caso seja -01/01/2020-05/01/2020, ele devolve o mesmo
        porém com - no começo delas, para indicar que foram adicionadas para filtrar(remover) dos dados.
        """
        try:
            intervalos = data_str.split(',')
            include, exclude = set(), set()

            for intervalo in intervalos:
                intervalo = intervalo.strip()
                target_set = exclude if intervalo.startswith('-') else include
                intervalo = intervalo.lstrip('-')

                if '-' in intervalo:
                    datas = self._gerar_intervalo_de_datas(intervalo)
                    target_set.update(datas)
                else:
                    date = self._parse_single_date(intervalo)
                    target_set.add(date)
        except ValueError:
            include, exclude = set(), set()
        return include, exclude

    def _gerar_intervalo_de_datas(self, intervalo):
        """Gera todas as datas dentro de um intervalo especificado."""
        start_date_str, end_date_str = intervalo.split('-')
        start_date = self._parse_date(start_date_str)
        end_date = self._parse_date(end_date_str)

        delta = end_date - start_date
        return {(start_date + timedelta(days=i)).strftime(self.config.get_data_format()) for i in range(delta.days + 1)}

    def _parse_single_date(self, date_str):
        """Analisa uma data única e retorna como string formatada."""
        return self._parse_date(date_str).strftime(self.config.get_data_format())

    def _parse_date(self, date_str):
        """Analisa uma string de data e retorna um objeto datetime."""
        return datetime.strptime(date_str.strip(), self.config.get_data_format())

    def _formatar_filtro(self, chave):
        """Formata o filtro para exibição nos inputs."""
        include = self.filtro[chave]['include']
        exclude = self.filtro[chave]['exclude']
        include_str = ",".join(include)
        exclude_str = ",-".join(exclude)
        if include and exclude:
            return f"{include_str},-{exclude_str}"
        return f"-{exclude_str}" if not include and exclude else include_str
