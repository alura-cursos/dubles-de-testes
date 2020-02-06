from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode
import logging
import os
import json
from math import ceil


def consultar_livros(autor):
    dados = preparar_dados_para_requisicao(autor)
    url = obter_url("https://buscador", dados)
    ret = executar_requisicao(url)
    return ret


def preparar_dados_para_requisicao(autor):
    pass


def obter_url(url, dados):
    pass


def executar_requisicao(url):
    try:
        with urlopen(url, timeout=10) as resposta:
            resultado = resposta.read().decode("utf-8")
    except HTTPError as e:
        logging.exception("Ao acessar '%s': %s" % (url, e))
    else:
        return resultado


def escrever_em_arquivo(arquivo, conteudo):
    diretorio = os.path.dirname(arquivo)
    try:
        os.makedirs(diretorio)
    except OSError as e:
        logging.exception("Não foi possível criar diretório %s" % diretorio)

    try:
        with open(arquivo, "w") as fp:
            fp.write(conteudo)
    except OSError as e:
        logging.exception("Não foi possível criar arquivo %s" % arquivo)


class Consulta:
    """
    Classe Consulta
    Armazena os dados da expressao de busca: 
    - autor, titulo e livre
    - pagina
    - url
    - dados_para_requisicao
    """

    def __init__(self, autor=None, titulo=None, livre=None):
        self._autor = autor
        self._titulo = titulo
        self._livre = livre
        self._pagina = 0
        self._dados_para_requisicao = None
        self._url = "https://buscarlivros"

    @property
    def pagina(self):
        return self._pagina

    @property
    def dados_para_requisicao(self):
        """
        Retorna um dicionário com os dados de Consulta
        """
        if not self._dados_para_requisicao:
            self._dados_para_requisicao = {}
            if self._livre:
                self._dados_para_requisicao = {"q": self._livre}
            else:
                if self._autor:
                    self._dados_para_requisicao["author"] = self._autor
                if self._titulo:
                    self._dados_para_requisicao["title"] = self._titulo
        return self._dados_para_requisicao

    @property
    def seguinte(self):
        dados_para_requisicao = self.dados_para_requisicao
        self._pagina += 1
        dados_para_requisicao["page"] = self._pagina
        req = Request(self._url, dados_para_requisicao)
        if req.data:
            return req.full_url + "?" + urlencode(req.data)


class Resposta:
    """
    Conteúdo da página em formato JSON 
    """

    # quantidade de documentos max esperado por página
    qtd_docs_por_pagina = 50

    def __init__(self, conteudo):
        # conteudo da pagina pura
        self._conteudo = conteudo
        # conteudo processado, formato dicionário
        self._dados = None

    @property
    def conteudo(self):
        return self._conteudo

    @property
    def dados(self):
        if not self._dados:
            try:
                j = json.loads(self.conteudo)
            except TypeError as e:
                logging.exception(
                    "Resultado da consulta '%s': tipo inválido. " % self.conteudo
                )
            except json.JSONDecodeError as e:
                logging.exception(
                    "Resultado da consulta '%s': JSON inválido. " % self.conteudo
                )
            else:
                self._dados = j
        return self._dados

    @property
    def documentos(self):
        # documentos retornados na pagina
        return self.dados.get("docs", [])

    @property
    def total_de_paginas(self):
        # total de paginas, todos os resultados
        if len(self.documentos):
            return ceil(self.dados.get("num_docs", 0) / self.qtd_docs_por_pagina)
        return 0


def baixar_livros(arquivo, autor=None, titulo=None, livre=None):
    consulta = Consulta(autor, titulo, livre)
    total_de_paginas = 1
    i = 0
    while True:
        resultado = executar_requisicao(consulta.seguinte)
        if resultado:
            resposta = Resposta(resultado)
            total_de_paginas = resposta.total_de_paginas
            escrever_em_arquivo(arquivo[i], resultado)
        elif consulta.pagina == 1:
            total_de_paginas = 2
        if consulta.pagina == total_de_paginas:
            break
        i += 1


def ler_arquivo(nome):
    return ""


def registrar_livros(arquivos, inserir_registros):
    qtd = 0
    for arq in arquivos:
        conteudo = ler_arquivo(arq)
        resposta = Resposta(conteudo)
        qtd += inserir_registros(resposta.documentos)
    return qtd
