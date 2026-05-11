# envio de e-mail de alerta usando smtplib (biblioteca nativa do Python)
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def enviar_email_alerta(produto_nome, quantidade_atual, quantidade_minima):
    # le as credenciais do arquivo .env
    remetente    = os.getenv('EMAIL_REMETENTE')
    senha        = os.getenv('EMAIL_SENHA_APP')
    destinatario = os.getenv('EMAIL_DESTINATARIO')

    # se nao tiver configurado, nao tenta enviar
    if not remetente or not senha or not destinatario:
        print("Credenciais de e-mail nao configuradas no .env")
        return False

    # monta o e-mail
    mensagem = MIMEMultipart('alternative')
    mensagem['From']    = remetente
    mensagem['To']      = destinatario
    mensagem['Subject'] = f'Estoque Baixo - {produto_nome}'

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

    mensagem.attach(MIMEText(corpo, 'html', 'utf-8'))

    # conecta no servidor do Gmail e envia
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatario, mensagem.as_string())
        servidor.quit()
        print(f"E-mail enviado para {destinatario}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Erro de autenticacao: verifique EMAIL_REMETENTE e EMAIL_SENHA_APP")
        return False

    except Exception as erro:
        print(f"Erro ao enviar e-mail: {erro}")
        return False


def verificar_e_notificar(produto):
    # envia alerta se o produto estiver abaixo do minimo
    if produto['quantidade'] <= produto['estoque_minimo']:
        return enviar_email_alerta(produto['nome'], produto['quantidade'], produto['estoque_minimo'])
    return False
