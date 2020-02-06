import pytest
from unittest.mock import (
    patch,
    mock_open,
    Mock,
)

from unittest import skip
from colecao.livros import (
    consultar_livros,
    executar_requisicao,
)
from urllib.error import HTTPError


@skip("Vale quando consultar_livros estiver completo")
def test_consultar_livros_retorna_resultado_formato_string():
    resultado = consultar_livros("Agatha Christie")
    assert type(resultado) == str


@skip
def test_consultar_livros_chama_preparar_dados_para_requisicao_uma_vez_e_com_os_mesmos_parametros_de_consultar_livros():
    with patch("colecao.livros.preparar_dados_para_requisicao") as duble:
        consultar_livros("Agatha Christie")
        duble.assert_called_once_with("Agatha Christie")


@skip
def test_consultar_livros_chama_obter_url_usando_como_parametro_o_retorno_de_preparar_dados_para_requisicao():
    with patch("colecao.livros.preparar_dados_para_requisicao") as duble_preparar:
        dados = {"author": "Agatha Christie"}
        duble_preparar.return_value = dados
        with patch("colecao.livros.obter_url") as duble_obter_url:
            consultar_livros("Agatha Christie")
            duble_obter_url.assert_called_once_with("https://buscador", dados)


@skip
def test_consultar_livros_chama_executar_requisicao_usando_retorno_obter_url():
    with patch("colecao.livros.obter_url") as duble_obter_url:
        duble_obter_url.return_value = "https://buscador"
        with patch("colecao.livros.executar_requisicao") as duble_executar_requisicao:
            consultar_livros("Agatha Christie")
            duble_executar_requisicao.assert_called_once_with("https://buscador")


class StubHTTPResponse:
    def read(self):
        return b""

    def __enter__(self):
        return self

    def __exit__(self, param1, param2, param3):
        pass


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
