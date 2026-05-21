# envio de e-mail de alerta usando Resend
import resend
import os
from dotenv import load_dotenv
from modules.configuracoes import get_email_destinatario

load_dotenv()


def enviar_email_alerta(produto_nome, quantidade_atual, quantidade_minima):
    api_key      = os.getenv('RESEND_API_KEY')
    destinatario = get_email_destinatario()

    if not api_key or not destinatario:
        print("RESEND_API_KEY ou EMAIL_DESTINATARIO nao configurados")
        return False

    resend.api_key = api_key

    corpo = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #c62828;">Alerta de Estoque Baixo</h2>
        <p>O produto abaixo atingiu o estoque minimo:</p>
        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse:collapse;">
            <tr style="background:#2c5f8a; color:white;">
                <th>Produto</th><th>Quantidade Atual</th><th>Estoque Minimo</th>
            </tr>
            <tr>
                <td>{produto_nome}</td>
                <td style="color:red; font-weight:bold;">{quantidade_atual}</td>
                <td>{quantidade_minima}</td>
            </tr>
        </table>
        <p>Providencie a reposicao do estoque.</p>
    </body></html>
    """

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [destinatario],
            "subject": f"Estoque Baixo - {produto_nome}",
            "html": corpo
        })
        print(f"E-mail enviado para {destinatario}")
        return True

    except Exception as erro:
        print(f"Erro ao enviar e-mail: {erro}")
        return False


def verificar_e_notificar(produto):
    if produto['quantidade'] <= produto['estoque_minimo']:
        return enviar_email_alerta(produto['nome'], produto['quantidade'], produto['estoque_minimo'])
    return False
