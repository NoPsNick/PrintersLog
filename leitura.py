import datetime
import os
import re  # Importa a biblioteca re para utilizar expressões regulares para pesquisa e manipulação de strings
from glob import glob

import pandas as pd
from bs4 import BeautifulSoup  # Importa BeautifulSoup da biblioteca bs4 para analisar e manipular arquivos HTML

from configuration import Config
from models import \
    Dados  # Importa a classe Dados do módulo models, para armazenar dados extraídos de arquivos HTML


class Leitura:
    """
    Classe responsável por ler arquivos HTML de um diretório específico
    (por padrão, ".\\printers\\") e extrair informações, retornando-as como um dicionário.
    """
    _remover = ["\n", "<td>", "</td>", "<tr>", "</tr>",
                "</span>", "<title>PaperCut Print Logger : Print Logs - ",
                "</title>"]  # Lista de strings HTML e caracteres a serem removidos durante a leitura do arquivo

    def __init__(self, root: str = None):
        self.config = Config()
        self.configs = self.config.get_configs()
        self.root = root if root else self.configs.get(
            '_printers_path')  # Inicializa a classe com o diretório especificado (ou o padrão)

    def _ler(self, filepath) -> list[Dados]:
        """
        Função responsável por ler e extrair dados de um único arquivo HTML.
        :param filepath: Caminho do arquivo que será lido.
        :return: Lista dos dados extraídos.
        """
        if filepath.endswith('.csv'):
            return self._ler_csv(filepath)

        try:
            with open(filepath, 'r', encoding='latin-1') as file:
                content = file.read()  # Lê o conteúdo do arquivo HTML

            soup = BeautifulSoup(content, 'html.parser')  # Analisa o conteúdo HTML usando BeautifulSoup
            title = soup.title.string  # Extrai o título do documento HTML
            date_match = re.search(r'(\d{1,2} \w+ \d{4})',
                                   title)  # Usa expressão regular para encontrar a data no título
            if date_match:
                date = datetime.datetime.strptime(self.config.translate(
                    date_match.group(1)), '%d %B %Y').strftime(
                    self.config.get_data_format())  # Se a data for encontrada, armazena-a na variável date
            else:
                date = "1 janeiro 0001"

            rows = soup.select('table.results tr')  # Seleciona todas as linhas da tabela com a classe 'results'
            data_list = []  # Inicializa a lista para armazenar os dados extraídos

            for row in rows[1:]:  # Itera sobre as linhas da tabela, ignorando a primeira (cabeçalho)
                cells = row.find_all('td')  # Encontra todas as células (td) na linha
                if len(cells) == 9:  # Verifica se a linha tem pelo menos 9 células
                    time = cells[0].text.strip()  # Extrai e limpa o texto da primeira célula (hora)
                    user = cells[1].text.strip()  # Extrai e limpa o texto da segunda célula (usuário)
                    pages = cells[2].text.strip()  # Extrai e limpa o texto da terceira célula (páginas)
                    copies = cells[3].text.strip()  # Extrai e limpa o texto da quarta célula (cópias)
                    print_queue = cells[4].text.strip()  # Extrai e limpa o texto da quinta célula (fila de impressão)
                    document = cells[5].text.strip().replace('\n',
                                                             ' ')  # Extrai e limpa o texto da sexta célula (documento)
                    station = cells[6].text.strip()  # Extrai e limpa o texto da sétima célula (estação)
                    duplex = cells[7].text.strip() == 'Yes'  # Verifica se a oitava célula é 'Yes' para definir duplex
                    grayscale = cells[
                                    8].text.strip() == 'Yes'  # Verifica se a nona célula é 'Yes' para definir escala de cinza

                    # Adiciona os dados extraídos na lista como uma instância da classe Dados
                    data_list.append(
                        Dados(os.path.basename(filepath), date, time, user, pages, copies, print_queue,
                              document, station, duplex, grayscale))
        except AttributeError:
            data_list = []
        return data_list  # Retorna a lista de dados extraídos

    def _ler_csv(self, filepath) -> list[Dados]:
        """
        Função responsável por ler e extrair dados de um único arquivo CSV.
        :param filepath: Caminho do arquivo que será lido.
        :return: Lista dos dados extraídos.
        """
        try:
            dt = pd.read_csv(filepath, encoding='latin-1', header=1, keep_default_na=False, na_filter=False,
                             index_col=False)
            lista = [row for row in dt.itertuples(index=False, name=None)]
            dados = []
            for item in lista:
                data, hora = item[0].split()
                date_str = datetime.datetime.strptime(data, '%Y-%m-%d').date(
                ).strftime(self.config.get_data_format())
                date = date_str
                time = hora
                user = item[1].strip()
                pages = str(item[2]).strip()
                copies = str(item[3]).strip()
                print_queue = item[4].strip()
                document = ",".join(
                    [item[5].strip(), item[7].strip(), item[8].strip(), item[9].strip(), item[10].strip()])
                station = item[6].strip()
                duplex = item[11].strip() != 'NOT DUPLEX'
                grayscale = item[
                                12].strip() != 'NOT GRAYSCALE'
                dados.append(Dados(os.path.basename(filepath), date, time, user, pages, copies, print_queue,
                                   document, station, duplex, grayscale))
        except:
            dados = []
        return dados

    def processar_arquivos(self) -> list[Dados]:
        """
        Função responsável em processar todos os arquivos HTML e CSV no diretório especificado.
        :return: Lista de todos os dados extraídos em formato da classe Dados.
        """

        arquivos_htm = glob(os.path.join(self.root, '*.htm'))
        arquivos_html = glob(os.path.join(self.root, '*.html'))
        arquivos_csv = glob(os.path.join(self.root, '*.csv'))

        # Combina as listas de arquivos .htm e .html
        arquivos = arquivos_htm + arquivos_html + arquivos_csv

        # Inicializa a lista para armazenar os dados de todos os arquivos
        dados_completos = []
        for filepath in arquivos:
            dados = self._ler(filepath)  # Lê o arquivo e extrai os dados
            if dados:  # Se dados foram extraídos com sucesso
                dados_completos.extend(dados)  # Adiciona os dados à lista completa

        return dados_completos  # Retorna a lista completa de dados extraídos


if __name__ == '__main__':
    pass
