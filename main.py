# -*- coding: latin-1 -*-
# Importando bibliotecas e módulos necessários
import calendar
import datetime
import re
from functools import partial

from dateutil.rrule import rrule, MONTHLY
from kivy.app import App
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

# Importando módulos customizados
from backup import Backup
from configuration import Config
from leitura import Leitura
from models import Dados
from navigation_screen_manager import NavigationScreenManager
from storage_manager import StorageManager
from testdb import TestDB


# Widget para exibir resultados individuais
class ResultWidget(BoxLayout):
    principal = StringProperty()
    data = StringProperty()
    hora = StringProperty()
    user = StringProperty()
    paginas = StringProperty()
    copias = StringProperty()
    impressora = StringProperty()
    arquivo = StringProperty()
    est = StringProperty()
    duplex = BooleanProperty()
    escala_de_cinza = BooleanProperty()


class ConfigScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.configs = None
        self.dicionario = {}
        self.config = None
        self.db_types = {'TestDB': 'test_db',
                         'Desativado': 'disabled'}

    def on_pre_enter(self, *args):
        self.config = Config()
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

    def save_printers_path(self):
        printer_path = self.ids.printer_path_input.text
        self.config._printers_path = printer_path
        self.config.save_config()

    def add_translation(self):
        chave = self.ids.chave.text.strip()
        valor = self.ids.valor.text.strip()

        # Verifica se ambos chave e valor são não vazios
        if chave and valor:
            # Atualiza o dicionário, garantindo que a chave esteja em minúsculas e o valor em título
            self.dicionario[chave.lower()] = valor.title()
        self.ids.chave.text, self.ids.valor.text = '', ''

    def save_additions_on_translate(self):
        dicionario = self.configs['_traduzir']
        for key, value in self.dicionario.items():
            dicionario[key] = value
        self.config._traduzir = dicionario
        self.config.save_config()

    def save_month_year(self):
        month = self.ids.month.text.replace(" ", "") or "1-12"
        todos = re.split(r',', month)

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
        months_list = [calendar.month_name[numero] for numero in meses_ordenados]
        months_list_to_show = [int(month) for month in (map(str, meses_ordenados))]
        months = ", ".join(months_list)
        self.config._default_months = months
        self.config._default_months_list = months_list
        self.config._default_months_list_to_show = months_list_to_show

        texto = self.ids.year.text.replace(" ", "")
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


class ListScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.lista = None
        self.config = None

    def on_pre_enter(self, *args):
        self.config = Config()
        self.lista = self.config.get_configs().get("_traduzir")
        self.update_list()

    def button_delete(self, key, *args):
        dicionario = self.lista
        if key in dicionario:
            del dicionario[key]
        self.update_list()

    def on_button_save(self):
        self.config._traduzir = self.lista
        self.config.save_config()

    def update_list(self):
        grid = self.ids.list_grid
        grid.clear_widgets()
        for key, value in self.lista.items():
            item_box = BorderedBoxLayout(size_hint_y=None, height=40)
            label = Label(text=f'{key.title()} traduzido para {value.title()}', size_hint_x=0.8)
            button = Button(text='Remover', size_hint_x=0.2, on_press=partial(self.button_delete, key))
            item_box.add_widget(label)
            item_box.add_widget(button)
            grid.add_widget(item_box)


class BorderedBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BorderedBoxLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Cor branca para o fundo
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        self.line.rectangle = (self.x, self.y, self.width, self.height)


# Widget para exibir resultados totais
class TotalWidget(BoxLayout):
    user = StringProperty()
    arquivo = StringProperty()
    total = NumericProperty()


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
    months_list_to_show = StringProperty(str(_default_months_list_to_show).replace("[", "").replace("]", ""))
    total = []

    def on_data_validate(self, widget):
        """Valida e configura a lista de meses."""
        texto = widget.text.replace(" ", "") or "1-12"
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
            db = TestDB('documentos.db')
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


class ResultScreen(Screen):
    """Tela que exibe os resultados processados."""
    config = Config().get_configs()
    recycleView = ObjectProperty(None)
    dados = None
    clicado = False
    msg_str = StringProperty("")
    msg_col = ColorProperty((1, 0, 0))
    default_root = config.get('_printers_path')
    printers_root = StringProperty(default_root)
    BL = BoxLayout(size_hint=(1, 0.1))
    backup_button_csv = Button(text="Criar CSVs", font_size=dp(12), size_hint=(1, 1))
    backup_button_json = Button(text="Salvar em JSON", font_size=dp(12), size_hint=(1, 1))
    backup_button_bd = Button(text="Salvar no Banco de Dados", font_size=dp(11), size_hint=(1, 1))
    BL.add_widget(backup_button_json)
    BL.add_widget(backup_button_csv)
    BL.add_widget(backup_button_bd)

    def msg_change(self, msg: str = "", col: tuple = (1, 0, 0)):
        """Altera a mensagem e sua cor."""
        self.msg_str = str(msg)
        self.msg_col = col

    def on_printers_root_validate(self, widget):
        """Valida e configura o caminho da raiz das impressoras."""
        self.printers_root = widget.text or self.default_root
        widget.text = self.printers_root

    def result(self):
        """Manipula a exibição dos resultados."""
        self.dados = Leitura(root=self.printers_root).processar_arquivos()
        if self.dados:
            self.msg_change()
            if not self.clicado:
                self.show_data()
                self.backup_button_csv.bind(on_press=self.csv)
                self.backup_button_json.bind(on_press=self.json)
                self.backup_button_bd.bind(on_press=self.bd)
                self.ids.boxlayout_principal.add_widget(self.BL)
                self.clicado = True
            else:
                self.show_data()
        else:
            self.recycleView.data = []

    def show_data(self):
        """Exibe os dados no RecycleView."""
        self.recycleView.data = [dado.get_dictionary() for dado in self.dados]

    def csv(self, widget):
        """Cria backup em CSV."""
        if self.dados:
            Backup(lista=self.dados).gerar_csv()
            Backup(lista=self.dados).gerar_total()
            self.msg_change("Csvs criados com sucesso.", (0, 1, 0, .5))
        else:
            self.msg_change("Não foi possível encontrar dados para salvar.")

    def json(self, widget):
        """Cria backup em JSON."""
        if self.dados:
            dados = [dado.get_dictionary() for dado in self.dados]
            StorageManager().save_data("dados", dados)
            self.msg_change("Backup em JSON criado com sucesso.", (0, 1, 0, .5))
        else:
            self.msg_change("Não foi possível encontrar dados para salvar.")

    def bd(self, widget):
        """Cria backup no Banco de Dados."""
        if self.config["_tipo_de_db"] == "test_db" and self.dados:
            bd = TestDB('documentos.db')
            bd.inserir_documentos(dados=self.dados)
            bd.fechar_conexao()
            self.msg_change("Backup salvo no Banco de Dados com sucesso.", (0, 1, 0, .5))
        else:
            self.msg_change("Não foi possível encontrar dados para salvar, ou você não configurou o banco de dados "
                            "corretamente.")


class MyScreenManager(NavigationScreenManager):
    pass


class MainMenu(Screen):
    pass


class Printers(App):
    """Aplicação principal."""

    manager = ObjectProperty(None)

    def build(self):
        self.manager = MyScreenManager()
        return self.manager


# Executa a aplicação
if __name__ == '__main__':
    Printers().run()
