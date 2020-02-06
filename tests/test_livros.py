import pytest
from unittest.mock import (
    patch,
    mock_open,
    Mock,
    MagicMock,
    call,
)

from unittest import skip
from colecao.livros import (
    consultar_livros,
    executar_requisicao,
    escrever_em_arquivo,
    Consulta,
    baixar_livros,
    Resposta,
    registrar_livros,
)
from urllib.error import HTTPError


class StubHTTPResponse:
    def read(self):
        return b""

    def __enter__(self):
        return self

    def __exit__(self, param1, param2, param3):
        pass


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_consultar_livros_retorna_resultado_formato_string(stub_urlopen):
    resultado = consultar_livros("Agatha Christie")
    assert type(resultado) == str


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_consultar_livros_chama_preparar_dados_para_requisicao_uma_vez_e_com_os_mesmos_parametros_de_consultar_livros(
    stub_urlopen,
):
    with patch("colecao.livros.preparar_dados_para_requisicao") as spy_preparar_dados:
        consultar_livros("Agatha Christie")
        spy_preparar_dados.assert_called_once_with("Agatha Christie")


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_consultar_livros_chama_obter_url_usando_como_parametro_o_retorno_de_preparar_dados_para_requisicao(
    stub_urlopen,
):
    with patch("colecao.livros.preparar_dados_para_requisicao") as stub_preparar:
        dados = {"author": "Agatha Christie"}
        stub_preparar.return_value = dados
        with patch("colecao.livros.obter_url") as spy_obter_url:
            consultar_livros("Agatha Christie")
            spy_obter_url.assert_called_once_with("https://buscador", dados)


@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_consultar_livros_chama_executar_requisicao_usando_retorno_obter_url(
    stub_urlopen,
):
    with patch("colecao.livros.obter_url") as stub_obter_url:
        stub_obter_url.return_value = "https://buscador"
        with patch("colecao.livros.executar_requisicao") as spy_executar_requisicao:
            consultar_livros("Agatha Christie")
            spy_executar_requisicao.assert_called_once_with("https://buscador")


def stub_de_urlopen(url, timeout):
    return StubHTTPResponse()


def test_executar_requisicao_retorna_tipo_string():
    with patch("colecao.livros.urlopen", stub_de_urlopen):
        print(stub_de_urlopen)
        resultado = executar_requisicao("https://buscarlivros?author=Jk+Rowlings")
        assert type(resultado) == str


"""
def test_executar_requisicao_retorna_resultado_tipo_str():
    with patch("colecao.livros.urlopen") as duble_de_urlopen:
        print(duble_de_urlopen)
        duble_de_urlopen.return_value = StubHTTPResponse()
        resultado = executar_requisicao("https://buscarlivros?author=Jk+Rowlings")
        assert type(resultado) == str


            
def test_executar_requisicao_retorna_resultado_tipo_str():
    with patch("colecao.livros.urlopen", return_value=StubHTTPResponse()):
        resultado = executar_requisicao("https://buscarlivros?author=Jk+Rowlings")
        assert type(resultado) == str
    

@patch("colecao.livros.urlopen", return_value=StubHTTPResponse())
def test_executar_requisicao_retorna_resultado_tipo_str(duble_de_urlopen):
    resultado = executar_requisicao("https://buscarlivros?author=Jk+Rowlings")
    assert type(resultado) == str

"""


@patch("colecao.livros.urlopen")
def test_executar_requisicao_retorna_resultado_tipo_str(duble_de_urlopen):
    duble_de_urlopen.return_value = StubHTTPResponse()
    resultado = executar_requisicao("https://buscarlivros?author=Jk+Rowlings")
    assert type(resultado) == str


class Dummy:
    pass


def stub_de_urlopen_que_levanta_excecao_http_error(url, timeout):
    fp = mock_open
    fp.close = Dummy
    raise HTTPError(Dummy(), Dummy(), "mensagem de erro", Dummy(), fp)


"""
def test_executar_requisicao_loga_mensagem_de_erro_de_http_error(caplog):
    with patch("colecao.livros.urlopen", stub_de_urlopen_que_levanta_excecao_http_error):
        resultado = executar_requisicao("http://")
        mensagem_de_erro = "mensagem de erro"
        assert len(caplog.records) == 1
        for registro in caplog.records:
            assert mensagem_de_erro in registro.message
        

def test_executar_requisicao_levanta_excecao_do_tipo_http_error():
    with patch("colecao.livros.urlopen", duble_de_urlopen_que_levanta_excecao_http_error):
        with pytest.raises(HTTPError) as excecao:
            executar_requisicao("http://")
        assert "mensagem de erro" in str(excecao.value)
            
        

@patch("colecao.livros.urlopen")
def test_executar_requisicao_levanta_excecao_do_tipo_http_error(duble_de_urlopen):
    fp = mock_open
    fp.close = Mock()
    duble_de_urlopen.side_effect = HTTPError(Mock(), Mock(), "mensagem de erro", Mock(), fp)
    with pytest.raises(HTTPError) as excecao:
        executar_requisicao("http://")
        assert "mensagem de erro" in str(excecao.value)
"""


