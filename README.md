# Visualiza��o e Manipula��o de Logs de Impressoras

Este projeto � uma aplica��o desenvolvida em Python para a visualiza��o e manipula��o de logs de impressoras. Ele
permite a leitura de arquivos de log, a cria��o de documentos PDF e o salvamento dos dados em formato JSON ou em um
banco de dados.

## Funcionalidades

- **Tela Principal**: In�cio da aplica��o com tr�s bot�es:
    - **Ler os Dados das Impress�es**: Acessa a tela de Resultados.
    - **Dados Salvos**: Acessa a tela de Dados Salvos.
    - **Configura��es**: Acessa a tela de Configura��es.

- **Tela de Resultados**:
    - Permite a leitura de arquivos `.html` e `.csv` com dados de impress�o.
    - **HTML**: Espera-se que no t�tulo tenha a data no formato `%d %B %Y`, e uma as tabela com colunas: Hora, Usu�rio,
      P�ginas, C�pias, Fila de Impress�o, Documento, Esta��o, Duplex, e Escala de Cinza.
    - **CSV**: A primeira linha � informa��o extra, a segunda linha tem o cabe�alho no formato: Time, User, Pages,
      Copies, Printer, Document Name, Client, Paper Size, Language, Height, Width, Duplex, Grayscale, Size.
    - Oferece op��es para salvar os resultados em JSON, CSVs compactos ou em um banco de dados.

- **Tela Dados Salvos**:
    - Permite pesquisar dados salvos.
    - Bot�es:
        - **Pesquisar**: Pesquisa em JSON ou banco de dados, dependendo da configura��o.
        - **Filtros**: Acessa a tela de Filtros.
        - **Criar Relat�rio em PDF**: Acessa a tela de Relat�rios, caso haja dados obtidos pelo bot�o Pesquisar.

- **Tela Filtros**:
    - Filtragem dos dados salvos:
        - **Data**: Permite filtrar por datas espec�ficas, ranges ou m�ltiplas datas.
        - **Usu�rio**: Filtra dados por usu�rio espec�fico ou exclui dados de usu�rios.
        - **Impressora**: Filtra dados por impressora.
        - **Esta��o**: Filtra dados por esta��o.
        - **Duplex e Escala de Cinza**: Filtra por caracter�sticas de impress�o, como duplex e escala de cinza.

- **Tela Relat�rios**:
    - Cria��o de relat�rios em PDF com op��es de personaliza��o:
        - **Set Font**: Define a fonte dos textos.
        - **Add Cell**: Adiciona c�lulas ao PDF.
        - **Add Multicell**: Adiciona c�lulas que ocupam v�rias linhas.
        - **Add C�digo Python**: Adiciona c�digo Python para criar PDFs dinamicamente.
        - **Remover �ltima Adi��o**: Remove a �ltima adi��o no estilo de PDF.
        - **Estilos de PDF Salvos**: Gerencia estilos de PDF salvos.
        - **Pegar Estilo Padr�o**: Obt�m o estilo padr�o de PDF.
        - **Salvar Estilo de PDF**: Salva o estilo de PDF atual.
        - **Gerar PDF**: Gera um PDF baseado no estilo atual.

## Instala��o

1. Clone o reposit�rio:
   ```bash
   git clone https://github.com/NoPsNick/PrintersLog.git
   cd repo

2. Crie um ambiente virtual (opcional, mas RECOMENDADO):
   ```bash 
    python -m venv env
    source env/bin/activate  # No Windows: env\Scripts\activate

3. Instale as depend�ncias:
    ```bash 
    pip install -r requirements.txt

## Uso

1. Execute a aplica��o:
    ```bash 
    python PrintersLogs.py

2. Navegue pelas diferentes telas da aplica��o usando a interface gr�fica.

## Estrutura dos Arquivos

