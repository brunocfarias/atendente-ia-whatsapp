from chat_terminal import formatar_whatsapp


def test_converte_negrito_markdown_para_whatsapp():
    assert formatar_whatsapp("Seu **Corte** às **11:00**") == "Seu *Corte* às *11:00*"