@patch("colecao.livros.urlopen")
def test_executar_requisicao_loga_mensagem_de_erro_de_http_error(stub_urlopen, caplog):
    fp = mock_open
    fp.close = Mock()
    stub_urlopen.side_effect = HTTPError(Mock(), Mock(), "mensagem de erro", Mock(), fp)
    executar_requisicao("http://")
    assert len(caplog.records) == 1
    for registro in caplog.records:
        assert "mensagem de erro" in registro.message


class DubleLogging:
    def __init__(self):
        self._mensagens = []

    @property
    def mensagens(self):
        return self._mensagens

    def exception(self, mensagem):
        self._mensagens.append(mensagem)


def duble_makedirs(diretorio):
    raise OSError("Não foi possível criar diretório %s" % diretorio)


def test_escrever_em_arquivo_registra_excecao_que_nao_foi_possivel_criar_diretorio():
    arquivo = "/tmp/arquivo.json"
    conteudo = "dados de livros"
    duble_logging = DubleLogging()
    with patch("colecao.livros.os.makedirs", duble_makedirs):
        with patch("colecao.livros.logging", duble_logging):
            escrever_em_arquivo(arquivo, conteudo)
            assert "Não foi possível criar diretório /tmp" in duble_logging.mensagens


@patch("colecao.livros.os.makedirs")
@patch("colecao.livros.logging.exception")
@patch("colecao.livros.open", side_effect=OSError())
def test_escrever_em_arquivo_registra_erro_ao_criar_o_arquivo(
    stub_open, spy_exception, stub_makedirs
):
    arq = "/bla/arquivo.json"
    escrever_em_arquivo(arq, "dados de livros")
    spy_exception.assert_called_once_with("Não foi possível criar arquivo %s" % arq)


class SpyFp:
    def __init__(self):
        self._conteudo = None

    def __enter__(self):
        return self

    def __exit__(self, param1, param2, param3):
        pass

    def write(self, conteudo):
        self._conteudo = conteudo


@skip
@patch("colecao.livros.open")
def test_escrever_em_arquivo_chama_write(stub_de_open):
    arq = "/tmp/arquivo"
    conteudo = "conteudo do arquivo"
    spy_de_fp = SpyFp()
    stub_de_open.return_value = spy_de_fp

    escrever_em_arquivo(arq, conteudo)
    assert spy_de_fp._conteudo == conteudo


@patch("colecao.livros.open")
def test_escrever_em_arquivo_chama_write(stub_de_open):
    arq = "/tmp/arquivo"
    conteudo = "conteudo do arquivo"
    spy_de_fp = MagicMock()
    spy_de_fp.__enter__.return_value = spy_de_fp
    spy_de_fp.__exit__.return_value = None
    stub_de_open.return_value = spy_de_fp

    escrever_em_arquivo(arq, conteudo)
    spy_de_fp.write.assert_called_once_with(conteudo)


@pytest.fixture
def resultado_em_duas_paginas():
    return [
        """
        {
            "num_docs": 5,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 5,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                 {"author": "Wes McKinney",
                 "title": "Python Para Análise de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def resultado_em_tres_paginas():
    return [
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                 {"author": "Wes McKinney",
                 "title": "Python Para Análise de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def conteudo_de_4_arquivos():
    return [
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]

        }
        """,
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 17,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                 {"author": "Wes McKinney",
                 "title": "Python Para Análise de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def resultado_em_tres_paginas_erro_na_pagina_2():
    return [
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        None,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                 {"author": "Wes McKinney",
                 "title": "Python Para Análise de Dados"
                }
            ]
        }
        """,
    ]


@pytest.fixture
def resultado_em_tres_paginas_erro_na_pagina_1():
    return [
        None,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Luciano Ramalho",
                 "title": "Python Fluente"
                },
                {"author": "Nilo Ney",
                 "title": "Introdução a Programação com Python"
                },
                 {"author": "Allen B. Downey",
                 "title": "Pense em Python"
                }
            ]
        }
        """,
        """
        {
            "num_docs": 8,
            "docs": [
                {"author": "Kenneth Reitz",
                 "title": "O Guia do Mochileiro Python"
                },
                 {"author": "Wes McKinney",
                 "title": "Python Para Análise de Dados"
                }
            ]
        }
        """,
    ]


