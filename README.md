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
    - **HTML**: Espera-se que no título tenha a data no formato `%d %B %Y`, e uma tabela com colunas: Hora, Usuário,
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

Para mais informações, entre em contato(Irá abrir o seu aplicativo de email)
com [serafim999junior@hotmail.com](mailto:serafim999junior@hotmail.com?subject=Contato%20do%20GitHub).

# Texto mais explicativo

- A tela **Principal** é o início da aplicação, onde há três botões.
    - Ler os Dados das Impressões que o usuário vai para a tela de Resultados.
    - Dados Salvos que o usuário vai para a tela de Dados Salvos.
    - Configurações que o usuário vai para a tela de Configuração da aplicação.

- A tela de **Resultados** é onde o usuário consegue colocar o diretório de todos os arquivos .html e .csv para leitura.
    - O html precisa ter no começo a data dentro do título do html no formato '%d %B %Y' e tabelas com as colunas sendo:
      Hora, Usuário, Paginas, Cópias, Fila de Impressão, Documento, Estação, Duplex e Escala de cinza.
    - O formato do csv: a primeira linha é informação extra, a segunda o cabeçalho no seguinte formato: Time, User,
      Pages, Copies, Printer, Document Name, Client, Paper Size, Language, Height, Width, Duplex, Grayscale, Size.
    - Após pressionar o botão Results, ele lê todos os arquivos html e csv que tenham a estruturação correta e aparecem 3 botões.
        - Salvar em JSON que salva o resultado obtido em formato JSON.
        - Criar CSVs que salva os resultados em arquivos csvs compactos.
        - Salvar no Banco de Dados que, caso esteja ativo, salva os resultados no banco de dados.

- A tela **Dados Salvos** o usuário consegue fazer a pesquisa de todos os dados salvos, contendo 3 botões.
    - Pesquisar que, caso o banco de dados esteja desativado nas configurações, faz a busca no formato JSON; caso esteja ativo, faz a busca no banco de dados.
    - Filtros que o usuário vai para a tela Filtros.
    - Criar Relatório em PDF que o usuário vai para a tela de Relatórios, caso tenha algum dado obtido pelo botão de Pesquisar.

- A tela **Filtros** é onde o usuário pode fazer filtragem dos dados que deseja obter dos que estão salvos, tendo dois formatos.
    - Os que ele quer e os que ele não quer.
    - Caso não seja informado (duplex e escala de cinza seriam selecionar tudo) irá buscar todos os dados que possuem tal filtragem; caso informado, ele busca apenas os dados que possuem tal filtragem. Caso informado com um '-' SINAL DE MENOS/TRAÇO NO COMEÇO, remove o dado da pesquisa.
    - Os tipos de filtragem são:
        - Data: O usuário fornece as datas que deseja. Caso tenha o '-' SINAL DE MENOS/TRAÇO NO COMEÇO, a seguinte data não aparece nos dados obtidos ao apertar o botão Pesquisar. Também oferece a função de colocar ranges ou múltiplas datas, utilizando o '-' SINAL DE MENOS/TRAÇO NO MEIO de duas datas. Também podendo ignorar caso tenha o '-' SINAL DE MENOS/TRAÇO NO COMEÇO, exemplos > '01/01/0001-10/01/0001, 12/01/0001' devolve as seguintes datas: '03/01/0001, 07/01/0001, 08/01/0001, 05/01/0001, 02/01/0001, 12/01/0001, 04/01/0001, 10/01/0001, 06/01/0001, 09/01/0001, 01/01/0001'
          Outro exemplo usando a remoção: '01/01/0001-10/01/0001, -05/01/0001, -07/01/0001-09/01/0001' devolve '03/01/0001, 02/01/0001, 04/01/0001, 10/01/0001, 06/01/0001,01/01/0001, -07/01/0001, -08/01/0001, -05/01/0001, -09/01/0001'.
        - Usuário: Seguindo a mesma lógica, caso tenha o '-' SINAL DE MENOS/TRAÇO NO COMEÇO, ele não aparece, e caso tenha sem, aparece apenas estes. Caso não tenha nenhum, aparecem todos. Exemplos > Caso coloque 'Joao' É CASE SENSITIVE, aparece apenas dados do usuário Joao, caso coloque '-Joao' É CASE SENSITIVE, aparecem todos, menos os dados do usuário Joao.
        - Impressora: Igual o de usuário, porém com o campo Impressora.
        - Estação: Igual o de usuário, porém com o campo Estação.
        - Duplex e Escala de cinza: Você pode marcar uma caixa, onde caso queira os que tenham, marcar o Com; caso queira os não tenham, marcar os Sem. Exemplos:
          Com Duplex, Sem Duplex, Com Escala de Cinza, Sem Escala de Cinza todos selecionados pega todos.
          Com Duplex, Com Escala de Cinza, Sem Escala de Cinza selecionados, pega todos, menos aqueles que não foram utilizados a forma de impressão Duplex.

