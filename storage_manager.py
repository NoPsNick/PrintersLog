# -*- coding: latin-1 -*-
import json


class StorageManager:
    """
    Classe para manipulação de documento JSON.
    """

    def load_data(self, data_name) -> list:
        """
        Carregar dados de um JSON através de seu nome.
        :param data_name: Nome do dados para busca.
        :return: Lista dos dados obtidos através do nome fornecido.
        """
        filename = self.get_filename(data_name)
        try:
            file = open(filename, "r")
            data = file.read()
            file.close()
        except FileNotFoundError:
            return []
        return json.loads(data)

    def save_data(self, data_name, data_content: list[dict]) -> None:
        """
        Salvar dados em JSON através de um nome.
        :param data_name: Nome no qual o dado será salvo.
        :param data_content: Dados para serem salvos.
        """
        filename = self.get_filename(data_name)
        data_str = json.dumps(data_content, indent=4)
        file = open(filename, "w")
        file.write(data_str)
        file.close()

    @staticmethod
    def get_filename(data_name):
        return "./jsons/" + data_name + ".json"