- Principal: Tela inicial com bot�es para acessar outras partes da aplica��o.
- Resultados: Tela para carregar e processar arquivos de log.
- Dados Salvos: Tela para pesquisar e visualizar dados salvos.
- Filtros: Tela para aplicar filtros aos dados salvos.
- Relat�rios: Tela para criar e personalizar relat�rios em PDF.
- Configura��es: Tela para ajustar configura��es da aplica��o.
- Lista de Tradu��es: Tela para gerenciar tradu��es.
- Alterar Documentos: Tela para remover documentos lidos.

## Depend�ncias

- kivy: Para a interface gr�fica.
- fpdf: Para manipula��o de PDFs.
- json: Para salvar e carregar dados em formato JSON.
- SQLAlchemy: Para armazenamento dos dados.
- pandas: Para visualiza��o/manipula��o dos dados.
- python-dateutil: Para documenta��o.
- numpy: Para opera��es matem�ticas complexas.

## Contribui��o

Contribui��es s�o bem-vindas! Sinta-se � vontade para abrir issues e pull requests.

## Licen�a

Este projeto est� licenciado sob a [MIT License](LICENSE).

## Contato

Para mais informa��es, entre em contato
com [serafim999junior@hotmail.com](mailto:serafim999junior@hotmail.com?subject=Contato%20do%20GitHub)

# Texto mais explicativo

- A tela **Principal**, � o in�cio da aplica��o, onde h� tr�s bot�es.
    - Ler os Dados das Impress�es que o usu�rio iria para a tela de Resultados.
    - Dados Salvos que o usu�rio iria para a tela de Dados Salvos.
    - Configura��es que o usu�rio iria para a tela de Configura��o da aplica��o.

- A tela de **Resultados** seria onde o usu�rio conseguiria colocar o diret�rio de todos os arquivos .html e .csv para
  leitura.
    - O html precisa ter no come�o a data dentro do t�tulo do html no formato '%d %B %Y' e tabelas com as colunas sendo:
      Hora, Usu�rio, Paginas, C�pias, Fila de Impress�o, Documento, Esta��o, Duplex e Escala de cinza.
    - O formato do csv: a primeira linha ser� informa��o extra, a segunda o cabe�alho no seguinte formato: Time, User,
      Pages, Copies, Printer, Document Name, Client, Paper Size, Language, Height, Width, Duplex, Grayscale, Size.
    - Ap�s pressionar o bot�o Results, ele ir� ler todos os arquivos html e csv que tenham a estrutura��o correta e ir�o
      aparecer 3 bot�es.
        - Salvar em JSON que ir� salvar o resultado obtido em formato JSON.
        - Criar CSVs que ir� salvar os resultado em arquivos csvs compactos.
        - Salvar no Banco de Dados que caso esteja ativo, ir� salvar os resultados no banco de dados.

- A tela **Dados Salvos** o usu�rio iria conseguir fazer a pesquisa de todos os dados salvos, contendo 3 bot�es.
    - Pesquisar que caso o banco de dados esteja desativo nas configura��es, ir� fazer a busca no formato JSON, caso
      esteja ativo, ir� fazer a busca no banco de dados.
    - Filtros que o usu�rio vai para a tela Filtros.
    - Criar Relat�rio em PDF que o usu�rio vai para a tela de Relat�rios, caso tenha alguma dado obtido pelo bot�o de
      Pesquisar.

