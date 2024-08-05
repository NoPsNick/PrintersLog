from kivy.graphics import Color, Line
from kivy.uix.boxlayout import BoxLayout


class BorderedBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BorderedBoxLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Cor branca para o fundo
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        self.line.rectangle = (self.x, self.y, self.width, self.height)
