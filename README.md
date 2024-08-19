# Visualização e Manipulação de Logs de Impressoras

Este projeto é uma aplicação desenvolvida em Python para a visualização e manipulação de logs de impressoras. Ele
permite a leitura de arquivos de log, a criação de documentos PDF e o salvamento dos dados em formato JSON ou em um
banco de dados.

## Funcionalidades

- **Tela Principal**: Início da aplicação com três botões:
    - **Ler os Dados das Impressões**: Acessa a tela de Resultados.
    - **Dados Salvos**: Acessa a tela de Dados Salvos.
    - **Configurações**: Acessa a tela de Configurações.

- **Tela de Resultados**:
    - Permite a leitura de arquivos `.html` e `.csv` com dados de impressão.
    - **HTML**: Espera-se que no título tenha a data no formato `%d %B %Y`, e uma as tabela com colunas: Hora, Usuário,
      Páginas, Cópias, Fila de Impressão, Documento, Estação, Duplex, e Escala de Cinza.
    - **CSV**: A primeira linha é informação extra, a segunda linha tem o cabeçalho no formato: Time, User, Pages,
      Copies, Printer, Document Name, Client, Paper Size, Language, Height, Width, Duplex, Grayscale, Size.
    - Oferece opções para salvar os resultados em JSON, CSVs compactos ou em um banco de dados.

- **Tela Dados Salvos**:
    - Permite pesquisar dados salvos.
    - Botões:
        - **Pesquisar**: Pesquisa em JSON ou banco de dados, dependendo da configuração.
        - **Filtros**: Acessa a tela de Filtros.
        - **Criar Relatório em PDF**: Acessa a tela de Relatórios, caso haja dados obtidos pelo botão Pesquisar.

- **Tela Filtros**:
    - Filtragem dos dados salvos:
        - **Data**: Permite filtrar por datas específicas, ranges ou múltiplas datas.
        - **Usuário**: Filtra dados por usuário específico ou exclui dados de usuários.
        - **Impressora**: Filtra dados por impressora.
        - **Estação**: Filtra dados por estação.
        - **Duplex e Escala de Cinza**: Filtra por características de impressão, como duplex e escala de cinza.

- **Tela Relatórios**:
    - Criação de relatórios em PDF com opções de personalização:
        - **Set Font**: Define a fonte dos textos.
        - **Add Cell**: Adiciona células ao PDF.
        - **Add Multicell**: Adiciona células que ocupam várias linhas.
        - **Add Código Python**: Adiciona código Python para criar PDFs dinamicamente.
        - **Remover Última Adição**: Remove a última adição no estilo de PDF.
        - **Estilos de PDF Salvos**: Gerencia estilos de PDF salvos.
        - **Pegar Estilo Padrão**: Obtém o estilo padrão de PDF.
        - **Salvar Estilo de PDF**: Salva o estilo de PDF atual.
        - **Gerar PDF**: Gera um PDF baseado no estilo atual.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/NoPsNick/PrintersLog.git
   cd repo

2. Crie um ambiente virtual (opcional, mas RECOMENDADO):
   ```bash 
    python -m venv env
    source env/bin/activate  # No Windows: env\Scripts\activate

3. Instale as dependências:
    ```bash 
    pip install -r requirements.txt

## Uso

