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
from visualdados import VisualDados

Builder.load_file("savedscreen.kv", encoding='latin-1')


class SavedScreen(Screen):
    """Tela que exibe os dados salvos e permite filtragem por mês e ano."""
    years_to_show = StringProperty()
    months = StringProperty()
    months_list_to_show = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.configs = self.config.get_configs()
        # Obtendo configurações padrões
        (
            self._traduzir,
            self._default_months,
            self._default_months_list,
            self._default_months_list_to_show,
            self._default_year,
            self._default_years_list,
            self._tipo_de_db
        ) = (
            self.configs["_traduzir"],
            self.configs["_default_months"],
            self.configs["_default_months_list"],
            self.configs["_default_months_list_to_show"],
            self.configs["_default_year"],
            self.configs["_default_years_list"],
            self.configs["_tipo_de_db"]
        )
        self.recycleView = ObjectProperty(None)
        self.totalView = ObjectProperty(None)
        self.dados = None
        self.clicado = False
        self.str_year = self._default_year
        self.end_year = self._default_year
        self.years_list = self._default_years_list
        self.total = []
        self.months_list = self._default_months_list
        self.months_list_to_show = str(self._default_months_list_to_show).replace(
            "[", "").replace("]", "")

    def on_enter(self, *args):
        self.config.read_configs()
        self.configs = self.config.get_configs()
        (
            self._traduzir,
            self._default_months,
            self._default_months_list,
            self._default_months_list_to_show,
            self._default_year,
            self._default_years_list,
            self._tipo_de_db,
            self._filters
        ) = (
            self.configs["_traduzir"],
            self.configs["_default_months"],
            self.configs["_default_months_list"],
            self.configs["_default_months_list_to_show"],
            self.configs["_default_year"],
            self.configs["_default_years_list"],
            self.configs["_tipo_de_db"],
            self.configs["_filters"]
        )
        self.str_year = self._default_year
        self.end_year = self._default_year
        self.years_list = self._default_years_list
        self.years_to_show = str(self._default_year)
        self.months = self._default_months
        self.months_list = self._default_months_list
        self.months_list_to_show = str(self._default_months_list_to_show).replace(
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
        meses = [self.config.translate_back(calendar.month_name[numero]) for numero in meses_ordenados]
        self.months_list = [numero for numero in meses_ordenados]
        self.months_list_to_show = ", ".join(map(str, self.months_list))
        self.months = ", ".join(meses)

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

    def _initialize_data(self):
        """Inicializa dados e totais."""
        self.dados = []
        self.total = []
        self.show_data()
        self.show_total()

    def _process_data(self, dados):
        """Processa os dados para filtro e cálculo de totais."""
        show, anos_verify = [], []

        # Verifica se há um 0 em years_list, se sim, pega todos os anos
        if any(0 in sublist for sublist in self.years_list):
            anos_verify = dados
        else:
            for anos in self.years_list:
                anos_verify.extend(self._filtrar_anos(dados, anos))

        for mes in self.months_list:
            show.extend(
                dado for dado in anos_verify if self._verify_month(mes, dado.get("data")))

        show = self._filtro(show)

        if show:
            self.dados = show
            totais, total = Backup(lista=self.dados).get_totals()
            self.total = [{"user": key, "total": value} for key, value in total.items()]
        else:
            self._initialize_data()

        self.show_data()
        self.show_total()

    def on_button_click(self):
        """Manipula o clique do botão para filtrar e exibir dados."""
        dados = StorageManager().load_data("dados")
        if not dados:
            self._initialize_data()
        else:
            self._process_data(dados)

    def on_button_click_db(self):
        """Manipula o clique do botão para filtrar e exibir dados do banco de dados."""
        if self._tipo_de_db == "test_db":
            dados = VisualDados().pegar_documentos()
        else:
            dados = []

        if not dados:
            self._initialize_data()
        else:
            # Ajusta campos específicos dos dados do banco de dados
            for dado in dados:
                dado["duplex"] = bool(dado.get('duplex'))
                dado["paginas"] = str(dado.get('paginas'))
                dado["escala_de_cinza"] = bool(dado.get('escala_de_cinza'))
                dado["copias"] = str(dado.get('copias'))
            self._process_data(dados)

    def on_button_relatorio(self):
        """Manipula o clique do botão para fazer o relatório dos dados em PDF."""
        if self.dados:
            screen = self.manager.get_screen("PDFScreen")
            screen.change(self.dados, self.config.get_filter())
            self.manager.push(screen.name)

    @staticmethod
    def _deve_remover(dado, filtro):
        """Determina se um dado deve ser removido com base no filtro."""
        for field, rules in filtro.items():
            include_set = set(rules.get("include", []))
            exclude_set = set(rules.get("exclude", []))

            # Se 'include' estiver vazio, incluir todos exceto os 'exclude'
            if not include_set:
                if str(dado[field]) in exclude_set:
                    return True
            else:
                if str(dado[field]) not in include_set or dado[field] in exclude_set:
                    return True
        return False

    def _filtro(self, dados: list[dict]) -> list[Dados]:
        filtro = self.config.get_filter()

        dados_removidos = [dado for dado in dados if self._deve_remover(dado, filtro)]

        # Dados não removidos
        dados_nao_removidos = [dado for dado in dados if dado not in dados_removidos]

        # Criar a lista final de objetos Dados
        new_list = [Dados(**dado) for dado in dados_nao_removidos]
        return new_list

    def _filtrar_anos(self, dados, anos):
        """Filtra os dados por anos."""
        if len(anos) == 2:
            return [dado for dado in dados if self._verify_between_years(anos, dado.get("data"))]
        elif len(anos) == 1:
            return [dado for dado in dados if self._verify_year(anos, dado.get("data"))]
        return []

    def show_data(self):
        """Exibe os dados no RecycleView."""
        self.recycleView.data = [dado.get_dictionary() for dado in self.dados]

    def show_total(self):
        """Exibe os totais no TotalView."""
        self.totalView.data = self.total

    def _verify_month(self, month, verificar):
        """Verifica se o mês corresponde ao dado."""
        mes_pego = datetime.datetime.strptime(verificar, self.config.get_data_format()).month
        return mes_pego == month

    def _verify_between_years(self, anos: list, ano: str):
        """Verifica se o ano está dentro do intervalo."""
        ano_pego = datetime.datetime.strptime(ano, self.config.get_data_format()).date().year
        return anos[0] <= ano_pego <= anos[1]

    def _verify_year(self, anos: list, ano: str):
        """Verifica se o ano corresponde ao dado."""
        ano_pego = datetime.datetime.strptime(ano, self.config.get_data_format()).date().year
        return ano_pego == anos[0]
