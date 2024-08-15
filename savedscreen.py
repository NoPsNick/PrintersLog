# -*- coding: latin-1 -*-
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from backup import Backup
from configuration import Config
from models import Dados
from storage_manager import StorageManager
from visualdados import VisualDocumentos

Builder.load_file("savedscreen.kv", encoding='latin-1')


class SavedScreen(Screen):
    """Tela que exibe os dados salvos e que permite filtragem."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.config = Config()
        self.configs = self.config.get_configs()
        # Obtendo configura��es padr�es
        (
            self._traduzir,
            self._tipo_de_db,
            self._filters
        ) = (
            self.configs["_traduzir"],
            self.configs["_tipo_de_db"],
            self.configs["_filters"]
        )
        self.recycleView = ObjectProperty(None)
        self.totalView = ObjectProperty(None)
        self.dados = None
        self.clicado = False
        self.total = []

    def on_enter(self, *args):
        self.config.read_configs()
        self.configs = self.config.get_configs()
        (
            self._traduzir,
            self._tipo_de_db,
            self._filters
        ) = (
            self.configs["_traduzir"],
            self.configs["_tipo_de_db"],
            self.configs["_filters"]
        )

    def _initialize_data(self):
        """Inicializa dados e totais."""
        self.dados = []
        self.total = []
        self.show_data()
        self.show_total()

    def _process_data(self, dados):
        """Processa os dados para filtro e c�lculo de totais."""
        show = self._filtro(dados)

        if show:
            self.dados = show
            totais, total = Backup(lista=self.dados).get_totals()
            self.total = [{"user": key, "total": value} for key, value in total.items()]
            self.show_data()
            self.show_total()
        else:
            self._initialize_data()

    def on_button_click(self):
        """Manipula o clique do bot�o para filtrar e exibir dados do banco de dados."""
        if self._tipo_de_db == "test_db":
            dados = VisualDocumentos().pegar_documentos()
        else:
            dados = StorageManager().load_data("dados")

        if not dados:
            self._initialize_data()
        else:
            self._process_data(dados)

    def on_button_relatorio(self):
        """Manipula o clique do bot�o para fazer o relat�rio dos dados em PDF."""
        if self.dados:
            screen = self.manager.get_screen("PDFScreen")
            screen.change(conteudo={"lista": self.dados, "filtros": self.config.get_show_filter()})
            self.manager.push(screen.name)

    def _deve_remover(self, dado: Dados):
        """Determina se um dado deve ser removido com base no filtro."""
        filtro = self.config.get_filter()
        for field, rules in filtro.items():
            include_set = set(rules.get("include", []))
            exclude_set = set(rules.get("exclude", []))

            valor_atributo = str(getattr(dado, field))

            # Se 'include' estiver vazio, incluir todos exceto os 'exclude'
            if not include_set:
                if valor_atributo in exclude_set:
                    return True
            else:
                if valor_atributo not in include_set or valor_atributo in exclude_set:
                    return True
        return False

    def _filtro(self, dados: list[Dados]) -> list[Dados]:
        dados_removidos = [dado for dado in dados if self._deve_remover(dado)]

        # Dados n�o removidos
        dados_nao_removidos = [dado for dado in dados if dado not in dados_removidos]
        for dado in dados_nao_removidos:
            dado.paginas = str(dado.paginas)
            dado.copias = str(dado.copias)

        return dados_nao_removidos

    def show_data(self):
        """Exibe os dados no RecycleView."""
        self.recycleView.data = [dado.get_dictionary_to_show(self.config.get_data_format()) for dado in self.dados]

    def show_total(self):
        """Exibe os totais no TotalView."""
        self.totalView.data = self.total