- A tela de **Relatórios** o usuário cria o estilo de PDF e salva-o do jeito que estiver, com as seguintes ferramentas.
    - No lado esquerdo há uma tela demonstrando os comandos que foram adicionados ao estilo de PDF, que gera um PDF.
    - Os seguintes botões >
        - Set Font > O usuário abre um Popup pedindo as seguintes informações: Family, Style e Size, que seriam as informações da fonte dos textos que estão abaixo deste comando.
        - Add Cell > O usuário abre um Popup pedindo as seguintes informações: Width, Height, Text, Border (0=Não, 1=Sim), Quebra de Linha (0=Não, 1=Sim) e Align, que seriam as informações para a criação de uma célula dentro do PDF.
        - Add Multicell > O usuário abre um Popup pedindo as seguintes informações: Width, Height, Text, Border (0=Não, 1=Sim) e Align, que seriam as informações para a criação de uma célula que ocupa diversas linhas caso ultrapasse o Width do PDF dentro do PDF.
        - Add código Python > Abre um Popup onde o usuário consegue escrever seu código python para a criação do PDF de forma DINÂMICA. As seguintes funções podem ser utilizadas pelo usuário:
            - As padrões:
                - conteudo é um dicionário onde a chave é o que ele quer pegar. O usuário consegue acessar os dados que foram obtidos na tela de Dados Salvos, que a chave seria 'lista', exemplo: conteudo['lista'] é uma lista de objetos Dados contendo os seguintes parâmetros: id, principal, data, hora, user, paginas, copias, impressora, arquivo, est, duplex, escala_de_cinza. Também pode escrever um código para colocar as informações em cells e multicells e também como acessar o conteudo['filtros'] pode ser encontrado ao utilizar o botão Pegar Estilo Padrão que se encontra na tela.
                - math biblioteca para fazer operações matemáticas.
                - datetime biblioteca para manipulação de datas.
                - pdf para manipulação do PDF.
                - set_font para setar fonte dos textos após este comando.
                - cell para adicionar uma cell no pdf.
                - multi_cell para adicionar multicell no pdf.
            - As funções customizadas (Pode ser encontrado como utilizar através do botão Pegar Estilo Padrão):
                - formatar_datas para pegar todas as datas que estão presentes nos dados obtidos.
                - truncate_text para adicionar '...' em uma parte do texto caso ele seja maior do que o estipulado.
                - calcular_periodo para receber três variáveis dentro de uma tupla, (primeira data, última data, dias entre elas).
                - pegar_totais para pegar duas variáveis dentro de uma tupla, (totais, total), o totais seria um dicionário onde a chave é o arquivo principal e os valores um dicionário onde a chave é o usuário e o valor o total de folhas, o total seria um dicionário onde a chave é o usuário e o valor o total de folhas.
                - formato_da_data para pegar o formato de data padrão.
        - Remover última adição > Remove a última adição no estilo de PDF.
        - Estilos de PDF Salvos > Abre um Popup contendo os nomes dos estilos de PDF salvos, podendo também pesquisar pelo nome ao escrever e clicar no botão Buscar estilo de PDF.
        - Pegar estilo padrão > Pega o estilo padrão de PDF, nele há vários códigos python para poder aprender como manipular as funções utilizáveis.
        - Salvar estilo de PDF > Abre um Popup onde é necessário informar um nome para salvar o estilo atual; caso esteja com o banco de dados desativado, ele salva no formato json; caso contrário, ele salva no banco de dados.
        - Gerar PDF > Gera um PDF baseado no estilo de PDF atual.

- A tela de **Configurações** é a tela onde o usuário altera partes do aplicativo.
    - Padrões e tipo do banco de dados, onde caso o tipo esteja desativado, a aplicação funciona através de salvamentos em JSON; caso contrário, funciona através de salvamentos no banco de dados.
    - Na parte superior encontram-se as traduções, que servem para casos de problemas de localização, não sendo recomendado alterar caso não seja necessário, contendo um botão para salvar a tradução e outro para ir para a tela Lista de Traduções.
    - Em seguida está o tipo

 do Banco de Dados, Ativado ou Desativado.
    - Em seguida o caminho padrão dos logs que fica como padrão ao entrar na tela de Resultados.
    - Por fim, um botão que encaminha o usuário para a tela Alterar Documentos.

- A tela **Lista de Traduções** lista todas as traduções da aplicação.
    - Onde traduz do primeiro para o segundo, podendo remover, e para salvar é necessário apertar no botão Aplicar; caso contrário, não é efetuada a ação de remoção.
    - **Cuidado: a ação de remoção não é possível ser revertida!**

- A tela de **Alterar Documentos** lista todos os htmls e csvs que foram salvos.
    - Pode-se apertar no botão Remover Documento.
    - Escrever o nome e apertar em Remover.
        - Os botões abrem um Popup demonstrando todos os dados que serão removidos do Banco de Dados.
    - **Aviso: Esta ação não é possível em casos de salvamentos do tipo JSON(Banco de Dados desativado). Cuidado: a ação de remoção não é possível ser revertida!**
