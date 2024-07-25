class Dados:
    # Arquivo Principal, Data, Horário, Usuário, Páginas, Cópias, Impressora, Arquivo, Tipo,
    # Tamanho,Tipo de Impressão,Estação,Duplex,Escala de Cinza.
    def __init__(self, principal, data, hora, user, paginas, copias, impressora, arquivo, est, duplex, escala_de_cinza):
        self.principal = principal
        self.data = data
        self.hora = hora
        self.user = user
        self.paginas = paginas
        self.copias = copias
        self.impressora = impressora
        self.arquivo = arquivo
        self.est = est
        self.duplex = duplex
        self.escala_de_cinza = escala_de_cinza

    def __repr__(self):
        return str(self.__dict__)

    def get_dictionary(self):
        return self.__dict__
