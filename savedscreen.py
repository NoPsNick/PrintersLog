# -*- coding: latin-1 -*-
import calendar
import datetime
import re

from dateutil.rrule import rrule, MONTHLY
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from backup import Backup
from configuration import Config
from models import Dados
from storage_manager import StorageManager
from testdb import TestDB

Builder.load_file("savedscreen.kv", encoding='latin-1')


class SavedScreen(Screen):
    """Tela que exibe os dados salvos e permite filtragem por mês e ano."""
    configs = Config().get_configs()
    # Obtendo configurações padrões
    (
        _traduzir,
        _default_months,
        _default_months_list,
        _default_months_list_to_show,
        _default_year,
        _default_years_list,
        _tipo_de_db
    ) = (
        configs["_traduzir"],
        configs["_default_months"],
        configs["_default_months_list"],
        configs["_default_months_list_to_show"],
        configs["_default_year"],
        configs["_default_years_list"],
        configs["_tipo_de_db"]
    )
    recycleView = ObjectProperty(None)
    totalView = ObjectProperty(None)
    dados = None
    clicado = False
    str_year = _default_year
    end_year = _default_year
    years_list = _default_years_list
    years_to_show = StringProperty(str(_default_year))
    months = StringProperty(_default_months)
    months_list = _default_months_list
    months_list_to_show = StringProperty(str(_default_months_list_to_show).replace(
        "[", "").replace("]", ""))
    total = []

    def on_pre_enter(self, *args):
        self.configs = Config().get_configs()
        (
            _traduzir,
            _default_months,
            _default_months_list,
            _default_months_list_to_show,
            _default_year,
            _default_years_list,
            _tipo_de_db
        ) = (
            self.configs["_traduzir"],
            self.configs["_default_months"],
            self.configs["_default_months_list"],
            self.configs["_default_months_list_to_show"],
            self.configs["_default_year"],
            self.configs["_default_years_list"],
            self.configs["_tipo_de_db"]
        )
        self.str_year = _default_year
        self.end_year = _default_year
        self.years_list = _default_years_list
        self.years_to_show = str(_default_year)
        self.months = _default_months
        self.months_list = _default_months_list
        self.months_list_to_show = str(_default_months_list_to_show).replace(
            "[", "").replace("]", "")

    def on_data_validate(self, widget):
        """Valida e configura a lista de meses."""
        texto = widget.text.strip().replace(" ", "")
        texto = texto if texto != "0" else "1-12"
        todos = re.split(r',', texto)

        pegar_meses = [re.findall(r'\b\d+\b', cada) for cada in todos]
        meses_set, to_show = set(), []

        for lis in pegar_meses:
            if len(lis) == 2:
                str_dt = datetime.date(int(self.str_year), int(lis[0]), 1)
                end_dt = datetime.date(int(self.end_year), int(lis[1]), 1)
                lista = [dt.month for dt in rrule(MONTHLY, dtstart=str_dt, until=end_dt)]
                meses_set.update(lista)
                to_show.extend(lista)
            elif len(lis) == 1:
                meses_set.add(int(lis[0]))
                to_show.append(int(lis[0]))

        meses_ordenados = sorted(meses_set)
        self.months_list = [calendar.month_name[numero] for numero in meses_ordenados]
        self.months_list_to_show = ", ".join(map(str, meses_ordenados))
        self.months = ", ".join(self.months_list)

    def on_year_validate(self, widget):
        """Valida e configura a lista de anos."""
        texto = widget.text.replace(" ", "")
        todos = re.split(",", texto)
        pegar_anos = [re.findall(r'\b\d+\b', cada) for cada in todos]

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
        self.years_to_show = ", ".join(map(str, anos_ordenados))
        self.years_list = [[ano] for ano in anos_ordenados]

    def on_button_click(self):
        """Manipula o clique do botão para filtrar e exibir dados."""
        dados = StorageManager().load_data("dados")
        show, anos_verify = [], []

        # Verifica se há um 0 em years_list, se sim, pega todos os anos
        if any(0 in sublist for sublist in self.years_list):
            anos_verify = dados
        else:
            for anos in self.years_list:
                anos_verify.extend(self._filtrar_anos(dados, anos))

        for mes in self.months_list:
            show.extend(dado for dado in anos_verify if self._verify_month(mes, self._translate(dado.get("data"))))

        if show:
            self.dados = [Dados(**dado) for dado in show]
            totais, total = Backup(lista=self.dados).get_totals()
            self.total = [{"user": key, "total": value} for key, value in total.items()]
        else:
            self.dados = []
            self.total = []

        self.show_data()
        self.show_total()

    def on_button_click_db(self):
        """Manipula o clique do botão para filtrar e exibir dados do banco de dados."""
        dados = []
        if self._tipo_de_db == "test_db":
            db = TestDB('./dbs/documentos.db')
            dados = db.buscar_documentos()
            db.fechar_conexao()
        else:
            return None
        show, anos_verify = [], []

        # Verifica se há um 0 em years_list, se sim, pega todos os anos
        if any(0 in sublist for sublist in self.years_list):
            anos_verify = dados
        else:
            for anos in self.years_list:
                anos_verify.extend(self._filtrar_anos(dados, anos))

        for mes in self.months_list:
            show.extend(dado for dado in anos_verify if self._verify_month(mes, self._translate(dado.get("data"))))

        if show:
            if self._tipo_de_db == "test_db":
                for dado in show:
                    dado["duplex"] = bool(dado.get('duplex'))
                    dado["paginas"] = str(dado.get('paginas'))
                    dado["escala_de_cinza"] = bool(dado.get('escala_de_cinza'))
                    dado["copias"] = str(dado.get('copias'))

            self.dados = [Dados(**dado) for dado in show]
            totais, total = Backup(lista=self.dados).get_totals()
            self.total = [{"user": key, "total": value} for key, value in total.items()]
        else:
            self.dados = []
            self.total = []

        self.show_data()
        self.show_total()

    def _filtrar_anos(self, dados, anos):
        """Filtra os dados por anos."""
        if len(anos) == 2:
            return [dado for dado in dados if self._verify_between_years(anos, self._translate(dado.get("data")))]
        elif len(anos) == 1:
            return [dado for dado in dados if self._verify_year(anos, self._translate(dado.get("data")))]
        return []

    def show_data(self):
        """Exibe os dados no RecycleView."""
        self.recycleView.data = [dado.get_dictionary() for dado in self.dados]

    def show_total(self):
        """Exibe os totais no TotalView."""
        self.totalView.data = self.total

    @staticmethod
    def _verify_month(month, verificar):
        """Verifica se o mês corresponde ao dado."""
        mes_pego = datetime.datetime.strptime(verificar, '%d %B %Y').strftime("%B")
        return mes_pego == month

    @staticmethod
    def _verify_between_years(anos: list, ano: str):
        """Verifica se o ano está dentro do intervalo."""
        ano_pego = datetime.datetime.strptime(ano, '%d %B %Y').date().year
        return anos[0] <= ano_pego <= anos[1]

    @staticmethod
    def _verify_year(anos: list, ano: str):
        """Verifica se o ano corresponde ao dado."""
        ano_pego = datetime.datetime.strptime(ano, '%d %B %Y').date().year
        return ano_pego == anos[0]

    def _translate(self, data):
        """Traduz a data para o formato adequado."""
        return re.sub('|'.join(self._traduzir.keys()),
                      lambda x: self._traduzir[x.group().lower()],
                      data,
                      flags=re.IGNORECASE)