1. Execute a aplicação:
    ```bash 
    python PrintersLogs.py

2. Navegue pelas diferentes telas da aplicação usando a interface gráfica.

## Estrutura dos Arquivos

- Principal: Tela inicial com botões para acessar outras partes da aplicação.
- Resultados: Tela para carregar e processar arquivos de log.
- Dados Salvos: Tela para pesquisar e visualizar dados salvos.
- Filtros: Tela para aplicar filtros aos dados salvos.
- Relatórios: Tela para criar e personalizar relatórios em PDF.
- Configurações: Tela para ajustar configurações da aplicação.
- Lista de Traduções: Tela para gerenciar traduções.
- Alterar Documentos: Tela para remover documentos lidos.

## Dependências

- kivy: Para a interface gráfica.
- fpdf: Para manipulação de PDFs.
- json: Para salvar e carregar dados em formato JSON.
- SQLAlchemy: Para armazenamento dos dados.
- pandas: Para visualização/manipulação dos dados.
- python-dateutil: Para documentação.
- numpy: Para operações matemáticas complexas.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para mais informações, entre em contato
com [serafim999junior@hotmail.com](mailto:serafim999junior@hotmail.com?subject=Contato%20do%20GitHub)

# Texto mais explicativo

- A tela **Principal**, é o início da aplicação, onde há três botões.
    - Ler os Dados das Impressões que o usuário iria para a tela de Resultados.
    - Dados Salvos que o usuário iria para a tela de Dados Salvos.
    - Configurações que o usuário iria para a tela de Configuração da aplicação.

- A tela de **Resultados** seria onde o usuário conseguiria colocar o diretório de todos os arquivos .html e .csv para
  leitura.
    - O html precisa ter no começo a data dentro do título do html no formato '%d %B %Y' e tabelas com as colunas sendo:
      Hora, Usuário, Paginas, Cópias, Fila de Impressão, Documento, Estação, Duplex e Escala de cinza.
    - O formato do csv: a primeira linha será informação extra, a segunda o cabeçalho no seguinte formato: Time, User,
      Pages, Copies, Printer, Document Name, Client, Paper Size, Language, Height, Width, Duplex, Grayscale, Size.
    - Após pressionar o botão Results, ele irá ler todos os arquivos html e csv que tenham a estruturação correta e irão
      aparecer 3 botões.
        - Salvar em JSON que irá salvar o resultado obtido em formato JSON.
        - Criar CSVs que irá salvar os resultado em arquivos csvs compactos.
        - Salvar no Banco de Dados que caso esteja ativo, irá salvar os resultados no banco de dados.

- A tela **Dados Salvos** o usuário iria conseguir fazer a pesquisa de todos os dados salvos, contendo 3 botões.
    - Pesquisar que caso o banco de dados esteja desativo nas configurações, irá fazer a busca no formato JSON, caso
      esteja ativo, irá fazer a busca no banco de dados.
    - Filtros que o usuário vai para a tela Filtros.
    - Criar Relatório em PDF que o usuário vai para a tela de Relatórios, caso tenha alguma dado obtido pelo botão de
      Pesquisar.

- A tela **Filtros** é onde o usuário poderá fazer filtragem dos dados que ele deseja obter dos que estão salvos, tendo
  dois formatos.
    - Os que ele quer e os que ele não quer.
    - Caso não seja informado(duplex e escala de cinza seria selecionar tudo) irá buscar todos os dados que possuem tal
      filtragem, caso informado ele irá buscar apenas os dados que possuem tal filtragem, caso informado com um '-'
      SINAL DE MENOS/TRAÇO NO COMEÇO, irá remover o dado da pesquisa.
    - Os tipos de filtragem são:
        - Data: O usuário irá fornecer as datas que ele desejar, caso tenha o '-' SINAL DE MENOS/TRAÇO NO COMEÇO a
          seguinte data não irá aparecer nos dados obtidos ao apertar o botão Pesquisar. Também oferece a função de
          colocar ranges ou múltiplas datas, utilizando o '-' SINAL DE MENOS/TRAÇO NO MEIO de duas datas, também podendo
          ignorar caso tenha o '-' SINAL DE MENOS/TRAÇO NO COMEÇO, exemplos > '01/01/0001-10/01/0001, 12/01/0001' irá
          devolver as seguintes datas: '03/01/0001, 07/01/0001, 08/01/0001, 05/01/0001, 02/01/0001, 12/01/0001,
          04/01/0001, 10/01/0001, 06/01/0001, 09/01/0001, 01/01/0001'
          Outro exemplo usando a remoção: '01/01/0001-10/01/0001, -05/01/0001, -07/01/0001-09/01/0001' irá devolver '
          03/01/0001, 02/01/0001, 04/01/0001, 10/01/0001, 06/01/0001,01/01/0001, -07/01/0001, -08/01/0001, -05/01/0001,
          -09/01/0001'.
        - Usuário: Seguindo a mesma lógica, caso tenha o '-' SINAL DE MENOS/TRAÇO NO COMEÇO, ele não irá aparecer, e
          caso tenha sem, irá aparecer apenas estes. Caso não tenha nenhum, irá aparecer todos. Exemplos > Caso
          coloque 'Joao' É CASE SENSITIVE, irá aparecer apenas dados do usuário Joao, caso coloque '-Joao' É CASE
          SENSITIVE, irá aparecer todos, menos os dados do usuário Joao.
        - Impressora: Igual o de usuário, porém com o campo Impressora.
        - Estação: Igual o de usuário, porém com o campo Estação.
        - Duplex e Escala de cinza: Você pode marcar uma caixa, onde caso queira os que tenham, marcar o Com, caso
          queira os não tenham marcar os Sem, exemplos:
          Com Duplex, Sem Duplex, Com Escala de Cinza, Sem Escala de Cinza todos selecionados irá pegar todos.
          Com Duplex, Com Escala de Cinza, Sem Escala de Cinza selecionados, irá pegar todos, menos aqueles que não
          foram utilizados a forma de impressão Duplex.

- A tela de **Relatórios** o usuário conseguirá criar o estilo de PDF e salvá-lo do jeito que estiver, com as seguintes
  ferramentas.
    - No lado esquerdo terá uma tela demonstrando os comandos que foram adicionados ao estilo de PDF, que irá gerar um
      PDF.
    - Os seguintes botões >
        - Set Font > O usuário irá abrir um Popup pedindo as seguintes informações: Family, Style e Size, que seria as
          informações da fonte dos textos que estão abaixo deste comando.
        - Add Cell > O usuário irá abrir um Popup pedindo as seguintes informações: Width, Height, Text, Border(0=Não,
          1=Sim), Quebra de Linha(0=Não, 1=Sim) e Align, que seria as informações para a criação de uma célula dentro do
          PDF.
        - Add Multicell > O usuário irá abrir um Popup pedindo as seguintes informações: Width, Height, Text, Border(
          0=Não, 1=Sim) e Align, que seria as informações para a criação de uma célula que ocupa diversas linhas caso
          ultrapasse o Width do PDF dentro do PDF.
        - Add código Python > Irá abrir um Popup onde o usuário conseguirá escrever seu código python para a criação do
          PDF de forma DINÂMICA. As seguintes funções podem ser utilizadas pelo usuário:
            - As padrões:
                - conteudo um dicionário onde a chave é o que ele quer pegar, o usuário consegue acessar os dados que
                  foram obtidos na tela de Dados Salvos, que a chave seria 'lista', exemplo: conteudo['lista'] seria uma
                  lista de objetos Dados contendo os seguintes parâmetros: id, principal, data, hora, user, paginas,
                  copias, impressora, arquivo, est, duplex, escala_de_cinza, jeito de escrever um código para colocar as
                  informações em cells e multicells e também como acessar o conteudo['filtros'] pode ser encontrado ao
                  utilizar o botão Pegar Estilo Padrão que se encontra na tela.
                - math biblioteca para fazer operações matemáticas.
                - datetime biblioteca para manipulação de datas.
                - pdf para manipulação do PDF.
                - set_font para setar fonte dos textos após este comando.
                - cell para adicionar uma cell no pdf.
                - multi_cell para adicionar multicell no pdf.
            - As funções customizadas(Pode ser encontrado como utilizar através do botão Pegar Estilo Padrão):
                - formatar_datas para pegar todas as datas que estão presentes nos dados obtidos.
                - truncate_text para adicionar '...' em uma parte do texto caso ele seja maior do que o estipulado.
                - calcular_periodo para receber três variáveis dentro de uma tupla, (primeira data, última data, dias
                  entre elas).
                - pegar_totais para pegar duas variáveis dentro de uma tupla, (totais, total), o totais seria um
                  dicionário onde a chave é o arquivo principal e os valores um dicionário onde a chave é o usuário e o
                  valor o total de folhas, o total seria um dicionário onde a chave é o usuário e o valor o total de
                  folhas.
                - formato_da_data para pegar o formato de data padrão.
        - Remover última adição > Remove a última adição no estilo de PDF.
        - Estilos de PDF Salvos > Abre um Popup contendo os nomes dos estilos de PDF salvos, podendo também pesquisar
          pelo nome ao escrever e clicar no botão Buscar estilo de PDF.
        - Pegar estilo padrão > Pega o estilo padrão de PDF, nele há vários códigos python para poder aprender como
          manipular as funções utilizáveis.
        - Salvar estilo de PDF > Abre um Popup onde é necessário informar um nome para salvar o estilo atual, caso
          esteja com o banco de dados desativado, ele irá salvar no formato json, caso contrário ele irá salvar no banco
          de dados.
        - Gerar PDF > Gera um PDF baseado no estilo de PDF atual.

- A tela de **Configurações** é a tela onde o usuário consegue alterar partes do aplicativo.
    - Padrões e tipo do banco de dados, onde caso o tipo esteja desativado, a aplicação irá funcionar através de
      salvamentos em JSON, caso contrário, irá funcionar através de salvamentos no banco de dados.
    - Na parte superior encontra-se as traduções, que serve para casos de problemas de localização, não sendo
      recomendado alterar caso não seja necessário, contendo um botão para salvar a tradução e outro para ir para a tela
      Lista de Traduções.
    - Em seguida está o tipo do Banco de Dados, Ativado ou Desativado.
    - Em seguida o caminho padrão dos logs que ficará como padrão ao entrar na tela de Resultados.
    - Por fim um botão que irá encaminhar o usuário para a tela Alterar Documentos.

- A tela **Lista de Traduções** irá listar todas as traduções da aplicação.
    - Onde irá traduzir do primeiro para o segundo, podendo remover, e para salvar é necessário apertar no botão
      Aplicar, caso contrário, não será efetuado a ação de remoção.
    - **Cuidado: a ação de remoção não é possível ser revertida!**

- A tela de **Alterar Documentos** é onde irá listar todos os htmls e csvs que foram salvos.
    - Pode-se apertar no botão Remover Documento
    - Escrever o nome e apertar em Remover.
        - Os botões irão abrir um Popup demonstrando todos os dados que serão removidos do Banco de Dados.
    - **Aviso: Esta ação não é plausível em caso de salvamentos em JSON. Cuidado: a ação de remoção não é possível ser
      revertida!**