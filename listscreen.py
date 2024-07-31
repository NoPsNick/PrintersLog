# -*- coding: latin-1 -*-
from functools import partial

from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from configuration import Config

Builder.load_file("listscreen.kv", encoding='latin-1')


class ListScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.lista = None
        self.config = Config()

    def on_pre_enter(self, *args):
        self.config.read_configs()
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
