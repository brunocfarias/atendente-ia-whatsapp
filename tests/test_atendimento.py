import db
from atendimento import contem_palavra_sensivel, transferir_para_humano


def test_transferencia_grava_no_banco_e_devolve_protocolo():
    resultado = transferir_para_humano("Bruno", "Reclamação", "Degradê ficou torto.")
    assert resultado["transferido"] is True
    assert len(db.escalacoes_abertas()) == 1


def test_detecta_palavra_sensivel_com_acento_e_maiuscula():
    assert contem_palavra_sensivel("Quero meu REEMBOLSO agora")
    assert contem_palavra_sensivel("Teve uma cobrança indevida no meu cartão")


def test_nao_dispara_em_mensagem_normal():
    assert not contem_palavra_sensivel("Como é o processo pra agendar?")
    assert not contem_palavra_sensivel("Quero cortar o cabelo sábado")