# ============================================================
# Módulo: notificacao.py
# Responsabilidade: Envio de e-mail de alerta via smtplib
# ============================================================
# Utiliza apenas bibliotecas nativas do Python (smtplib, email)
# Credenciais lidas de variáveis de ambiente (.env)
# ============================================================

import smtplib                              # Biblioteca nativa para envio de e-mail
import os                                   # Para ler variáveis de ambiente
from email.mime.text import MIMEText        # Formata o corpo do e-mail
from email.mime.multipart import MIMEMultipart  # Permite e-mail com HTML
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


def enviar_email_alerta(produto_nome, quantidade_atual, quantidade_minima):
    """
    Envia um e-mail de alerta quando um produto atinge o estoque mínimo.

    Parâmetros:
        produto_nome     (str): Nome do produto com estoque baixo
        quantidade_atual (int): Quantidade atual em estoque
        quantidade_minima(int): Quantidade mínima configurada

    Retorna:
        True  se o e-mail foi enviado com sucesso
        False se houve algum erro ou credenciais não configuradas
    """
    # Lê as credenciais de e-mail das variáveis de ambiente
    email_remetente    = os.getenv('EMAIL_REMETENTE')
    senha_app          = os.getenv('EMAIL_SENHA_APP')
    email_destinatario = os.getenv('EMAIL_DESTINATARIO')

    # Verifica se as credenciais estão configuradas no .env
    # Estrutura condicional (if) para validação
    if not email_remetente or not senha_app or not email_destinatario:
        print("AVISO: Credenciais de e-mail não configuradas no arquivo .env")
        return False

    # --- Monta a mensagem de e-mail ---

    # Cria o objeto de mensagem com suporte a múltiplas partes
    mensagem = MIMEMultipart('alternative')
    mensagem['From']    = email_remetente
    mensagem['To']      = email_destinatario
    mensagem['Subject'] = f'ALERTA: Estoque Baixo - {produto_nome}'

    # Corpo do e-mail em formato HTML para melhor visualização
    corpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">

        <h2 style="color: #c0392b;">⚠️ Alerta de Estoque Baixo</h2>
        <p>O produto abaixo atingiu o estoque mínimo na cantina escolar:</p>

        <table border="1" cellpadding="12" cellspacing="0"
               style="border-collapse: collapse; width: 100%; max-width: 500px;">
            <thead style="background-color: #2c5f8a; color: white;">
                <tr>
                    <th>Produto</th>
                    <th>Qtd. Atual</th>
                    <th>Estoque Mínimo</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>{produto_nome}</strong></td>
                    <td style="color: red; font-weight: bold; text-align: center;">
                        {quantidade_atual}
                    </td>
                    <td style="text-align: center;">{quantidade_minima}</td>
                </tr>
            </tbody>
        </table>

        <br>
        <p style="color: #c0392b;">
            <strong>Ação necessária:</strong> Providencie a reposição do estoque.
        </p>
        <hr>
        <p style="color: #888; font-size: 12px;">
            Sistema de Controle de Estoque - Cantina Escolar<br>
            Mensagem gerada automaticamente pelo sistema.
        </p>

    </body>
    </html>
    """

    # Adiciona o corpo HTML à mensagem
    mensagem.attach(MIMEText(corpo_html, 'html', 'utf-8'))

    # --- Envia o e-mail via servidor SMTP do Gmail ---
    try:
        # Conecta ao servidor SMTP do Gmail na porta 587 (protocolo TLS)
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.ehlo()          # Identifica o cliente ao servidor
        servidor.starttls()      # Inicia a criptografia TLS
        servidor.login(email_remetente, senha_app)  # Autentica com senha de app

        # Envia a mensagem
        servidor.sendmail(
            from_addr=email_remetente,
            to_addrs=email_destinatario,
            msg=mensagem.as_string()
        )

        servidor.quit()  # Encerra a conexão com o servidor

        print(f"E-mail de alerta enviado com sucesso para {email_destinatario}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("ERRO: Falha de autenticação. Verifique EMAIL_REMETENTE e EMAIL_SENHA_APP no .env")
        return False

    except Exception as erro:
        print(f"ERRO ao enviar e-mail: {erro}")
        return False


def verificar_e_notificar(produto):
    """
    Verifica se um produto está com estoque baixo e,
    se estiver, envia o e-mail de alerta automaticamente.

    Parâmetro:
        produto (dict): Dicionário com os dados do produto

    Retorna:
        True se notificação foi enviada, False caso contrário
    """
    # Estrutura condicional (if) para verificar estoque mínimo
    if produto['quantidade'] <= produto['estoque_minimo']:
        # Produto abaixo do mínimo: envia o alerta por e-mail
        resultado = enviar_email_alerta(
            produto_nome=produto['nome'],
            quantidade_atual=produto['quantidade'],
            quantidade_minima=produto['estoque_minimo']
        )
        return resultado

    # Estoque ainda está OK, nenhuma notificação necessária
    return False