class MockConsulta:
    def __init__(self):
        self.chamadas = []
        self.consultas = []

    def Consulta(self, autor=None, titulo=None, livre=None):
        consulta = Consulta(autor, titulo, livre)
        self.chamadas.append((autor, titulo, livre))
        self.consultas.append(consulta)
        return consulta

    def verificar(self):
        assert len(self.consultas) == 1
        assert self.chamadas == [(None, None, "Python")]


@patch("colecao.livros.executar_requisicao")
def test_baixar_livros_instancia_Consulta_uma_vez(
    stub_executar_requisicao, resultado_em_duas_paginas
):
    mock_consulta = MockConsulta()
    stub_executar_requisicao.side_effect = resultado_em_duas_paginas
    Resposta.qtd_docs_por_pagina = 3
    arquivo = ["/tmp/arquivo1", "/tmp/arquivo2", "/tmp/arquivo3"]
    with patch("colecao.livros.Consulta", mock_consulta.Consulta):
        baixar_livros(arquivo, None, None, "Python")
        mock_consulta.verificar()


@patch("colecao.livros.executar_requisicao")
def test_baixar_livros_chama_executar_requisicao_n_vezes(
    mock_executar_requisicao, resultado_em_duas_paginas
):
    mock_executar_requisicao.side_effect = resultado_em_duas_paginas
    Resposta.qtd_docs_por_pagina = 3
    arquivo = ["/tmp/arquivo1", "/tmp/arquivo2", "/tmp/arquivo3"]
    baixar_livros(arquivo, None, None, "python")
    assert mock_executar_requisicao.call_args_list == [
        call("https://buscarlivros?q=python&page=1"),
        call("https://buscarlivros?q=python&page=2"),
    ]


@patch("colecao.livros.executar_requisicao")
def test_baixar_livros_instancia_Resposta_tres_vezes(
    stub_executar_requisicao, resultado_em_tres_paginas
):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas
    Resposta.qtd_docs_por_pagina = 3
    arquivo = ["/tmp/arquivo1", "/tmp/arquivo2", "/tmp/arquivo3"]
    with patch("colecao.livros.Resposta") as MockResposta:
        MockResposta.side_effect = [
            Resposta(resultado_em_tres_paginas[0]),
            Resposta(resultado_em_tres_paginas[1]),
            Resposta(resultado_em_tres_paginas[2]),
        ]
        baixar_livros(arquivo, None, None, "python")
        assert MockResposta.call_args_list == [
            call(resultado_em_tres_paginas[0]),
            call(resultado_em_tres_paginas[1]),
            call(resultado_em_tres_paginas[2]),
        ]


@patch("colecao.livros.executar_requisicao")
def test_baixar_livros_chama_escrever_em_arquivo_tres_vezes(
    stub_executar_requisicao, resultado_em_tres_paginas
):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas
    Resposta.qtd_docs_por_pagina = 3
    arquivo = ["/tmp/arquivo1", "/tmp/arquivo2", "/tmp/arquivo3"]
    with patch("colecao.livros.escrever_em_arquivo") as mock_escrever:
        mock_escrever.return_value = None
        baixar_livros(arquivo, None, None, "python")
        assert mock_escrever.call_args_list == [
            call(arquivo[0], resultado_em_tres_paginas[0]),
            call(arquivo[1], resultado_em_tres_paginas[1]),
            call(arquivo[2], resultado_em_tres_paginas[2]),
        ]


@patch("colecao.livros.executar_requisicao")
def test_baixar_livros_chama_escrever_em_arquivo_para_pagina_1_e_3(
    stub_executar_requisicao, resultado_em_tres_paginas_erro_na_pagina_2
):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas_erro_na_pagina_2
    Resposta.qtd_docs_por_pagina = 3
    arquivo = ["/tmp/arquivo1", "/tmp/arquivo2", "/tmp/arquivo3"]
    with patch("colecao.livros.escrever_em_arquivo") as mock_escrever:
        mock_escrever.side_effect = [None, None]
        baixar_livros(arquivo, None, None, "python")
        assert mock_escrever.call_args_list == [
            call(arquivo[0], resultado_em_tres_paginas_erro_na_pagina_2[0]),
            call(arquivo[2], resultado_em_tres_paginas_erro_na_pagina_2[2]),
        ]