- A tela **Filtros** � onde o usu�rio poder� fazer filtragem dos dados que ele deseja obter dos que est�o salvos, tendo
  dois formatos.
    - Os que ele quer e os que ele n�o quer.
    - Caso n�o seja informado(duplex e escala de cinza seria selecionar tudo) ir� buscar todos os dados que possuem tal
      filtragem, caso informado ele ir� buscar apenas os dados que possuem tal filtragem, caso informado com um '-'
      SINAL DE MENOS/TRA�O NO COME�O, ir� remover o dado da pesquisa.
    - Os tipos de filtragem s�o:
        - Data: O usu�rio ir� fornecer as datas que ele desejar, caso tenha o '-' SINAL DE MENOS/TRA�O NO COME�O a
          seguinte data n�o ir� aparecer nos dados obtidos ao apertar o bot�o Pesquisar. Tamb�m oferece a fun��o de
          colocar ranges ou m�ltiplas datas, utilizando o '-' SINAL DE MENOS/TRA�O NO MEIO de duas datas, tamb�m podendo
          ignorar caso tenha o '-' SINAL DE MENOS/TRA�O NO COME�O, exemplos > '01/01/0001-10/01/0001, 12/01/0001' ir�
          devolver as seguintes datas: '03/01/0001, 07/01/0001, 08/01/0001, 05/01/0001, 02/01/0001, 12/01/0001,
          04/01/0001, 10/01/0001, 06/01/0001, 09/01/0001, 01/01/0001'
          Outro exemplo usando a remo��o: '01/01/0001-10/01/0001, -05/01/0001, -07/01/0001-09/01/0001' ir� devolver '
          03/01/0001, 02/01/0001, 04/01/0001, 10/01/0001, 06/01/0001,01/01/0001, -07/01/0001, -08/01/0001, -05/01/0001,
          -09/01/0001'.
        - Usu�rio: Seguindo a mesma l�gica, caso tenha o '-' SINAL DE MENOS/TRA�O NO COME�O, ele n�o ir� aparecer, e
          caso tenha sem, ir� aparecer apenas estes. Caso n�o tenha nenhum, ir� aparecer todos. Exemplos > Caso
          coloque 'Joao' � CASE SENSITIVE, ir� aparecer apenas dados do usu�rio Joao, caso coloque '-Joao' � CASE
          SENSITIVE, ir� aparecer todos, menos os dados do usu�rio Joao.
        - Impressora: Igual o de usu�rio, por�m com o campo Impressora.
        - Esta��o: Igual o de usu�rio, por�m com o campo Esta��o.
        - Duplex e Escala de cinza: Voc� pode marcar uma caixa, onde caso queira os que tenham, marcar o Com, caso
          queira os n�o tenham marcar os Sem, exemplos:
          Com Duplex, Sem Duplex, Com Escala de Cinza, Sem Escala de Cinza todos selecionados ir� pegar todos.
          Com Duplex, Com Escala de Cinza, Sem Escala de Cinza selecionados, ir� pegar todos, menos aqueles que n�o
          foram utilizados a forma de impress�o Duplex.

