# -*- coding: latin-1 -*-
from kivy.uix.screenmanager import ScreenManager


class NavigationScreenManager(ScreenManager):
    """
    Classe para gerenciamento de telas do Kivy.
    """
    screen_stack = []

    def push(self, screen_name) -> None:
        """
        Altera a tela atual para a tela fornecidada caso ela já não tenha sido acessada.
        :param screen_name: Identificador da tela.
        """
        if screen_name not in self.screen_stack:
            self.screen_stack.append(self.current)
            self.transition.direction = "left"
            self.current = screen_name

    def pop(self) -> None:
        """
        Altera para a tela anterior da atual caso tenha.
        """
        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.transition.direction = "right"
            self.current = screen_name