@patch("colecao.livros.executar_requisicao")
def test_baixar_livros_chama_escrever_em_arquivo_para_pagina_2_e_3(
    stub_executar_requisicao, resultado_em_tres_paginas_erro_na_pagina_1
):
    stub_executar_requisicao.side_effect = resultado_em_tres_paginas_erro_na_pagina_1
    Resposta.qtd_docs_por_pagina = 3
    arquivo = ["/tmp/arquivo1", "/tmp/arquivo2", "/tmp/arquivo3"]
    with patch("colecao.livros.escrever_em_arquivo") as mock_escrever:
        mock_escrever.side_effect = [None, None]
        baixar_livros(arquivo, None, None, "python")
        assert mock_escrever.call_args_list == [
            call(arquivo[1], resultado_em_tres_paginas_erro_na_pagina_1[1]),
            call(arquivo[2], resultado_em_tres_paginas_erro_na_pagina_1[2]),
        ]


def fake_inserir_registros(dados):
    return len(dados)


def test_registrar_livros_chama_ler_arquivo_3_vezes(resultado_em_tres_paginas):
    arquivos = [
        "/tmp/arq1",
        "/tmp/arq2",
        "/tmp/arq3",
    ]
    with patch("colecao.livros.ler_arquivo") as mock_ler_arquivo:
        mock_ler_arquivo.side_effect = resultado_em_tres_paginas
        registrar_livros(arquivos, fake_inserir_registros)
        assert mock_ler_arquivo.call_args_list == [
            call(arquivos[0]),
            call(arquivos[1]),
            call(arquivos[2]),
        ]


@patch("colecao.livros.ler_arquivo")
def test_registrar_livros_instancia_Resposta_4_vezes(
    stub_ler_arquivo, conteudo_de_4_arquivos
):
    stub_ler_arquivo.side_effect = conteudo_de_4_arquivos
    arquivos = [
        "/tmp/arquivos1",
        "/tmp/arquivos2",
        "/tmp/arquivos3",
        "/tmp/arquivos4",
    ]
    with patch("colecao.livros.Resposta") as MockResposta:
        MockResposta.side_effect = [
            Resposta(conteudo_de_4_arquivos[0]),
            Resposta(conteudo_de_4_arquivos[1]),
            Resposta(conteudo_de_4_arquivos[2]),
            Resposta(conteudo_de_4_arquivos[3]),
        ]
        registrar_livros(arquivos, fake_inserir_registros)
        assert MockResposta.call_args_list == [
            call(conteudo_de_4_arquivos[0]),
            call(conteudo_de_4_arquivos[1]),
            call(conteudo_de_4_arquivos[2]),
            call(conteudo_de_4_arquivos[3]),
        ]


@patch("colecao.livros.ler_arquivo")
def test_registrar_livros_chama_inserir_registros(
    stub_ler_arquivo, conteudo_de_4_arquivos
):
    arquivos = [
        "/tmp/arquivos1",
        "/tmp/arquivos2",
        "/tmp/arquivos3",
    ]
    conteudo_de_3_arquivos = conteudo_de_4_arquivos[1:]
    stub_ler_arquivo.side_effect = conteudo_de_3_arquivos

    qtd = registrar_livros(arquivos, fake_inserir_registros)
    assert qtd == 12


class FakeDB:
    def __init__(self):
        self._registros = []

    def inserir_registros(self, dados):
        self._registros.extend(dados)
        return len(dados)


@patch("colecao.livros.ler_arquivo")
def test_registrar_livros_insere_12_registros_na_base_de_dados(
    stub_ler_arquivo, resultado_em_tres_paginas
):
    arquivos = ["/tmp/arq1", "/tmp/arq2", "/tmp/arq3"]
    stub_ler_arquivo.side_effect = resultado_em_tres_paginas
    fake_db = FakeDB()
    qtd = registrar_livros(arquivos, fake_db.inserir_registros)
    assert qtd == 8
    assert fake_db._registros[0] == {
        "author": "Luciano Ramalho",
        "title": "Python Fluente",
    }


@patch("colecao.livros.ler_arquivo")
def test_registrar_livros_insere_5_registros(
    stub_ler_arquivo, resultado_em_duas_paginas
):
    stub_ler_arquivo.side_effect = resultado_em_duas_paginas
    arquivos = ["/tmp/arq1", "/tmp/arq2"]

    fake_db = MagicMock()
    fake_db.inserir_registros = fake_inserir_registros
    qtd = registrar_livros(arquivos, fake_db.inserir_registros)
    assert qtd == 5
