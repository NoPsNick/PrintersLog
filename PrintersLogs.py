# -*- coding: latin-1 -*-
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from navigation_screen_manager import NavigationScreenManager


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


# Widget para exibir resultados totais
class TotalWidget(BoxLayout):
    user = StringProperty()
    arquivo = StringProperty()
    total = NumericProperty()


class MyScreenManager(NavigationScreenManager):
    pass


class MainMenu(Screen):
    pass


class PrintersLogs(App):
    """Aplicação principal."""

    manager = ObjectProperty(None)

    def build(self):
        self.manager = MyScreenManager()
        return self.manager


# Executa a aplicação
if __name__ == '__main__':
    PrintersLogs().run()