- A tela de **Relat�rios** o usu�rio conseguir� criar o estilo de PDF e salv�-lo do jeito que estiver, com as seguintes
  ferramentas.
    - No lado esquerdo ter� uma tela demonstrando os comandos que foram adicionados ao estilo de PDF, que ir� gerar um
      PDF.
    - Os seguintes bot�es >
        - Set Font > O usu�rio ir� abrir um Popup pedindo as seguintes informa��es: Family, Style e Size, que seria as
          informa��es da fonte dos textos que est�o abaixo deste comando.
        - Add Cell > O usu�rio ir� abrir um Popup pedindo as seguintes informa��es: Width, Height, Text, Border(0=N�o,
          1=Sim), Quebra de Linha(0=N�o, 1=Sim) e Align, que seria as informa��es para a cria��o de uma c�lula dentro do
          PDF.
        - Add Multicell > O usu�rio ir� abrir um Popup pedindo as seguintes informa��es: Width, Height, Text, Border(
          0=N�o, 1=Sim) e Align, que seria as informa��es para a cria��o de uma c�lula que ocupa diversas linhas caso
          ultrapasse o Width do PDF dentro do PDF.
        - Add c�digo Python > Ir� abrir um Popup onde o usu�rio conseguir� escrever seu c�digo python para a cria��o do
          PDF de forma DIN�MICA. As seguintes fun��es podem ser utilizadas pelo usu�rio:
            - As padr�es:
                - conteudo um dicion�rio onde a chave � o que ele quer pegar, o usu�rio consegue acessar os dados que
                  foram obtidos na tela de Dados Salvos, que a chave seria 'lista', exemplo: conteudo['lista'] seria uma
                  lista de objetos Dados contendo os seguintes par�metros: id, principal, data, hora, user, paginas,
                  copias, impressora, arquivo, est, duplex, escala_de_cinza, jeito de escrever um c�digo para colocar as
                  informa��es em cells e multicells e tamb�m como acessar o conteudo['filtros'] pode ser encontrado ao
                  utilizar o bot�o Pegar Estilo Padr�o que se encontra na tela.
                - math biblioteca para fazer opera��es matem�ticas.
                - datetime biblioteca para manipula��o de datas.
                - pdf para manipula��o do PDF.
                - set_font para setar fonte dos textos ap�s este comando.
                - cell para adicionar uma cell no pdf.
                - multi_cell para adicionar multicell no pdf.
            - As fun��es customizadas(Pode ser encontrado como utilizar atrav�s do bot�o Pegar Estilo Padr�o):
                - formatar_datas para pegar todas as datas que est�o presentes nos dados obtidos.
                - truncate_text para adicionar '...' em uma parte do texto caso ele seja maior do que o estipulado.
                - calcular_periodo para receber tr�s vari�veis dentro de uma tupla, (primeira data, �ltima data, dias
                  entre elas).
                - pegar_totais para pegar duas vari�veis dentro de uma tupla, (totais, total), o totais seria um
                  dicion�rio onde a chave � o arquivo principal e os valores um dicion�rio onde a chave � o usu�rio e o
                  valor o total de folhas, o total seria um dicion�rio onde a chave � o usu�rio e o valor o total de
                  folhas.
                - formato_da_data para pegar o formato de data padr�o.
        - Remover �ltima adi��o > Remove a �ltima adi��o no estilo de PDF.
        - Estilos de PDF Salvos > Abre um Popup contendo os nomes dos estilos de PDF salvos, podendo tamb�m pesquisar
          pelo nome ao escrever e clicar no bot�o Buscar estilo de PDF.
        - Pegar estilo padr�o > Pega o estilo padr�o de PDF, nele h� v�rios c�digos python para poder aprender como
          manipular as fun��es utiliz�veis.
        - Salvar estilo de PDF > Abre um Popup onde � necess�rio informar um nome para salvar o estilo atual, caso
          esteja com o banco de dados desativado, ele ir� salvar no formato json, caso contr�rio ele ir� salvar no banco
          de dados.
        - Gerar PDF > Gera um PDF baseado no estilo de PDF atual.

- A tela de **Configura��es** � a tela onde o usu�rio consegue alterar partes do aplicativo.
    - Padr�es e tipo do banco de dados, onde caso o tipo esteja desativado, a aplica��o ir� funcionar atrav�s de
      salvamentos em JSON, caso contr�rio, ir� funcionar atrav�s de salvamentos no banco de dados.
    - Na parte superior encontra-se as tradu��es, que serve para casos de problemas de localiza��o, n�o sendo
      recomendado alterar caso n�o seja necess�rio, contendo um bot�o para salvar a tradu��o e outro para ir para a tela
      Lista de Tradu��es.
    - Em seguida est� o tipo do Banco de Dados, Ativado ou Desativado.
    - Em seguida o caminho padr�o dos logs que ficar� como padr�o ao entrar na tela de Resultados.
    - Por fim um bot�o que ir� encaminhar o usu�rio para a tela Alterar Documentos.

- A tela **Lista de Tradu��es** ir� listar todas as tradu��es da aplica��o.
    - Onde ir� traduzir do primeiro para o segundo, podendo remover, e para salvar � necess�rio apertar no bot�o
      Aplicar, caso contr�rio, n�o ser� efetuado a a��o de remo��o.
    - **Cuidado: a a��o de remo��o n�o � poss�vel ser revertida!**

- A tela de **Alterar Documentos** � onde ir� listar todos os htmls e csvs que foram salvos.
    - Pode-se apertar no bot�o Remover Documento
    - Escrever o nome e apertar em Remover.
        - Os bot�es ir�o abrir um Popup demonstrando todos os dados que ser�o removidos do Banco de Dados.
    - **Aviso: Esta a��o n�o � plaus�vel em caso de salvamentos em JSON. Cuidado: a a��o de remo��o n�o � poss�vel ser
      revertida!**